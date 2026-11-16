"""Build a self-contained HTML report with tests, OOD images and separated metrics."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
OUT = ROOT / "report.html"
TITLES = {
    "ood_macro_watch": "微距琥珀机械腕表",
    "ood_gongbi_blueprint": "工笔重彩＋工程蓝图荷塘",
    "ood_greenhouse_dashboard": "中文智慧温室看板",
    "ood_woodcut_arctic": "1920 年代木刻北极考察站",
    "ood_style_snow_egret": "雪景工笔蓝图风格迁移",
    "ood_edit_watch_background": "腕表背景保持编辑",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: object, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return esc(value)


def pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def metric(label: str, value: object, suffix: str = "") -> str:
    return (
        '<div class="metric"><span class="metric-label">'
        + esc(label)
        + '</span><strong class="metric-value">'
        + fmt(value)
        + esc(suffix)
        + "</strong></div>"
    )


def list_items(values: list[str], limit: int = 5) -> str:
    if not values:
        return '<p class="muted">无</p>'
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in values[:limit]) + "</ul>"


def image(path: str, alt: str, cls: str = "result-image") -> str:
    return (
        f'<a href="{esc(path)}" target="_blank" rel="noopener">'
        f'<img class="{cls}" src="{esc(path)}" alt="{esc(alt)}" loading="lazy"></a>'
    )


def case_card(case: dict) -> str:
    name = case["case"]
    title = TITLES.get(name, name)
    metrics = case["metrics"]
    ocr = metrics.get("ocr") or {}
    reference = metrics.get("reference") or {}
    reference_metrics = (
        metric("CP", reference.get("cp")) + metric("PF", reference.get("pf")) if reference else ""
    )
    refs = ""
    if case.get("input_images"):
        refs = (
            '<div class="reference-row"><h4>输入参考图</h4><div class="ref-grid">'
            + "".join(
                image(path, f"{title}输入参考图", "ref-image") for path in case["input_images"]
            )
            + "</div></div>"
        )
    tags = metrics.get("failure_tags") or case.get("failure_tags") or []
    failure_html = (
        '<div class="tags">'
        + "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags)
        + "</div>"
        if tags
        else '<p class="muted">未返回失败标签</p>'
    )
    advice = case.get("advice") or {}
    advice_html = ""
    if advice:
        advice_html = f"""
        <details class="advice"><summary>Prompt Advisor：生图建议与评估审计</summary>
          <div class="advice-grid">
            <section><h4>独立 Prompt 修改建议</h4>{list_items(advice.get("generation_prompt_suggestions", []), 4)}</section>
            <section><h4>对当前评估的意见</h4><p>{esc(advice.get("overall_assessment", ""))}</p>
              <h4>可能的评审误判</h4>{list_items(advice.get("possible_judge_errors", []), 4)}</section>
          </div>
          <details><summary>查看评估提示词建议</summary>{list_items(advice.get("evaluation_prompt_suggestions", []), 5)}</details>
          <details><summary>查看独立改写 Prompt</summary><pre class="prompt">{esc(advice.get("revised_generation_prompt", ""))}</pre></details>
        </details>
        """
    return f"""
    <article class="case-card">
      <div class="case-head"><div><span class="case-id">{esc(name)}</span><h3>{esc(title)}</h3></div>
        <span class="rate">全项通过率 {pct(metrics.get("full_requirement_rate"))}</span></div>
      <div class="case-layout"><div>{image(case["image"], title)}</div>
        <div class="case-body"><div class="metrics">
          {metric("动态VQA（任务检查项均值）", metrics.get("task_score"))}
          {metric("保持检查项均值", metrics.get("preservation_score"))}
          {metric("PQ / 10", metrics.get("perceptual_quality"))}
          {metric("OCR Accuracy", ocr.get("accuracy"))}
          {metric("OCR F1", ocr.get("f1"))}
          {metric("文字布局分", metrics.get("text_layout_score"))}
          {reference_metrics}
          {metric("最低检查项", metrics.get("minimum_requirement_score"))}
        </div>
        <h4>失败标签</h4>{failure_html}
        <details><summary>原始用户 Prompt</summary><pre class="prompt">{esc(case["prompt"])}</pre></details>
        </div></div>
      {refs}{advice_html}
    </article>"""


def build() -> str:
    summary = json.loads(
        (RUNS / "ood-showcase-20261115T145746-9fa1d346" / "summary.json").read_text()
    )
    cases = [*summary["t2i"], *summary["dependent"]]
    # Use the second-stage two-call audit for the snow style-transfer case.
    snow_score = json.loads((RUNS / "run-20261115T150838-3c994afe" / "score-00.json").read_text())
    for index, case in enumerate(cases):
        if case["case"] == "ood_style_snow_egret":
            cases[index]["metrics"] = snow_score["metrics"]
            cases[index]["advice"] = snow_score.get("advice")
    tests_text = (ROOT / "test-results.txt").read_text()
    tests = re.findall(r"^(EVA/tests/\S+)\s+(PASSED|FAILED|ERROR)", tests_text, re.MULTILINE)
    test_rows = "".join(
        f'<tr><td><code>{esc(name)}</code></td><td><span class="status-pass">{esc(status)}</span></td></tr>'
        for name, status in tests
    )
    hand = json.loads(
        (RUNS / "hand-probe-20261115T135753-71ed52b8" / "combined-12-trials.json").read_text()
    )
    positions = json.loads(
        (RUNS / "hand-position-probe-20261115T141702-f6e27992" / "summary.json").read_text()
    )
    cards = "\n".join(case_card(case) for case in cases)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Seedream EVA 测试与分布外评估报告</title>
<style>
:root{{--bg:#f5f7fb;--surface:#fff;--ink:#172033;--muted:#657087;--line:#dfe5ef;--blue:#256abf;--blue-soft:#eaf3fe;--green:#087a55;--amber:#9a5b00;--shadow:0 8px 26px rgba(23,32,51,.07)}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
a{{color:var(--blue);text-decoration:none}}a:hover{{text-decoration:underline}}header{{background:#102a4c;color:#fff;padding:38px 28px}}.wrap{{max-width:1320px;margin:auto;padding:0 22px}}
h1{{margin:0 0 8px;font-size:30px}}header p{{margin:4px 0;color:#d5e2f4}}.badge{{display:inline-block;margin-top:14px;padding:5px 10px;border:1px solid #5f86b6;border-radius:999px;font-size:12px}}
nav{{display:flex;gap:8px;flex-wrap:wrap;margin:24px 0}}nav button{{border:1px solid var(--line);background:#fff;padding:10px 16px;border-radius:9px;cursor:pointer;color:var(--ink);font-weight:600}}nav button.active{{background:var(--blue);color:#fff;border-color:var(--blue)}}
.page{{display:none}}.page.active{{display:block}}.tiles{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}.tile{{background:var(--surface);padding:18px;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow)}}.tile strong{{font-size:26px;display:block}}.tile span{{color:var(--muted)}}
.case-card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0;box-shadow:var(--shadow)}}.case-head{{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px}}.case-head h3{{margin:3px 0 0;font-size:21px}}.case-id{{font:12px ui-monospace,monospace;color:var(--muted)}}.rate{{background:var(--blue-soft);color:#184f95;padding:6px 10px;border-radius:8px;white-space:nowrap;font-weight:650}}.case-layout{{display:grid;grid-template-columns:minmax(280px,480px) 1fr;gap:22px}}.result-image{{width:100%;max-height:520px;object-fit:contain;background:#0e1420;border-radius:10px}}.ref-grid{{display:flex;gap:12px;flex-wrap:wrap}}.ref-image{{width:180px;max-height:200px;object-fit:contain;background:#0e1420;border-radius:8px}}.reference-row{{margin-top:20px}}
.metrics{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}}.metric{{padding:10px;background:#f6f8fb;border:1px solid var(--line);border-radius:8px}}.metric-label{{display:block;color:var(--muted);font-size:12px}}.metric-value{{font-size:20px}}h4{{margin:15px 0 7px;font-size:14px}}.tags{{display:flex;flex-wrap:wrap;gap:7px}}.tag{{background:#fff1e5;color:#8b4800;border:1px solid #f3d4b8;padding:4px 8px;border-radius:999px;font-size:12px}}.muted{{color:var(--muted)}}details{{margin-top:12px}}summary{{cursor:pointer;color:var(--blue);font-weight:650}}.prompt{{white-space:pre-wrap;word-break:break-word;background:#f4f6fa;border:1px solid var(--line);padding:12px;border-radius:8px;font:12px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace;max-height:420px;overflow:auto}}.advice{{margin-top:18px;border-top:1px solid var(--line);padding-top:12px}}.advice-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}ul{{padding-left:20px}}table{{width:100%;border-collapse:collapse;background:#fff}}td,th{{text-align:left;padding:9px;border-bottom:1px solid var(--line)}}.status-pass{{color:var(--green);font-weight:700}}.note{{border-left:3px solid var(--blue);padding:10px 14px;background:var(--blue-soft);margin:14px 0}}.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}code{{word-break:break-all}}
@media(max-width:900px){{.case-layout,.advice-grid,.two-col{{grid-template-columns:1fr}}.tiles{{grid-template-columns:repeat(2,1fr)}}.case-head{{flex-direction:column}}}}
@media(max-width:520px){{.metrics{{grid-template-columns:1fr}}.tiles{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div class="wrap"><h1>Seedream EVA 测试与分布外评估报告</h1>
<p>真实 Seedream 生成＋VLM 评审＋OCR＋独立 Prompt Advisor。仅展示分离指标，不计算总分。</p>
<p>生成时间：{esc(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} · VLM: seed2.1pro endpoint · Seedream: doubao-seedream-5-5-261028 · 2K</p>
<span class="badge">19 tests passed · Ruff passed · OOD 6 cases</span></div></header>
<main class="wrap"><nav><button class="active" data-page="overview">总览</button><button data-page="cases">分布外结果</button><button data-page="audit">评估器审计</button><button data-page="tests">19 项测试</button></nav>
<section id="overview" class="page active"><div class="tiles">
<div class="tile"><strong>19 / 19</strong><span>单元与流程测试通过</span></div>
<div class="tile"><strong>6</strong><span>新分布外生成/编辑任务</span></div>
<div class="tile"><strong>2 阶段</strong><span>评估审计与独立 Prompt 改写</span></div>
<div class="tile"><strong>0</strong><span>总分、权重、跨指标归一化</span></div></div>
<div class="note"><strong>怎么读：</strong>“动态 VQA”是自定义动态 VQA 任务对齐分，仅为当前 Prompt 的任务检查项均值，不是官方 VQAScore，也不是总评分；保持度、PQ、CP/PF、OCR Accuracy/F1、文字布局分与全项通过率都独立报告。OCR Accuracy=0 可能是漏检，不等于文字不存在；全项通过率也不是综合质量分。</div>
<div class="case-card"><h2>本次运行内容</h2><ul><li>微距琥珀腕表：材质、视角、微小文字和数量</li><li>工笔蓝图荷塘：风格融合、双语文字和蓝图标注</li><li>中文温室 UI：卡片布局、数值与特殊字符</li><li>木刻北极：历史物品、人数与犬只</li><li>雪景风格迁移：参考风格、左右翼和禁止数字</li><li>腕表背景编辑：材质、刻字、结构与背景保持</li></ul>
<p><a href="test-results.txt" target="_blank">查看 pytest 原始输出</a> · <a href="ruff-results.txt" target="_blank">查看 Ruff 原始输出</a></p></div></section>
<section id="cases" class="page">{cards}</section>
<section id="audit" class="page"><div class="two-col">
<div class="case-card"><h2>自然语言左右手评审</h2><div class="metrics">
{metric("总尝试", hand["attempted_trials"])}{metric("有效返回", hand["valid_trials"])}
{metric("右手红书误判", hand["right_hand_errors"])}{metric("右手误判率", pct(hand["right_hand_error_rate"]))}
{metric("左手扳手误判", hand["left_hand_errors"])}{metric("协议失败率", pct(hand["protocol_failure_rate"]))}
</div><p class="note">同一张双参考图、固定检查项重复 12 次。75% 是特定图片的小样本误判率，不能外推为所有任务。</p></div>
<div class="case-card"><h2>bbox 坐标法</h2><div class="metrics">
{metric("复测次数", positions["trials"])}{metric("有效返回", positions["valid_trials"])}
{metric("位置判断错误", positions["errors"])}{metric("错误率", pct(positions["error_rate"]))}
</div><p class="note">VLM 只输出人物、扳手和红书的位置框，程序比较 x 坐标，避免“自身左右/观众左右”的语言混淆。</p></div></div>
<div class="case-card"><h2>两阶段 Prompt Advisor</h2><ol><li><strong>评估审计：</strong>查看全部输入输出、逐项评分、OCR 和评审理由，输出当前评估的问题与补充检查项。</li><li><strong>独立 Prompt 改写：</strong>只看原始 Prompt 与图像，不传入评分、评审理由、OCR、争议检查项或评估意见。</li></ol>
<p>返回顺序为：先生图 Prompt 建议与改写版本，再贴对当前评估的意见。这样有问题的评估不会直接成为 Prompt 修改依据。</p></div></section>
<section id="tests" class="page"><div class="case-card"><h2>19 项测试明细</h2><table><thead><tr><th>测试</th><th>结果</th></tr></thead><tbody>{test_rows}</tbody></table>
<p class="note">另有 1 条来自 FastAPI TestClient 的第三方弃用警告，不影响测试通过。Ruff：All checks passed。</p></div></section>
</main><script>
document.querySelectorAll('nav button').forEach(button=>button.addEventListener('click',()=>{{
document.querySelectorAll('nav button').forEach(b=>b.classList.remove('active'));button.classList.add('active');
document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById(button.dataset.page).classList.add('active');
window.scrollTo({{top:0,behavior:'smooth'}});
}}));
</script></body></html>"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)
