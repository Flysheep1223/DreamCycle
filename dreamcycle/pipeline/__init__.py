r"""# pipeline 模块

实时编排分两段并行：

1. **生成期间**：Router 与 Seedream 同时执行；
2. **生成之后**：每张图的 VLM 评审与 OCR 同时执行。

`DREAMER_WORKERS` 通过 semaphore 限制批量请求并发。每次运行保存：

```text
request.json / generation.json / route.json / generated-00.png
judge-00.json / score-00.json / result.json
```

已有图片可用 `generated_image=` 跳过生成，单独做效果评价。"""

from .service import EvaluationPipeline

__all__ = ["EvaluationPipeline"]
