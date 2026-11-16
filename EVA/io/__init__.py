r"""# io 模块

- URL 图片直接交给 Ark，本地图片压缩为有尺寸上限的 JPEG data URI。
- 生成结果下载后统一转成 PNG，便于 VLM、OCR 和测试读取。
- 每次运行创建独立 `EVA/runs/run-*` 目录，保存 route、原始 judge 输出和最终分数。
- 下载限制为 40 MB，且不会把 `.env` 写入运行目录。"""
