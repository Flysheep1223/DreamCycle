r"""# spatial 模块

`SpatialHandJudge` 将左右手问题拆成两步：

1. VLM 只输出人物、扳手和红书的归一化 bbox，不判断左右手；
2. 程序比较物体中心与人物中心的 x 坐标。

对正面对观众的右侧人物，自身左手对应画面右侧、自身右手对应画面左侧。这样把空间计算交给程序，避免 VLM 在“自身左右”和“观众左右”之间反复改口。当前实现用于任务4的专项验证，不自动替代通用 VLM 评审。"""

from .hand_positions import SpatialHandJudge

__all__ = ["SpatialHandJudge"]
