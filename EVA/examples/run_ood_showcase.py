"""Out-of-distribution prompts for style, domain, text and editing generalization."""

from __future__ import annotations

import asyncio
import json

from EVA.config import get_settings
from EVA.examples.run_showcase import _execute
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline

T2I_CASES = [
    {
        "case": "ood_macro_watch",
        "prompt": (
            "超写实微距产品摄影，一块独特的半透明琥珀机械腕表斜放在湿润的黑色玄武岩上，"
            "琥珀表壳内部可见三层交叠黄铜齿轮与一颗蓝色蓝宝石轴承，表盘无品牌。"
            "只能有一块腕表，黑色钛金属表带从左上延伸到右下。表背刻字仅为“N°07”，必须清晰可读，"
            "不得出现其他品牌、字母或数字。画面中只能有三颗独立螺丝：左上一颗、右侧一颗、底部中央一颗；"
            "表壳表面恰好七滴圆形水珠，不能增加更多水珠。侧逆光穿过琥珀，真实折射、金属拉丝、"
            "岩石水膜和浅景深，不能出现人物、第二个表盘、手链或额外首饰。"
        ),
        "target_texts": ["N°07"],
    },
    {
        "case": "ood_gongbi_blueprint",
        "prompt": (
            "中国传统工笔重彩与淡蓝工程蓝图线稿融合的长卷，五只机械白鹭飞入初夏荷塘，"
            "每只白鹭的左翼是洁白羽毛，右翼露出细密铜骨架，五只姿态必须不同且互不重叠。"
            "水面只有三只莲蓬，水下能看到两只红色锦鲤，远处一只木船但没有人物。"
            "左下角用毛笔写“惊蛰”，右上角用小型无衬线字体写“AWAKEN”，除这两处外不得出现任何文字、"
            "数字、尺寸线编号或印章。设色克制，宣纸纤维、石青与赭石渐变、机械铆钉和荷叶叶脉清晰。"
        ),
        "target_texts": ["惊蛰", "AWAKEN"],
    },
    {
        "case": "ood_greenhouse_dashboard",
        "prompt": (
            "一张16:9中文智慧温室数据看板，扁平矢量UI，不使用照片、人物或植物插画。"
            "严格四张等宽卡片排成2×2网格：左上标题“空气温度”，数值“22.4°C”；"
            "右上标题“土壤湿度”，数值“41%”；左下标题“CO₂”，数值“620 ppm”；"
            "右下标题“灌溉”，状态“关闭”。所有标签和数值一一对应，不能交换卡片位置，"
            "不得新增第五张卡片、折线图、告警、Logo、页码、其他文字或装饰性数字。"
            "深海军蓝背景，青绿色状态线，圆角12像素，充足留白，文字清楚锐利。"
        ),
        "target_texts": ["空气温度", "22.4°C", "土壤湿度", "41%", "CO₂", "620 ppm", "灌溉", "关闭"],
    },
    {
        "case": "ood_woodcut_arctic",
        "prompt": (
            "1920年代黑白木刻版画风格的北极考察站夜景，粗粝刀痕、有限灰阶与强烈黑白对比。"
            "画面中恰好四名穿厚羊毛外套的探险者和三只雪橇犬，四人分工明确：一人记录日记、"
            "一人提着鲸油灯、一人修理木质雪橇、一人站在雪屋门口守望，三只狗不能被画成狼或额外人物。"
            "背景有木屋、低矮雪墙和极光。门旁木牌只写“北纬 78°”，不得出现其他文字。"
            "禁止飞机、汽车、卫星天线、LED灯、羽绒服拉链、塑料设备或任何现代物品。"
        ),
        "target_texts": ["北纬 78°"],
    },
]


def dependent_cases(watch_path: str, bird_path: str) -> list[dict]:
    return [
        {
            "case": "ood_style_snow_egret",
            "prompt": (
                "仅参考输入图的“工笔重彩＋淡蓝工程蓝图线稿”风格，不复制原构图。"
                "改画大雪后的竹林，一只机械白鹭单脚站在浅溪中的青石上，白鹭仍保持左翼羽毛、"
                "右翼铜骨架的结构。背景恰好七根带雪竹竿，远景不得出现房屋、人物、莲蓬或木船。"
                "左下角用毛笔写“小雪”，右上角用无衬线小字写“SNOW”，除这两处外不得出现其他文字、"
                "数字或印章。保留宣纸纹理、石青与赭石配色和精细机械铆钉。"
            ),
            "input_images": [bird_path],
            "target_texts": ["小雪", "SNOW"],
        },
        {
            "case": "ood_edit_watch_background",
            "prompt": (
                "只把输入图的湿润黑色玄武岩背景替换为均匀象牙白博物馆天鹅绒，"
                "保留琥珀腕表的形状、角度、三层黄铜齿轮、蓝色轴承、黑色钛金属表带、"
                "三颗独立螺丝、七滴水珠以及表背刻字“N°07”的原始位置和字形。"
                "不得改变腕表材质、光照方向、齿轮结构、文字、产品比例和景深，"
                "不要增加展示盒、标签、人物、其他首饰或任何新物体。"
            ),
            "input_images": [watch_path],
            "target_texts": ["N°07"],
        },
    ]


async def main() -> None:
    settings = get_settings()
    settings.validate()
    showcase_id, showcase_dir = create_run_dir(settings.runs_dir, prefix="ood-showcase")
    pipeline = EvaluationPipeline(settings)
    print(f"OOD showcase directory: {showcase_dir}", flush=True)
    first = await asyncio.gather(*(_execute(pipeline, case) for case in T2I_CASES))
    failed = [item for item in first if "error" in item]
    if failed:
        write_json(showcase_dir / "summary.json", {"t2i": first})
        raise RuntimeError(f"OOD prerequisites failed: {failed}")
    print("OOD base images complete; starting style/edit cases", flush=True)
    dependent = await asyncio.gather(
        *(
            _execute(pipeline, case)
            for case in dependent_cases(first[0]["image"], first[1]["image"])
        )
    )
    summary = {
        "showcase_id": showcase_id,
        "showcase_dir": str(showcase_dir),
        "t2i": first,
        "dependent": dependent,
    }
    write_json(showcase_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
