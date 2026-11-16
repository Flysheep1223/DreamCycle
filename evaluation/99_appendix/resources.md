# 参考资料与复现工具入口

> 整理日期：2026-11-15。优先列论文作者/机构的官方资源。仓库默认分支会变化，正式实验请记录 commit 或 release。

## 1. 综述与“评价评价器”的研究

- **Evaluating Text-to-Image Synthesis: Survey and Taxonomy of Image Quality Metrics**（2024）：[arXiv 2403.11821](https://arxiv.org/abs/2403.11821)。按保真、对齐、美学等梳理传统与现代指标。
- **Revisiting Text-to-Image Evaluation with Gecko**，ICLR 2025：[论文](https://arxiv.org/abs/2404.16820)。强调 prompt slice、人工模板和模型排序/成对/点估计三种验证任务。
- **Evaluating the Evaluators: Metrics for Compositional Text-to-Image Generation**（2025）：[论文](https://arxiv.org/abs/2509.21227)。比较多类组合对齐评分器的人机一致性。
- **Holistic Evaluation of Text-to-Image Models (HEIM)**：[论文](https://arxiv.org/abs/2311.12987)。将对齐、质量、美学、推理、知识、公平、毒性、鲁棒、多语言和效率放在统一框架。
- **GenEval 2: Addressing Benchmark Drift**：[论文](https://arxiv.org/abs/2512.16853)。解释为什么旧评分器在新模型上会与人类判断漂移。
- **Quality Assessment for Text-to-Image Generation: A Survey**（2025）：[IEEE 页面](https://www.computer.org/csdl/magazine/mu/2025/02/10877350/247rXOwIrNm)。生成图质量评价专题。

## 2. 对齐与组合性官方实现

| 方法 | 官方入口 |
|---|---|
| CLIP / CLIPScore | [openai/CLIP](https://github.com/openai/CLIP)、[jmhessel/clipscore](https://github.com/jmhessel/clipscore) |
| BLIP / BLIP-2 | [salesforce/BLIP](https://github.com/salesforce/BLIP)、[salesforce/LAVIS](https://github.com/salesforce/LAVIS) |
| VQAScore / GenAI-Bench | [linzhiqiu/t2v_metrics](https://github.com/linzhiqiu/t2v_metrics) |
| TIFA | [Yushi-Hu/tifa](https://github.com/Yushi-Hu/tifa) |
| DSG | [j-min/DSG](https://github.com/j-min/DSG) |
| GenEval | [djghosh13/geneval](https://github.com/djghosh13/geneval) |
| GenEval 2 / Soft-TIFA | [facebookresearch/GenEval2](https://github.com/facebookresearch/GenEval2) |
| T2I-CompBench++ | [Karine-Huang/T2I-CompBench](https://github.com/Karine-Huang/T2I-CompBench) |
| DPG-Bench | [TencentQQGYLab/ELLA/dpg_bench](https://github.com/TencentQQGYLab/ELLA/tree/main/dpg_bench) |
| WISE | [PKU-YuanGroup/WISE](https://github.com/PKU-YuanGroup/WISE) |
| OneIG-Bench | [OneIG-Bench/OneIG-Benchmark](https://github.com/OneIG-Bench/OneIG-Benchmark) |
| VIEScore | [TIGER-AI-Lab/VIEScore](https://github.com/TIGER-AI-Lab/VIEScore) |

## 3. 偏好模型与质量工具

- PickScore：[代码](https://github.com/yuvalkirstain/PickScore)、[模型](https://huggingface.co/yuvalkirstain/PickScore_v1)
- HPS v2：[代码](https://github.com/tgxs002/HPSv2)
- HPS v3：[代码](https://github.com/MizzenAI/HPSv3)
- ImageReward：[代码](https://github.com/THUDM/ImageReward)
- MPS：[代码](https://github.com/Kwai-Kolors/MPS)
- VisionReward：[代码](https://github.com/THUDM/VisionReward)
- IQA-PyTorch / `pyiqa`：[chaofengc/IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch)。统一调用 MUSIQ、CLIP-IQA、Q-Align 及大量 NR/FR IQA；仍要记录具体 checkpoint。
- LAION Aesthetic：[官方](https://github.com/LAION-AI/aesthetic-predictor)、[improved 常用实现](https://github.com/christophschuhmann/improved-aesthetic-predictor)
- Q-Align：[项目](https://q-future.github.io/Q-Align/)

## 4. 分布与感知相似度工具

- Clean-FID：[GaParmar/clean-fid](https://github.com/GaParmar/clean-fid)。固定 resize/quantization，支持 clean/legacy 模式。
- Torch-Fidelity：[toshas/torch-fidelity](https://github.com/toshas/torch-fidelity)。FID、KID、IS、P&R 等。
- CMMD：[google-research/cmmd](https://github.com/google-research/google-research/tree/master/cmmd)
- PRDC：[clovaai/generative-evaluation-prdc](https://github.com/clovaai/generative-evaluation-prdc)
- Vendi Score：[vertaix/Vendi-Score](https://github.com/vertaix/Vendi-Score)
- LPIPS：[richzhang/PerceptualSimilarity](https://github.com/richzhang/PerceptualSimilarity)
- SSIM/PSNR/MS-SSIM：[piq](https://github.com/photosynthesis-team/piq)、[scikit-image](https://scikit-image.org/docs/stable/api/skimage.metrics.html)
- DINO / DINOv2：[DINO](https://github.com/facebookresearch/dino)、[DINOv2](https://github.com/facebookresearch/dinov2)

## 5. 编辑、多模态与 OCR

- PIE-Bench / PnP Inversion：[官方](https://github.com/cure-lab/PnPInversion)
- GEdit-Bench：[评分代码](https://github.com/stepfun-ai/Step1X-Edit/tree/main/GEdit-Bench)
- I²EBench：[cocoshe/I2EBench](https://github.com/cocoshe/I2EBench)
- ImgEdit：[PKU-YuanGroup/ImgEdit](https://github.com/PKU-YuanGroup/ImgEdit)
- DreamBench++：[yuangpeng/dreambench_plus](https://github.com/yuangpeng/dreambench_plus)
- MMIG-Bench：[hanghuacs/MMIG-Bench](https://github.com/hanghuacs/MMIG-Bench)
- AnyText：[tyxsspa/AnyText](https://github.com/tyxsspa/AnyText)
- PaddleOCR：[PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- `jiwer`（CER/WER）：[jitsi/jiwer](https://github.com/jitsi/jiwer)

## 6. 综合评测工程

- Stanford HELM/HEIM：[stanford-crfm/helm](https://github.com/stanford-crfm/helm)
- EvalScope（含 AIGC/T2I 评测文档）：[modelscope/evalscope](https://github.com/modelscope/evalscope)
- TorchMetrics：[Lightning-AI/torchmetrics](https://github.com/Lightning-AI/torchmetrics)

这些框架能简化运行，但“同一框架”不等于“同一协议”。仍需记录数据、checkpoint、resize、prompt 模板和聚合逻辑。

## 7. 人工与统计

- Artificial Analysis 图像方法页：[Image Methodology](https://artificialanalysis.ai/image/methodology)。BT MLE、Elo-like 缩放、投票 cohort 的实际示例。
- SciPy 统计：[scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)。Spearman、Kendall、Pearson、bootstrap。
- Choix（Bradley–Terry 等）：[lucasmaystre/choix](https://github.com/lucasmaystre/choix)
- Pingouin（ICC 等）：[pingouin-stats.org](https://pingouin-stats.org/)
- Krippendorff α：[fast-krippendorff](https://github.com/pln-fing-udelar/fast-krippendorff)

## 8. 引用规范

建议每个实验同时引用：

1. **生成模型**论文与精确 checkpoint；
2. **prompt/数据集**论文与版本；
3. **评分指标**原论文；
4. **实际实现**仓库 commit；
5. 若使用 VLM judge，附完整评审 prompt、模型快照与原始输出。

不要只引用一个排行榜或二手博客作为指标定义依据。二手资料可用于发现线索，最终数字与定义应回到论文、官方代码和数据卡。
