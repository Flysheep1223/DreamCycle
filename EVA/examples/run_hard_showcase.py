"""Harder adversarial generation/edit cases with strict requirement metrics."""

from __future__ import annotations

import asyncio
import json

from EVA.config import get_settings
from EVA.examples.run_showcase import _execute
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline

HARD_ANIME = [
    {
        "case": "hard_anime_clockwork_station",
        "prompt": (
            "超复杂原创二次元时钟车站剖面图，必须同时满足全部约束。"
            "六名角色从左到右严格排列：1银发绿眼少女拿透明伞，2红双马尾少女抱蓝狐狸，"
            "3黑发少年推黄色工具车，4浅棕卷发护目镜少女拿扳手，5白发老者抱一本红书，"
            "6蓝发小孩抱一只黑猫。任何人都不能交换位置、服装或道具。"
            "前景恰好四只白猫，分别戴红、蓝、黄、绿项圈；真实空中恰好六只橙色纸鹤，"
            "镜面只反射其中三只纸鹤的倒影，因此全图可见六个实体纸鹤加三个倒影，共九个纸鹤形象；"
            "镜面不得额外生成现实中不存在的纸鹤。中央钟表的时针指向3、分针指向12。"
            "左侧招牌写“北”，中间小票写“春”，右下角黄色编号牌写“07”，三块文字不可互换，"
            "除这三处指定内容外，任何位置不得出现其他可读文字、数字、店名、日历页码或编号。"
            "场景包含螺旋楼梯、地下齿轮河、悬空书桥和两辆方向相反的列车，"
            "冷色雨夜与暖色车厢灯并存。日系赛璐璐，复杂但每个关键物体都清晰可数。"
        ),
        "target_texts": ["北", "春", "07"],
    },
    {
        "case": "hard_anime_mirror_florist",
        "prompt": (
            "高难度原创二次元镜面花店，强调属性绑定、左右手、遮挡和精确数量。"
            "画面现实空间只有两名角色：左侧短发绿眼少女穿蓝外套，人物自身右手拿红剪刀"
            "（正面对观众时位于画面左侧），人物自身左手拿蓝水壶（位于画面右侧）；"
            "右侧长白发少年穿黑外套，人物自身右手拿黄剪刀（位于画面左侧），"
            "人物自身左手拿透明喷壶（位于画面右侧），不得左右手互换。"
            "两人之间的桌上有恰好十二支玫瑰，五支红玫瑰在左瓶、七支白玫瑰在右瓶，"
            "不得多一朵或少一朵，桌面散落花瓣不计入玫瑰数量。少女身体遮住少年左半张脸，但少年的右眼仍可见。"
            "后墙上的大镜子只反射两人的背影和剪刀，镜中左右关系应符合镜面反射而非简单复制，"
            "镜子不得反射街道、车辆或花瓶。侧面独立窗户与镜子不是同一区域，"
            "左侧仅有1个价签写 LEFT，右侧仅有1个价签写 RIGHT，门牌仅有1个写 07，除此之外没有其他可读文字。"
            "窗外能看到雨中的三条街道，每条街只有一辆红色小车。精细日系动画背景与人物结构。"
        ),
        "target_texts": ["LEFT", "RIGHT", "07"],
    },
]


def _hard_image_cases(image_a: str, image_b: str) -> list[dict]:
    return [
        {
            "case": "hard_reference_paper_theater",
            "prompt": (
                "以输入图最左侧银发绿眼持透明伞少女为身份参考，将她变成纸雕剧场里的Q版角色，"
                "但仍须辨认出相同脸型、银发和绿眼。她现在穿白色宇航服、抱一颗蓝色星球，"
                "不再穿参考图中的原始服装。她身后是一面魔法记忆镜，显示的是她过去的旧形象，"
                "镜中必须恢复参考图最左侧少女原始的外套、内搭、下装和透明伞，"
                "不得自行改成和服、羽织或其他款式，也不是现实物体的物理倒影；现实形象与镜中旧形象不得混淆，"
                "镜中不得出现现实宇航服形象的倒影。舞台左边有三个红色纸月亮，右边有两个黄色纸太阳，"
                "只能出现她一个真实角色。底部木牌写 PAPER-07，其他位置不要文字。"
                "多层剪纸阴影与柔和舞台光，Q版比例但身份特征清楚。"
            ),
            "input_images": [image_a],
            "target_texts": ["PAPER-07"],
        },
        {
            "case": "hard_reference_costume_swap",
            "prompt": (
                "组合两张输入图中的两位少女：图1银发绿眼少女与图2深色短发绿眼少女。"
                "保留各自脸型、发型、发色和眼睛颜色，但交换她们的外套："
                "银发绿眼少女改穿蓝绿色短斗篷，深色短发绿眼少女改穿藏青和服外套。"
                "服装交换不能造成脸或身份交换。银发少女站左侧，人物自身右手拿透明伞；"
                "深色短发少女站右侧，人物自身左手拿扳手（正面对观众时位于画面右侧），"
                "人物自身右手托一本红书（位于画面左侧），不得同一只手同时拿两个道具，也不得左右手互换。"
                "背景是一间有六扇窗的飞艇教室，六扇窗横向等高排列且位于人物与雨伞上方，"
                "人物、透明伞和黑板都不得遮挡窗户。每扇窗只看得到一种天气："
                "晴、雨、雪、雷、极光、星空，顺序不能改变。黑板上写 TEAM-07，地面不能有额外人物。"
                "精细原创二次元，复杂光影与机械教室细节。"
            ),
            "input_images": [image_a, image_b],
            "target_texts": ["TEAM-07"],
        },
        {
            "case": "hard_edit_one_hair_ribbon",
            "prompt": (
                "只编辑输入图中央酒红双马尾少女头部右侧清晰可见的红色蝴蝶结发饰："
                "把该蝴蝶结主体颜色从红色改为青绿色，形状、大小、位置和丝带走向保持。"
                "不得修改她怀中蓝狐、手臂、袖套或其他人物，尤其不要改黑发推车少年的袖章。"
                "除此之外必须逐像素尽量不变：左侧招牌仍写“北”，中间小票仍写“春”，"
                "右下角黄色编号牌仍写“07”，其他原有文字也不得改变。"
                "所有人物的脸、发型、衣服其他部分、位置、动作、白猫与黑猫、橙色纸鹤、钟表、"
                "螺旋楼梯、地下齿轮河、悬空书桥和两辆列车都必须保持，不能增减任何物体，"
                "不能改变雨滴、灯光、构图和背景，禁止把任何招牌改成“星轨茶馆”。"
            ),
            "input_images": [image_a],
            "target_texts": ["北", "春", "07"],
        },
        {
            "case": "hard_edit_mirror_cat_text",
            "prompt": (
                "编辑输入的镜面花店图：找到镜子反射区域中门上的“07”门牌号，"
                "把该原位置的文字替换为“云上书店”，不得新增另一块木牌，也不得把文字放到真实空间其他位置。"
                "只在真实空间的镜框左右两侧各新增一只红色纸鹤，合计两只，纸鹤不得进入镜面或遮挡人物。"
                "原图真实空间没有白猫，请在四个指定真实空间位置分别新增一个花盆并放入一只白猫："
                "左上靠窗真实位置、左侧 LEFT 价签旁真实台面、右侧 RIGHT 价签旁真实台面、右下角真实桌面。"
                "每个新增花盆只放一只白猫，真实空间白猫总数恰好四只；不得借用原有透明玫瑰花瓶，"
                "不得把白猫放在人物手臂、工具或花瓶里，也不得给真实人物添加猫耳或尾巴。"
                "镜子可以自然反射这些新增物体，镜中倒影不计为额外真实白猫；但不得凭空出现没有实体对应的"
                "镜中白猫，也不得改变镜中两人的背影、街景和左右关系。保留两名真实人物及镜中两人的背影、"
                "左右手工具、玫瑰、LEFT/RIGHT价签、窗外街景和其他构图细节，人物身份、动作和服装不得改变。"
            ),
            "input_images": [image_b],
            "target_texts": ["云上书店"],
        },
    ]


async def main() -> None:
    settings = get_settings()
    settings.validate()
    showcase_id, showcase_dir = create_run_dir(settings.runs_dir, prefix="hard-showcase")
    pipeline = EvaluationPipeline(settings)
    print(f"Hard showcase directory: {showcase_dir}", flush=True)
    anime = await asyncio.gather(*(_execute(pipeline, case) for case in HARD_ANIME))
    failed = [item for item in anime if "error" in item]
    if failed:
        write_json(showcase_dir / "summary.json", {"anime": anime})
        raise RuntimeError(f"Hard anime prerequisites failed: {failed}")
    print("Hard anime complete; starting hard reference/edit cases", flush=True)
    image_results = await asyncio.gather(
        *(
            _execute(pipeline, case)
            for case in _hard_image_cases(anime[0]["image"], anime[1]["image"])
        )
    )
    summary = {
        "showcase_id": showcase_id,
        "showcase_dir": str(showcase_dir),
        "anime": anime,
        "image_tasks": image_results,
    }
    write_json(showcase_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
