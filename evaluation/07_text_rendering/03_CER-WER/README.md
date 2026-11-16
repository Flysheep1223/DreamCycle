# CER / WER（Character / Word Error Rate）

## 一句话介绍

CER 将识别错误按参考字符数归一化，WER 按参考词数归一化，均由替换、删除、插入组成；越低越好，适合长文本、中文和英文的分粒度错误分析。

- **CER**：字符错误率，中文尤其常用
- **WER**：词错误率，英文及有空格分词语言常用
- **输出**：0 为完全正确；由于插入错误，**可大于 1/100%**
- **输入**：OCR 预测与 GT，需明确文本区域和阅读顺序

## 公式

对参考长度 `N`，最小编辑操作分解为替换 `S`、删除 `D`、插入 `I`：

`CER = (S_c + D_c + I_c) / N_chars`

`WER = (S_w + D_w + I_w) / N_words`

删除表示 GT 中有、OCR 漏掉；插入表示 OCR 多出内容。CER/WER 与 Accuracy 方向相反，不要标成越高越好。

## CER 与 NED 的关系

常见 NED 相似度用 `max(len(pred),len(gt))` 作分母，而 CER 用 `len(gt)`。因此：

- CER 可因大量插入超过 1；NED_similarity 通常仍在 0–1。
- 只有在特定操作/长度条件下两者才可简单写成 `NED_sim=1-CER`，不能默认成立。
- 报告时保留 S/D/I 分解，可区分漏字、错字、多字。

## 中文与英文注意

- 中文通常按 Unicode 字符算 CER；若计算 WER，必须指定分词器和是否保留标点。
- 英文 WER 需定义大小写、缩写、连字符、数字和标点；例如 `don't` 是一个词还是两个词。
- 多行文本需明确先按行计算再平均，还是按阅读顺序拼接后计算。
- 长文本可用 micro CER：`Σ(S+D+I)/ΣN`，避免短文本与长文本权重混淆。

## 优点

- 是 OCR/ASR 领域标准错误度量，容易解释错误总数。
- 比完全正确率更适合长文本，能区分局部错误和整体失败。
- S/D/I 分解可指导模型改进：漏生成、乱加字、字形混淆分别处理。

## 局限

- 依赖 OCR 和文本归一化，可能将 OCR 误识别计为生成错误。
- 字符/词等权不代表业务严重性；关键名称或数字可另设字段级准确率。
- 多区域顺序匹配不清会产生大量假替换，先做好区域对应。
- 不测文字位置、字体、可读性、背景和整体图像质量。

## 来源与工具

- 编辑距离及 ASR/OCR 通用错误率定义，可参照 [NIST sclite](https://github.com/usnistgov/SCTK)
- Python 实现：[jiwer](https://github.com/jitsi/jiwer)
- 长/稠密文字基准参考：[TextAtlas5M / TextAtlasEval](https://textatlas5m.github.io/)

> 报告示例：`micro CER / character-level / NFKC / punctuation retained / reading-order matched / 3,000 samples`。
