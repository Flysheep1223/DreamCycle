"""Build an offline A/B/C/D/E iterative prompt comparison report."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["A", "B", "C", "D", "E"]
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


def metric_row(label: str, stages: dict, key: str, nested: str | None = None) -> str:
    values = []
    for name in STAGES:
        metrics = stages.get(name, {}).get("metrics")
        if not metrics:
            values.append("—")
            continue
        source = metrics.get(nested) if nested else metrics
        values.append(fmt(source.get(key)) if isinstance(source, dict) else "—")
    return f"<tr><td>{esc(label)}</td><td>" + "</td><td>".join(values) + "</td></tr>"


def prompt_length_row(stages: dict) -> str:
    values = [str(len(stages[stage]["prompt"])) if stage in stages else "—" for stage in STAGES]
    return "<tr><td>Prompt 字符数</td><td>" + "</td><td>".join(values) + "</td></tr>"


def case_card(case: dict) -> str:
    name = case["case"]
    stages = case["stages"]
    images = []
    for stage in STAGES:
        if stage not in stages:
            continue
        item = stages[stage]
        images.append(
            f'<section><h3>{stage}</h3><a href="{esc(item["image"])}" target="_blank" rel="noopener">'
            f'<img src="{esc(item["image"])}" alt="{name}{stage}" loading="lazy"></a></section>'
        )
    metrics = "".join(
        [
            metric_row("动态 VQA", stages, "task_score"),
            metric_row("保持检查项均值", stages, "preservation_score"),
            metric_row("PQ / 10", stages, "perceptual_quality"),
            metric_row("OCR Accuracy", stages, "accuracy", "ocr"),
            metric_row("OCR F1", stages, "f1", "ocr"),
            metric_row("文字布局分", stages, "text_layout_score"),
            metric_row("CP", stages, "cp", "reference"),
            metric_row("PF", stages, "pf", "reference"),
            metric_row("全项通过率", stages, "full_requirement_rate"),
            metric_row("最低检查项", stages, "minimum_requirement_score"),
            prompt_length_row(stages),
        ]
    )
    prompt_details = []
    for stage in STAGES:
        if stage not in stages:
            continue
        item = stages[stage]
        audit = item.get("advisor_raw", {}).get("evaluation_audit", {})
        audit_text = audit.get("overall_assessment", "")
        prompt_details.append(
            f"<details><summary>{stage} Prompt / 评估意见</summary><pre>{esc(item['prompt'])}</pre>"
            + (f"<p><strong>评估意见：</strong>{esc(audit_text)}</p>" if audit_text else "")
            + "</details>"
        )
    failures = []
    for stage in STAGES:
        if stage not in stages:
            continue
        tags = stages[stage]["metrics"].get("failure_tags") or []
        failures.append(f"<tr><td>{stage}</td><td>{esc('；'.join(tags) or '无')}</td></tr>")
    errors = "".join(
        f'<p class="error">{esc(str(error["stage"]) + ": " + error["error"])}</p>'
        for error in case.get("errors", [])
    )
    recoveries = "".join(
        f'<p class="note">{esc(str(item["stage"]))} 第 {esc(item["attempt"])} 次生成成功；首次接口错误保留在 summary.json。</p>'
        for item in case.get("recoveries", [])
    )
    return f"""
    <article class="case-card"><h2>{esc(TITLES.get(name, name))}</h2>
      <div class="image-grid">{"".join(images)}</div>
      <table><thead><tr><th>分离指标</th>{"".join(f"<th>{stage}</th>" for stage in STAGES)}</tr></thead><tbody>{metrics}</tbody></table>
      <h3>失败标签（VLM 返回）</h3><table><tbody>{"".join(failures)}</tbody></table>
      {"".join(prompt_details)}{recoveries}{errors}
    </article>"""


def build() -> str:
    directory = max((ROOT / "runs").glob("prompt-iterations-*"), key=lambda path: path.name)
    summary = json.loads((directory / "summary.json").read_text())
    cards = "\n".join(case_card(case) for case in summary["cases"])
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A/B/C/D/E 连续 Prompt 改写对比</title><style>
:root{{--bg:#f5f7fb;--surface:#fff;--ink:#172033;--line:#dfe5ef;--blue:#256abf;--soft:#eaf3fe}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}}header{{background:#102a4c;color:#fff;padding:32px 24px}}.wrap{{max-width:1600px;margin:auto;padding:0 20px}}h1{{margin:0 0 8px}}header p{{color:#d5e2f4}}.case-card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;margin:22px 0;box-shadow:0 8px 26px #17203310}}.image-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}}.image-grid img{{width:100%;height:260px;object-fit:contain;background:#0e1420;border-radius:8px}}table{{width:100%;border-collapse:collapse;margin:16px 0}}td,th{{padding:8px;border-bottom:1px solid var(--line);text-align:right}}td:first-child,th:first-child{{text-align:left}}pre{{white-space:pre-wrap;word-break:break-word;background:#f4f6fa;padding:12px;border-radius:8px;max-height:360px;overflow:auto;font:12px/1.6 ui-monospace,monospace}}details{{margin:10px 0}}summary{{cursor:pointer;color:var(--blue);font-weight:650}}.note{{background:var(--soft);border-left:3px solid var(--blue);padding:12px 16px;margin:18px 0}}.error{{color:#a33}}@media(max-width:1050px){{.image-grid{{grid-template-columns:repeat(2,1fr)}}table{{font-size:12px}}}}@media(max-width:560px){{.image-grid{{grid-template-columns:1fr}}}}
</style></head><body><header><div class="wrap"><h1>A/B/C/D/E 连续 Prompt 改写对比</h1><p>A 原始 Prompt，B-E 以原始需求为锚点进行有限局部改写；五组统一使用 A 原始检查清单评分。</p><p>{esc(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} · VLM temperature=0 · 生图未固定 seed · 不计算总分</p><p>{esc(summary["run_id"])} · {esc(summary.get("revision_policy", "legacy_cumulative_revision"))}</p></div></header><main class="wrap"><div class="note">Prompt 改写只看原始需求、当前草稿和图像，不读取评分或审计意见。每轮最多等义澄清两处已有歧义，不新增可检查条件并限制长度；若连续两次超长则回退原始需求。请分别比较动态 VQA、PQ、保持度、OCR、CP/PF 和检查统计。</div>{cards}</main></body></html>"""


if __name__ == "__main__":
    output = ROOT / "iterations.html"
    output.write_text(build(), encoding="utf-8")
    print(output)
