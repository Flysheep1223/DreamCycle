"""Run six real generation/evaluation showcases against the configured Ark models."""

from __future__ import annotations

import asyncio
import json

from EVA.config import get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline

ANIME_CASES = [
    {
        "case": "anime_cyber_shrine",
        "prompt": (
            "超精细原创日系赛璐璐二次元插画，雨夜的赛博神社与空中列车交汇。"
            "画面左侧是一名银白短发、翠绿色眼睛、穿藏青和服外套的少女，手持透明雨伞；"
            "中央是一名酒红双马尾、琥珀色眼睛、穿白色巫女服与红色电子袖套的少女，"
            "双手托起发光蓝色全息狐狸；右侧是一名黑发少年，穿黄色长雨衣，蹲着修理三轮机器人。"
            "三人必须完整出现且位置不可交换。前景有两尊石狐雕像、七只橙色纸鹤和一盏旧式绿灯笼；"
            "中景有交错的红色鸟居、雨滴与霓虹倒影；远景是穿过云层的磁悬浮列车。"
            "画面中央偏上的招牌只写“星轨茶馆”，字体清晰，不要其他标题。"
            "复杂但清晰的纵深构图，冷紫霓虹与暖橙灯光对比，细腻雨水、衣物纹样与金属反射。"
        ),
        "target_texts": ["星轨茶馆"],
    },
    {
        "case": "anime_sky_library",
        "prompt": (
            "高复杂度原创蒸汽朋克二次元场景，一座在云海上方移动的空中图书馆。"
            "左前景是戴圆形护目镜、浅棕卷发的少女机械师，穿蓝绿色短斗篷，正用扳手修理黄铜翅膀；"
            "中央是高挑的黑发图书管理员，戴银色单眼镜，穿深紫长外套，双手展开一本漂浮发光的书；"
            "右后方是穿橙红飞行服的小男孩，站在楼梯上拉动绳索。画面必须恰好有五只不同姿态的白猫，"
            "其中一只睡在打开的书上，一只抓着飘带。背景有螺旋书塔、齿轮温室、悬挂星图、"
            "三艘小型飞艇和穿过彩虹的巨大鲸鱼。入口木牌只写“云上书店”，不要出现其他店名。"
            "日系动画电影感，丰富机械细节，金色夕照穿过云层，清楚的人物遮挡关系和透视。"
        ),
        "target_texts": ["云上书店"],
    },
]


def _image_cases(image_a: str, image_b: str) -> list[dict]:
    return [
        {
            "case": "reference_single_observatory",
            "prompt": (
                "以输入图中的银白短发、翠绿色眼睛少女为唯一身份参考，保持她的脸型、发型、发色、"
                "瞳色和主要外观辨识度，生成她站在雪山天文台观景窗前的全新侧身半身像。"
                "她改穿白色高领防寒服与深蓝色星图披肩，手中仍有一把收起的透明雨伞。"
                "窗外是极光、雪峰和清晰的北斗七星，室内有黄铜望远镜与悬浮星盘。"
                "画面左下角用精致小字写 POLARIS。日系赛璐璐风格，不要改变角色身份。"
            ),
            "input_images": [image_a],
            "target_texts": ["POLARIS"],
        },
        {
            "case": "reference_dual_airship",
            "prompt": (
                "组合两张输入图中的角色：保留图1银白短发绿眼少女和图2浅棕卷发护目镜少女的身份特征。"
                "生成两人共同驾驶一艘小型木质飞艇穿过雷云的场景。银发少女站在左舷操控发光导航罗盘，"
                "卷发少女位于右侧俯身修理黄铜引擎，两人不能交换位置或合并外貌。"
                "远景保留空中图书馆和一条彩虹鲸鱼，雨滴、闪电和暖色船舱灯形成对比。"
                "船头小旗写 SKY CREW，其他区域不要标题。高细节原创二次元动画画面。"
            ),
            "input_images": [image_a, image_b],
            "target_texts": ["SKY CREW"],
        },
        {
            "case": "editing_rain_night",
            "prompt": (
                "编辑输入图：将原有雨夜场景进一步加强为深夜暴雨，保留三名角色的数量、身份、位置、"
                "姿态和服装，不改变石狐雕像与七只橙色纸鹤。把中央偏上的招牌文字从“星轨茶馆”"
                "精确替换为“夜宵茶馆”，只修改光照、雨势和该招牌文字，其他构图与人物细节尽量保持。"
            ),
            "input_images": [image_a],
            "target_texts": ["夜宵茶馆"],
        },
        {
            "case": "editing_desert_library",
            "prompt": (
                "编辑输入图：把云海背景替换为黄昏沙漠与远处岩石城，保留空中图书馆主体结构、"
                "三名主要人物的身份、位置、服装颜色与动作，以及恰好五只白猫。"
                "移除最远处三艘小飞艇，新增两只在书塔间盘旋的机械鸟。"
                "保留入口木牌“云上书店”的文字与位置，其他书籍、齿轮和人物细节尽量不变。"
            ),
            "input_images": [image_b],
            "target_texts": ["云上书店"],
        },
    ]


async def _execute(pipeline: EvaluationPipeline, case: dict) -> dict:
    try:
        result = await pipeline.run(
            prompt=case["prompt"],
            input_images=case.get("input_images", []),
            target_texts=case.get("target_texts", []),
        )
        evaluation = result.evaluations[0]
        return {
            "case": case["case"],
            "prompt": case["prompt"],
            "input_images": case.get("input_images", []),
            "target_texts": case.get("target_texts", []),
            "run_id": result.run_id,
            "output_dir": result.output_dir,
            "image": evaluation.image.path,
            "modes": [mode.value for mode in result.route.modes],
            "metrics": evaluation.metrics,
            "failure_tags": evaluation.failure_tags,
            "advice": (
                evaluation.advice.model_dump(mode="json") if evaluation.advice is not None else None
            ),
        }
    except Exception as exc:  # noqa: BLE001 - isolate independent live showcase failures.
        return {"case": case["case"], "error": f"{type(exc).__name__}: {exc}"}


async def main() -> None:
    settings = get_settings()
    settings.validate()
    showcase_id, showcase_dir = create_run_dir(settings.runs_dir, prefix="showcase")
    pipeline = EvaluationPipeline(settings)
    print(f"Showcase directory: {showcase_dir}", flush=True)

    anime = await asyncio.gather(*(_execute(pipeline, case) for case in ANIME_CASES))
    failed = [item for item in anime if "error" in item]
    if failed:
        write_json(showcase_dir / "summary.json", {"anime": anime})
        raise RuntimeError(f"Anime prerequisites failed; see summary: {failed}")
    print("Anime cases complete; starting reference and editing cases", flush=True)

    image_a = anime[0]["image"]
    image_b = anime[1]["image"]
    image_results = await asyncio.gather(
        *(_execute(pipeline, case) for case in _image_cases(image_a, image_b))
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
