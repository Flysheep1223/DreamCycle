r"""# ark 模块

只封装官方 `arkruntime` 的两类调用：

1. `chat.completions.create`：VLM 视觉输入 + `json_schema` 严格结构化输出；
2. `images.generate`：Seedream 文生图或带参考图生成。

同步 SDK 调用通过 `asyncio.to_thread` 执行，避免阻塞并行流水线。API key 仅通过 `Settings` 传给官方客户端，不进入结果 JSON。

官方接口依据：

- [Seedream 图片生成教程](https://www.volcengine.com/docs/82379/1824121)
- [图片理解](https://www.volcengine.com/docs/82379/1362931)
- [结构化输出（JSON Schema）](https://www.volcengine.com/docs/82379/1958523)"""

from .client import ArkClient

__all__ = ["ArkClient"]
