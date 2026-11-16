from EVA.examples.run_prompt_optimization import generation_config


def test_generation_seed_blocks_are_fixed_and_do_not_repeat_after_plateau():
    blocks = {
        stage: {generation_config("ood_macro_watch", slot, stage)["seed"] for slot in range(4)}
        for stage in "BCDE"
    }
    assert blocks["B"] == {41000, 41001, 41002, 41003}
    assert blocks["C"] == {41004, 41005, 41006, 41007}
    assert blocks["D"] == {41008, 41009, 41010, 41011}
    assert blocks["E"] == {41012, 41013, 41014, 41015}
    for later in "CDE":
        assert blocks["B"].isdisjoint(blocks[later])


def test_generation_config_keeps_exact_size_and_omits_unsupported_guidance():
    config = generation_config("ood_style_snow_egret", 2, "D")
    assert config["size"] == "1776x2368"
    assert config["guidance_scale"] is None
    assert config["output_format"] == "png"
    assert config["watermark"] is False
