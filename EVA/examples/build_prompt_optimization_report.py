"""Build an offline report for guarded, fixed-parameter A-E optimization."""

from __future__ import annotations

import html
import json
from itertools import pairwise
from pathlib import Path

from PIL import Image

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
AUDIT_NOTES = {
    "ood_macro_watch": (
        "人工抽查疑点：B 的 t10“独立螺丝恰好三颗”获满分，但顶部仍有疑似带槽螺丝；"
        "B Prompt 还将“表背刻字”改为“表壳可见刻字”。该机评提升不能视为计数与位置均无误判。"
    )
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return esc(value)


def check_drop_count(before: dict, after: dict) -> int:
    before_checks = {item["id"]: item["score"] for item in before["metrics"].get("checks", [])}
    after_checks = {item["id"]: item["score"] for item in after["metrics"].get("checks", [])}
    return sum(
        after_checks[check_id] < before_checks[check_id]
        for check_id in before_checks.keys() & after_checks.keys()
    )


def values_row(label: str, values: list[object]) -> str:
    return (
        f"<tr><td>{esc(label)}</td><td>" + "</td><td>".join(fmt(v) for v in values) + "</td></tr>"
    )


def metric_row(stages: dict, label: str, key: str, nested: str | None = None) -> str:
    values = []
    for stage in STAGES:
        metrics = stages[stage]["metrics"]
        source = metrics.get(nested) if nested else metrics
        values.append(source.get(key) if isinstance(source, dict) else None)
    return values_row(label, values)


def acceptance_text(stage: dict, name: str) -> str:
    if name == "A":
        return "单样本起点"
    if stage.get("accepted"):
        source = {"incumbent": "继承最佳Prompt", "revised": "改写Prompt"}.get(
            stage.get("accepted_prompt_source"), "改写Prompt"
        )
        return f"接受 slot {stage['generation']['candidate_slot']} · {source}"
    return f"平台期，继承 {stage['source_stage']}"


def candidate_details(stage_name: str, stage: dict) -> str:
    if (
        not stage.get("candidates")
        and not stage.get("generation_errors")
        and not stage.get("stage_error")
    ):
        return ""
    rows = []
    for candidate in stage.get("candidates", []):
        metrics = candidate["metrics"]
        decision = candidate["selection"]
        outcome = []
        if candidate.get("selected"):
            outcome.append("本轮胜者")
        elif decision["accepted"]:
            outcome.append("合格但未选中")
        if decision["improved"]:
            outcome.append("改善：" + "、".join(decision["improved"]))
        if decision["degraded"]:
            outcome.append("退化：" + "、".join(decision["degraded"]))
        if not outcome:
            outcome.append("无指标改善")
        ocr = metrics.get("ocr") or {}
        prompt_source = {"incumbent": "继承最佳", "revised": "改写"}.get(
            candidate.get("prompt_source"), "改写"
        )
        rows.append(
            "<tr>"
            f"<td>{candidate['generation']['candidate_slot']}</td>"
            f"<td>{prompt_source}</td>"
            f"<td>{candidate['generation']['seed']}</td>"
            f"<td>{fmt(metrics.get('task_score'))}</td>"
            f"<td>{fmt(metrics.get('perceptual_quality'))}</td>"
            f"<td>{fmt(metrics.get('preservation_score'))}</td>"
            f"<td>{fmt(ocr.get('accuracy'))}</td>"
            f"<td>{fmt(metrics.get('full_requirement_rate'))}</td>"
            f"<td>{fmt(metrics.get('minimum_requirement_score'))}</td>"
            f'<td>{esc("；".join(outcome))}<br><a href="{esc(candidate["image"])}" target="_blank">候选图片</a></td>'
            "</tr>"
        )
    errors = "".join(
        f'<p class="error">slot {esc(item["generation"]["candidate_slot"])}：{esc(item["error"])}</p>'
        for item in stage.get("generation_errors", [])
    )
    recoveries = "".join(
        f'<p class="note">slot seed {esc(item["seed"])} 网络错误后第 {esc(item["attempt"])} 次生成成功，已重新参与验收。</p>'
        for item in stage.get("recoveries", [])
    )
    stage_error = (
        f'<p class="error">{esc(stage["stage_error"])}</p>' if stage.get("stage_error") else ""
    )
    prompt = stage.get("candidate_prompt")
    prompt_block = f"<pre>{esc(prompt)}</pre>" if prompt else ""
    return f"""<details><summary>{stage_name} 候选 Prompt、{len(rows)} 个候选及验收记录</summary>
      {prompt_block}{recoveries}{stage_error}{errors}
      <div class="scroll"><table><thead><tr><th>slot</th><th>Prompt来源</th><th>seed</th><th>动态VQA</th><th>PQ</th><th>保持</th><th>OCR Acc</th><th>全项率</th><th>最低项</th><th>验收原因</th></tr></thead>
      <tbody>{"".join(rows)}</tbody></table></div></details>"""


def case_card(case: dict) -> str:
    stages = case["stages"]
    if set(stages) != set(STAGES):
        return f'<article class="case-card"><h2>{esc(case["case"])}</h2><p class="error">阶段不完整</p></article>'
    images = []
    actual_sizes = []
    for name in STAGES:
        stage = stages[name]
        with Image.open(stage["image"]) as image:
            actual_sizes.append(f"{image.width}×{image.height}")
        images.append(
            f"<section><h3>{name} · {esc(acceptance_text(stage, name))}</h3>"
            f'<a href="{esc(stage["image"])}" target="_blank"><img src="{esc(stage["image"])}" loading="lazy"></a></section>'
        )
    rows = "".join(
        [
            values_row("验收状态", [acceptance_text(stages[s], s) for s in STAGES]),
            values_row("实际尺寸", actual_sizes),
            values_row("选中图片 seed", [stages[s]["generation"]["seed"] for s in STAGES]),
            metric_row(stages, "动态 VQA", "task_score"),
            metric_row(stages, "保持检查项均值", "preservation_score"),
            metric_row(stages, "PQ / 10", "perceptual_quality"),
            metric_row(stages, "OCR Accuracy", "accuracy", "ocr"),
            metric_row(stages, "OCR NED", "ned", "ocr"),
            metric_row(stages, "OCR CER ↓", "cer", "ocr"),
            metric_row(stages, "OCR F1", "f1", "ocr"),
            metric_row(stages, "文字布局分", "text_layout_score"),
            metric_row(stages, "编辑 SC", "sc", "edit"),
            metric_row(stages, "编辑 PQ", "pq", "edit"),
            metric_row(stages, "参考 CP", "cp", "reference"),
            metric_row(stages, "参考 PF", "pf", "reference"),
            metric_row(stages, "全项通过率", "full_requirement_rate"),
            metric_row(stages, "最低检查项", "minimum_requirement_score"),
            values_row(
                "逐项检查下降数",
                ["—"]
                + [
                    check_drop_count(stages[before], stages[after])
                    for before, after in pairwise(STAGES)
                ],
            ),
            values_row("最佳 Prompt 字符数", [len(stages[s]["prompt"]) for s in STAGES]),
        ]
    )
    delta = stages["E"]["metrics"]["task_score"] - stages["A"]["metrics"]["task_score"]
    fixed = case["fixed_generation"]
    audit_note = (
        f'<p class="note"><strong>人工抽查：</strong>{esc(AUDIT_NOTES[case["case"]])}</p>'
        if case["case"] in AUDIT_NOTES
        else ""
    )
    candidates = "".join(candidate_details(name, stages[name]) for name in STAGES[1:])
    best_prompts = "".join(
        f"<details><summary>{name} 当前最佳 Prompt</summary><pre>{esc(stages[name]['prompt'])}</pre></details>"
        for name in STAGES
    )
    return f"""<article class="case-card"><h2>{esc(TITLES.get(case["case"], case["case"]))}
      <span class="delta">动态 VQA A→E：{fmt(delta)}</span></h2>
      <p class="config">固定尺寸 {esc(fixed["size"])} · guidance_scale=端点不支持，未传 · 固定 seed 序列 {esc(fixed["seed_schedule"])} · PNG · watermark=false</p>
      {audit_note}
      <div class="image-grid">{"".join(images)}</div>
      <div class="scroll"><table><thead><tr><th>分离指标</th>{"".join(f"<th>{s}</th>" for s in STAGES)}</tr></thead><tbody>{rows}</tbody></table></div>
      {candidates}{best_prompts}</article>"""


def build() -> str:
    directory = max((ROOT / "runs").glob("prompt-optimization-*"), key=lambda path: path.name)
    summary = json.loads((directory / "summary.json").read_text())
    cards = "".join(case_card(case) for case in summary["cases"])
    accepted = sum(
        stage.get("accepted") is True
        for case in summary["cases"]
        for name, stage in case["stages"].items()
        if name != "A"
    )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A–E 固定参数最佳检查点优化</title><style>
:root{{--bg:#f4f7fb;--surface:#fff;--ink:#172033;--line:#dce4ef;--blue:#205fa8;--soft:#e9f2fc}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}}header{{background:#102a4c;color:white;padding:30px 24px}}.wrap{{max-width:1650px;margin:auto;padding:0 20px}}h1{{margin:0 0 8px}}header p{{color:#d7e4f5;max-width:1200px}}.case-card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;margin:22px 0;box-shadow:0 8px 25px #1720330d}}.image-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}}.image-grid h3{{font-size:12px;min-height:38px}}.image-grid img{{width:100%;height:255px;object-fit:contain;background:#101722;border-radius:8px}}table{{width:100%;border-collapse:collapse;margin:14px 0;white-space:nowrap}}td,th{{padding:8px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}td:first-child,th:first-child{{text-align:left}}td:last-child{{white-space:normal;min-width:220px;text-align:left}}.scroll{{overflow-x:auto}}pre{{white-space:pre-wrap;word-break:break-word;background:#f3f6fa;padding:12px;border-radius:8px;max-height:340px;overflow:auto;font:12px/1.6 ui-monospace,monospace}}details{{margin:10px 0}}summary{{cursor:pointer;color:var(--blue);font-weight:650}}.note{{background:var(--soft);border-left:3px solid var(--blue);padding:12px 16px;margin:18px 0}}.config{{color:#53647a}}.delta{{float:right;font-size:14px;color:var(--blue)}}.error{{color:#a33333}}@media(max-width:1050px){{.image-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:560px){{.image-grid{{grid-template-columns:1fr}}}}
</style></head><body><header><div class="wrap"><h1>A–E 固定参数最佳检查点优化</h1><p>{esc(summary["note"])}</p><p>{esc(summary["selection_rule"])}</p><p>{esc(summary["run_id"])} · VLM temperature={esc(summary["vlm"]["temperature"])} · 共接受 {accepted} 次候选改善 · 不计算总分</p></div></header>
<main class="wrap"><div class="note"><strong>实验口径：</strong>A 只有一个样本，B–E 每轮最多从 4 个固定 seed 候选中选一个，因此提升来自“Prompt 改写＋生成＋选优”整体，而不是单独证明 Prompt 的因果收益。平台期会重复最佳图片，不用更差图片继续。A 已为 1.0 时没有动态 VQA 上升空间。</div>{cards}</main></body></html>"""


if __name__ == "__main__":
    output = ROOT / "optimization.html"
    output.write_text(build(), encoding="utf-8")
    print(output)
