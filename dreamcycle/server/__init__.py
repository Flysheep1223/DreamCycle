r"""# server 模块

启动本地实时 API：

```bash
uv run uvicorn dreamcycle.server.app:app --host 127.0.0.1 --port 8000
```

- `GET /health`：查看非敏感配置；
- `POST /v1/evaluate`：生成并评分；传 `generated_image` 时仅评分已有图片。

请求示例：

```json
{
  "prompt": "一张写着春日咖啡的中文海报",
  "input_images": [],
  "target_texts": ["春日咖啡"]
}
```

当前只建议绑定 `127.0.0.1`，因为本地路径和任意图片 URL 都属于受信任的本地开发输入。"""
