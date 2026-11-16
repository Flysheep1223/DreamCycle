"""Build an offline side-by-side original-vs-revised prompt comparison report."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    "ood_macro_watch": "微距琥珀腕表",
    "ood_gongbi_blueprint": "工笔蓝图荷塘",
    "ood_greenhouse_dashboard": "中文温室看板",
    "ood_woodcut_arctic": "木刻北极考察站",
    "ood_style_snow_egret": "雪景风格迁移",
    "ood_edit_watch_background": "腕表背景替换",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return esc(value)


def delta(a: object, b: object) -> str:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return "—"
    value = b - a
    return f"{value:+.3f}".rstrip("0").rstrip(".")


def row(label: str, a: object, b: object) -> str:
    return f"<tr><td>{esc(label)}</td><td>{fmt(a)}</td><td>{fmt(b)}</td><td>{delta(a, b)}</td></tr>"


def image(path: str, alt: str) -> str:
    return f'<a href="{esc(path)}" target="_blank" rel="noopener"><img src="{esc(path)}" alt="{esc(alt)}" loading="lazy"></a>'


def metrics_table(original: dict, revised: dict) -> str:
    ocr_a = original.get("ocr") or {}
    ocr_b = revised.get("ocr") or {}
    ref_a = original.get("reference") or {}
    ref_b = revised.get("reference") or {}
    rows = [
        row("动态 VQA", original.get("task_score"), revised.get("task_score")),
        row(
            "保持检查项均值", original.get("preservation_score"), revised.get("preservation_score")
        ),
        row("PQ / 10", original.get("perceptual_quality"), revised.get("perceptual_quality")),
        row("OCR Accuracy", ocr_a.get("accuracy"), ocr_b.get("accuracy")),
        row("OCR F1", ocr_a.get("f1"), ocr_b.get("f1")),
        row("文字布局分", original.get("text_layout_score"), revised.get("text_layout_score")),
        row("CP", ref_a.get("cp"), ref_b.get("cp")),
        row("PF", ref_a.get("pf"), ref_b.get("pf")),
        row(
            "全项通过率",
            original.get("full_requirement_rate"),
            revised.get("full_requirement_rate"),
        ),
        row(
            "最低检查项",
            original.get("minimum_requirement_score"),
            revised.get("minimum_requirement_score"),
        ),
    ]
    return (
        "<table><thead><tr><th>分离指标</th><th>A 原 Prompt</th><th>B 修改 Prompt</th><th>B-A</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def card(comparison: dict) -> str:
    case = comparison["case"]
    original = comparison["original"]
    if "error" in comparison:
        return f'<article class="case-card"><h2>{esc(TITLES.get(case, case))}</h2><p class="error">B组生成失败：{esc(comparison["error"])}</p><details><summary>A组原图</summary>{image(original["image"], case)}</details></article>'
    revised_result = comparison["revised"]["evaluations"][0]
    revised_metrics = revised_result["metrics"]
    advice = comparison.get("advisor_raw", {}).get("evaluation_audit", {})
    failures_a = original["metrics"].get("failure_tags") or original.get("failure_tags") or []
    failures_b = revised_metrics.get("failure_tags") or []
    return f"""
    <article class="case-card"><h2>{esc(TITLES.get(case, case))}</h2>
      <div class="image-pair">
        <section><h3>A · 原 Prompt</h3>{image(original["image"], case + "原Prompt")}</section>
        <section><h3>B · 修改 Prompt</h3>{image(revised_result["image"]["path"], case + "修改Prompt")}</section>
      </div>
      {metrics_table(original["metrics"], revised_metrics)}
      <div class="two-col"><details><summary>A 原始 Prompt</summary><pre>{esc(original["prompt"])}</pre></details>
      <details><summary>B 独立改写 Prompt</summary><pre>{esc(comparison["revised_prompt"])}</pre></details></div>
      <div class="two-col"><section><h4>A 失败标签</h4><p>{esc("；".join(failures_a) or "无")}</p></section>
      <section><h4>B 失败标签</h4><p>{esc("；".join(failures_b) or "无")}</p></section></div>
      <details><summary>对当前评估的意见（独立审计）</summary><p>{esc(advice.get("overall_assessment", ""))}</p>
      <h4>可能的评审误判</h4><ul>{"".join(f"<li>{esc(x)}</li>" for x in advice.get("possible_judge_errors", []))}</ul></details>
    </article>"""


def build() -> str:
    directory = max((ROOT / "runs").glob("prompt-ab-showcase-*"), key=lambda path: path.name)
    summary = json.loads((directory / "summary.json").read_text())
    fixed_path = directory / "fixed_summary.json"
    if fixed_path.exists():
        fixed = json.loads(fixed_path.read_text())
        by_case = {item["case"]: item for item in fixed["comparisons"]}
        for item in summary["comparisons"]:
            fixed_item = by_case.get(item["case"], {})
            if "fixed_original_metrics" in fixed_item:
                item["original"]["metrics"] = fixed_item["fixed_original_metrics"]
                item["revised"]["evaluations"][0]["metrics"] = fixed_item["fixed_revised_metrics"]
        summary["fixed_standard"] = True
    cards = "\n".join(card(item) for item in summary["comparisons"])
    standard_note = (
        "A、B两组图片均使用A原始Prompt生成的同一套检查清单重新评分，确保动态VQA标准一致。"
        if summary.get("fixed_standard")
        else "A使用原Prompt检查清单，B使用修改Prompt检查清单，动态VQA标准可能不同。"
    )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>原 Prompt vs 修改 Prompt A/B 对比</title><style>
:root{{--bg:#f5f7fb;--surface:#fff;--ink:#172033;--muted:#657087;--line:#dfe5ef;--blue:#256abf;--soft:#eaf3fe}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}}header{{background:#102a4c;color:#fff;padding:34px 24px}}.wrap{{max-width:1420px;margin:auto;padding:0 22px}}h1{{margin:0 0 8px}}header p{{color:#d5e2f4}}.case-card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;margin:22px 0;box-shadow:0 8px 26px #17203310}}.image-pair,.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.image-pair img{{width:100%;max-height:520px;object-fit:contain;background:#0e1420;border-radius:10px}}h2{{margin-top:0}}table{{width:100%;border-collapse:collapse;margin:18px 0}}td,th{{padding:9px;border-bottom:1px solid var(--line);text-align:left}}td:nth-child(2),td:nth-child(3),td:nth-child(4),th:nth-child(2),th:nth-child(3),th:nth-child(4){{text-align:right}}pre{{white-space:pre-wrap;word-break:break-word;background:#f4f6fa;padding:12px;border-radius:8px;max-height:420px;overflow:auto;font:12px/1.65 ui-monospace,monospace}}details{{margin:12px 0}}summary{{cursor:pointer;color:var(--blue);font-weight:650}}.note{{background:var(--soft);border-left:3px solid var(--blue);padding:12px 16px;margin:18px 0}}.error{{color:#a33}}@media(max-width:800px){{.image-pair,.two-col{{grid-template-columns:1fr}}}}
</style></head><body><header><div class="wrap"><h1>原 Prompt vs 修改 Prompt · A/B 实际生成对比</h1><p>A 为上次保留结果，B 为独立 Advisor 改写后重新生成。只比较分离指标，不计算总分。</p><p>{esc(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} · 同一输入图、模型与尺寸；当前版本未固定 seed，差异包含随机生成波动。</p></div></header><main class="wrap"><div class="note">{esc(standard_note)} B-A 只表示本次两次生成的数值差，不代表 Prompt 的稳定因果收益。请同时比较图像、失败标签和逐项理由。</div>{cards}</main></body></html>"""


if __name__ == "__main__":
    output = ROOT / "compare.html"
    output.write_text(build(), encoding="utf-8")
    print(output)
