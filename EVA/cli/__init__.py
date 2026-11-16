r"""# cli 模块

```bash
# 查看非敏感配置
uv run eva config

# 只测试路由
uv run eva route --prompt '一张写着春日咖啡的海报' --target-text '春日咖啡'

# 真实生成并评分
uv run eva run --prompt '一张写着春日咖啡的海报' --target-text '春日咖啡'

# 带输入图生成
uv run eva run --prompt '保留主体，把背景换成月球' --image /path/source.png

# 不生成，只评已有图
uv run eva run --prompt '一张猫的照片' --generated-image /path/generated.png
```"""
