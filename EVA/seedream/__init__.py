r"""# seedream 模块

使用用户配置的 `SEEDREAM_MODEL` 和 `SEEDREAM_SIZE`。

- 无输入图时只传 `prompt`；有输入图时传 URL 或本地图片 data URI。
- 多参考图以列表传给 Seedream。
- 支持一次返回多张图，全部下载后会逐张评分。
- 生成参数和输出位置保存到 `generation.json`，不保存密钥。"""

from .generator import SeedreamGenerator

__all__ = ["SeedreamGenerator"]
