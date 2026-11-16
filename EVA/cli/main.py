"""Command line entry point: config, route-only, or full generate-and-score."""

from __future__ import annotations

import argparse
import asyncio
import json

from EVA.ark import ArkClient
from EVA.config import get_settings
from EVA.pipeline import EvaluationPipeline
from EVA.router import Router


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eva", description="Seedream realtime evaluator")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("config", help="Print non-secret configuration")
    route = sub.add_parser("route", help="Only run the multi-label router")
    _add_request_args(route, generation=False)
    run = sub.add_parser("run", help="Generate (or reuse) an image and score it")
    _add_request_args(run, generation=True)
    return parser


def _add_request_args(parser: argparse.ArgumentParser, generation: bool) -> None:
    parser.add_argument("--prompt", required=True)
    parser.add_argument(
        "--image", action="append", default=[], help="Input/reference image path or URL; repeatable"
    )
    parser.add_argument(
        "--target-text",
        action="append",
        default=[],
        help="Exact text expected in the output; repeatable",
    )
    if generation:
        parser.add_argument(
            "--generated-image", help="Skip generation and score this existing image"
        )
        parser.add_argument(
            "--no-advice",
            action="store_true",
            help="Skip the independent prompt/evaluation audit",
        )


async def _run(args: argparse.Namespace) -> None:
    settings = get_settings()
    if args.command == "config":
        print(json.dumps(settings.public_dict(), ensure_ascii=False, indent=2))
        return
    if args.command == "route":
        settings.validate(require_seedream=False)
        router = Router(ArkClient(settings))
        result = await router.route(
            prompt=args.prompt,
            input_images=args.image,
            explicit_target_texts=args.target_text,
        )
        print(result.model_dump_json(indent=2))
        return
    settings.validate(require_seedream=not bool(args.generated_image))
    pipeline = EvaluationPipeline(settings)
    result = await pipeline.run(
        prompt=args.prompt,
        input_images=args.image,
        target_texts=args.target_text,
        generated_image=args.generated_image,
        include_advice=not args.no_advice,
    )
    summary = {
        "run_id": result.run_id,
        "output_dir": result.output_dir,
        "modes": [mode.value for mode in result.route.modes],
        "evaluations": [
            {
                "image": evaluation.image.path,
                "metrics": evaluation.metrics,
                "failure_tags": evaluation.failure_tags,
                "advice": (
                    evaluation.advice.model_dump(mode="json")
                    if evaluation.advice is not None
                    else None
                ),
            }
            for evaluation in result.evaluations
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    args = _parser().parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
