# Elo / Bradley–Terry（BT）模型排名

## 一句话介绍

将大量两两胜负转成全模型相对能力分。Elo 常用递推更新，BT 用最大似然拟合成对胜率；很多现代图像 Arena 实际用 BT MLE 后再缩放到 Elo-like 分数。

- **输入**：模型间成对 A/B/tie 投票矩阵
- **输出**：相对 rating、预计胜率与区间
- **关键依赖**：对手池、票池、连通性、tie 模型、时间窗口与锚点
- **不能解释为**：图像绝对质量百分比

## 经典 Elo

模型 A 对 B 的期望胜率：

`E_A = 1 / (1 + 10^((R_B-R_A)/400))`

实际结果 `S_A∈{0,0.5,1}` 后：

`R_A' = R_A + K(S_A-E_A)`

K 控制更新幅度。递推 Elo 可能受比赛顺序、初始 rating、K 与活跃程度影响；离线研究通常更倾向统一拟合 BT。

## Bradley–Terry

每个模型有能力参数 `β_m`：

`P(A≻B) = exp(β_A) / [exp(β_A)+exp(β_B)] = sigmoid(β_A-β_B)`

最大化所有比较的对数似然求 `β`。为了可识别需设一个模型为 0、令均值 0 或加正则。可用 Rao–Kupper/Davidson 等扩展建模平局。

将 `β` 线性映射到 Elo-like 数值只是显示尺度；锚定某模型为 1000 或改变缩放不会改变由同一模型导出的理论胜率，但会改变表面分值。

## 拟合与报告

1. 清洗机器人/异常票，但不能按“是否支持某模型”过滤。
2. 保留完整两两矩阵、平局、票数和时间范围。
3. 检查比较图是否连通；新模型若只与少数对手比较，rating 不稳定。
4. 对 prompt/rater 聚类 bootstrap，重新拟合 BT，给 rating 区间与两两胜率区间。
5. 报告锚点、正则、tie 模型、样本量和是否仅使用当前方法版本票。

## 优点

- 将不完整、非全连接的成对比较整合成统一相对排名。
- 可预测未直接比较模型的理论胜率，并量化新模型不确定性。
- 比只报总票数更能处理对手强度不同。

## 局限

- BT 假设单一潜在能力及较一致的传递性；实际模型在人物、文字、编辑等子域可能形成不同排名。
- 非独立投票、位置偏差和人群偏好会进入参数；模型分数不是客观物理量。
- 增加/删除模型或改变 prompt 分布会改变 rating；旧榜与新榜不能只因锚点相同就直接连线。
- 置信区间相近时不应强排唯一冠军；同时给分项两两矩阵更透明。

## 实际 Arena 示例

Artificial Analysis 图像评测方法页说明其 Quality Elo 使用 **Bradley–Terry 最大似然**并做 Elo-like 缩放，区分 T2I 与 Editing，且方法版本和投票 cohort 会变化。引用榜单必须写查询日期和 cohort，不要复制分值后省略方法版本。

## 来源与实现

- Elo, **The Rating of Chessplayers, Past and Present**（Elo 基础）
- Bradley & Terry, 1952（BT 模型）
- 官方图像 Arena 方法说明：[Artificial Analysis Image Methodology](https://artificialanalysis.ai/image/methodology)
- 常用统计实现：[Choix](https://github.com/lucasmaystre/choix)、Python `statsmodels`/自行 scipy MLE
