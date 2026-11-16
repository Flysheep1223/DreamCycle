r"""# config 模块

从项目根目录 `.env` 读取配置，调用方通过 `get_settings()` 获取单例。

- 不在日志和 `repr` 中输出 `ARK_API_KEY`。
- `public_dict()` 只返回模型、并发数、输出目录和“key 是否已配置”。
- `DREAMER_WORKERS` 控制批量请求并发。
- 默认输出目录为 `EVA/runs/`，可用 `EVA_RUNS_DIR` 覆盖。"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
