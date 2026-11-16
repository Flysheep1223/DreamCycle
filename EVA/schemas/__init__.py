r"""# schemas 模块

所有跨模块数据都用 Pydantic 模型传递：

- `RouteDecision`：多标签路由和动态检查清单；
- `JudgeResult`：通用对齐、PQ、编辑与参考图评分；
- `OCRScore`：Accuracy、NED、CER、Precision/Recall/F1；
- `EvaluationResult`：分离指标、逐项检查、原始证据与评审建议。

这样路由、API、CLI 和测试不会各自发明一套字段。"""

from .models import (
    AdviceReport,
    CheckItem,
    EditScore,
    EvaluationResult,
    GeneratedImage,
    JudgeCheckResult,
    JudgeResult,
    OCRScore,
    PipelineResult,
    ReferenceScore,
    RouteDecision,
    TaskMode,
)

__all__ = [
    "AdviceReport",
    "CheckItem",
    "EditScore",
    "EvaluationResult",
    "GeneratedImage",
    "JudgeCheckResult",
    "JudgeResult",
    "OCRScore",
    "PipelineResult",
    "ReferenceScore",
    "RouteDecision",
    "TaskMode",
]
