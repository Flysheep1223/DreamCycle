# OCR Accuracy / Sentence Accuracy（文字完全正确率）

## 一句话介绍

用 OCR 从生成图识别文字，与 ground truth 做精确字符串匹配，计算完全正确的文本行/句子/区域比例；是视觉文字渲染最严格的常用指标之一。

- **输入**：生成图、目标文本，最好还有文本区域位置/顺序
- **输出**：0–1 或百分数，越高越好
- **常见基准**：AnyText-Benchmark、TextDiffuser/MARIO-Eval、CVTG-2K
- **关键**：OCR 引擎、文本归一化、区域匹配与“按行还是按整图”定义

## 基本公式

对第 `i` 个目标文本区域：

`correct_i = 1[normalize(OCR(x)_matched_i) = normalize(gt_i)]`

`Sen.Acc = (1/N) Σ_i correct_i`

任何替换、插入或删除都使该区域为 0，因此它回答的是“完全可用”而非“相似程度”。

## 区域级与整图级不要混淆

- **Region/Sentence Accuracy**：每个目标文本行/区域独立算一次。
- **Image Exact Accuracy**：一张图所有要求文本区域都完全正确才记 1；多区域海报更严格。
- 可再定义 **No-extra-text Accuracy**：除所有 GT 正确外，不允许额外幻觉文字。是否采用需预先声明。

## 标准评分流程

1. 用固定 OCR 检测+识别模型处理整张生成图，保留文本、box 与置信度。
2. 按 GT 区域 IoU/位置/阅读顺序匹配预测与 GT；无框任务需公开匹配规则。
3. 同时保留两套文本：
   - **strict**：只做必要解码，不改大小写/空格/标点；
   - **normalized**：例如 Unicode NFKC、去除首尾空格、统一连续空白，是否忽略大小写/标点另行声明。
4. 计算区域完全正确率和整图完全正确率。
5. 对 OCR 失败、低置信和人工抽检样本单列，不能把所有 OCR 失败都武断视为生成错误。

## 归一化为何必须公开

`Café` 与 `Café` 可能视觉相同但 Unicode 码点不同；中文全角/半角、英文连字符、空格和智能引号也会改变 exact match。宽松归一化适合内容正确性，严格归一化适合排版交付。报告两者比只选一个更透明。

## 优点

- 直接对应“文字是否可交付”，不会被大部分正确掩盖关键错字。
- 结果易解释，可与 NED/CER 联合定位轻微和严重错误。
- 不需要生成像素级目标图，适用于多种字体和背景。

## 局限

- OCR 对艺术字体、低分辨率、弯曲/遮挡文字有误检，分数同时受生成器和 OCR 影响。
- 完全正确率不提供部分信用：错一个字符与整句无关都为 0。
- 多文本区域的匹配/阅读顺序若不统一，结果不可复现。
- 只测文字，不测背景、布局、美感或非文字 prompt 对齐。

## 来源与工具

- Tuo et al., **AnyText: Multilingual Visual Text Generation and Editing**：[论文](https://arxiv.org/abs/2311.03054)，[官方代码](https://github.com/tyxsspa/AnyText)
- Chen et al., **TextDiffuser**（MARIO 系列评测与 OCR）：[论文](https://arxiv.org/abs/2305.10855)
- 常用 OCR：[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

> 报告示例：`Sentence Accuracy / PaddleOCR exact version / NFKC+case-sensitive / region-level / English split`。
