"""Arbitrary storyboard grid and reading-order mapping without inferred panel shapes."""

from __future__ import annotations

from EVA.schemas import ActionRegion, StoryboardLayout


def region_for_panel(
    layout: StoryboardLayout | None, panel_index: int | None
) -> ActionRegion | None:
    """Resolve a panel region only when both grid dimensions are explicitly known."""
    if layout is None or panel_index is None:
        return None
    if layout.rows is None or layout.columns is None:
        return None
    if layout.rows * layout.columns != layout.panel_count:
        raise ValueError("Storyboard rows × columns must equal panel_count")
    if not 1 <= panel_index <= layout.panel_count:
        raise ValueError(f"panel_index must be in 1..{layout.panel_count}")

    index = panel_index - 1
    if layout.reading_order in {"left_to_right", "right_to_left"}:
        row = index // layout.columns
        column = index % layout.columns
        if layout.reading_order == "right_to_left":
            column = layout.columns - 1 - column
    else:
        column = index // layout.rows
        row = index % layout.rows
        if layout.reading_order == "bottom_to_top":
            row = layout.rows - 1 - row

    return ActionRegion(
        x=column / layout.columns,
        y=row / layout.rows,
        width=1 / layout.columns,
        height=1 / layout.rows,
    )
