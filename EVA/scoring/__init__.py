r"""# scoring 模块

`ScoreReporter` 只负责整理**分离指标**，不再做跨指标归一化、权重或总分计算。

输出示例：

```json
{
  "task_score": 0.875,
  "preservation_score": 1.0,
  "text_layout_score": 1.0,
  "perceptual_quality": 8.0,
  "edit": {"sc": 8.0, "pq": 8.0, "overall": 8.0},
  "reference": {"cp": 4.0, "pf": 3.0},
  "ocr": {"accuracy": 1.0, "ned": 1.0, "cer": 0.0, "f1": 1.0},
  "checks": [],
  "full_requirement_rate": 0.9048,
  "minimum_requirement_score": 0.0
}
```

各指标保留原始尺度：

- `task_score` 显示名为“动态 VQA”，只是当前 Prompt 的任务检查项均值，不是官方 VQAScore，也不是跨指标总分；
- `preservation_score` 只是保持类检查项均值，与任务分独立；

- Task/Preservation：0–1；
- PQ：0–10；
- 编辑 SC/PQ/Overall：0–10，Overall 只是编辑内部的 `sqrt(SC×PQ)`，不是全任务总分；
- CP/PF：0–4；
- OCR Accuracy/NED/CER/F1：各自定义，不合成文字总分；
- `full_requirement_rate` 和 `minimum_requirement_score` 仅是检查项统计。

`raw_scores` 同时保留 VLM、OCR、输入警告等原始证据。旧的 `normalize.py` 仅作为兼容入口，不再包含总分算法。"""

from .report import ScoreReporter

__all__ = ["ScoreReporter"]
