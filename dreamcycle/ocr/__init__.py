r"""# ocr 模块

使用 `rapidocr-onnxruntime` 做文字检测与识别，原始结果按从上到下、从左到右排序。

`metrics.py` 与 OCR 引擎解耦，可独立测试：

- Accuracy：目标字符串完全正确率；
- NED：`1 - 编辑距离 / max(预测长度,目标长度)`；
- CER：总编辑距离 / 总目标字符数；
- F1：一对一 exact match，额外 OCR 行计 FP，漏目标计 FN。

多行拼接匹配和官方特定 benchmark 的区域 IoU 规则不在当前实时 MVP 中，因此这些分数是**在线 OCR 协议**，不能冒充某个官方榜单分。目标与 OCR 行使用一对一分配，同一 OCR 行不能被多个目标重复利用；共享 ONNX 引擎的初始化和推理由锁保护。"""

from .metrics import levenshtein, normalize_text, score_texts
from .plugin import OCRPlugin

__all__ = ["OCRPlugin", "levenshtein", "normalize_text", "score_texts"]
