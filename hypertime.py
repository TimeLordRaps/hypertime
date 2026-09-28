"""Finite Hypertime presentation, not a universal external clock."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Placement:
    reality_id: str
    index: int


@dataclass(frozen=True)
class Advance:
    earlier_id: str
    later_id: str


@dataclass(frozen=True)
class Frame:
    """Named presentations with an abstract display index and declared order."""

    placements: tuple[Placement, ...]
    advances: tuple[Advance, ...]

    def __post_init__(self) -> None:
        if (not isinstance(self.placements, tuple) or not 1 <= len(self.placements) <= 64
                or not isinstance(self.advances, tuple) or len(self.advances) > 256):
            raise ValueError("finite frame requires 1–64 placements and at most 256 advances")
        indices: dict[str, int] = {}
        for item in self.placements:
            if (not isinstance(item, Placement) or not isinstance(item.reality_id, str)
                    or not item.reality_id or not isinstance(item.index, int)
                    or isinstance(item.index, bool)):
                raise ValueError("invalid named hypertime placement")
            if item.reality_id in indices:
                raise ValueError("duplicate reality identity")
            indices[item.reality_id] = item.index
        seen: set[tuple[str, str]] = set()
        for step in self.advances:
            if (not isinstance(step, Advance) or not isinstance(step.earlier_id, str)
                    or not isinstance(step.later_id, str)
                    or step.earlier_id not in indices or step.later_id not in indices):
                raise ValueError("unbound hypertime advance")
            pair = (step.earlier_id, step.later_id)
            if pair in seen:
                raise ValueError("duplicate hypertime advance")
            if indices[step.earlier_id] >= indices[step.later_id]:
                raise ValueError("advance must increase the declared display index")
            seen.add(pair)


def project(frame: Frame) -> tuple[tuple[str, int], ...]:
    """Return the selected display axis; ties need not be simultaneous."""
    return tuple((item.reality_id, item.index)
                 for item in sorted(frame.placements, key=lambda item: (item.index, item.reality_id)))


def declared_precedes(frame: Frame, earlier_id: str, later_id: str) -> bool:
    """Test an explicit finite path, not causal or physical precedence."""
    names = {item.reality_id for item in frame.placements}
    if earlier_id not in names or later_id not in names:
        raise ValueError("unknown presented reality")
    if earlier_id == later_id:
        return False
    pending = [earlier_id]
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        for step in frame.advances:
            if step.earlier_id == current:
                if step.later_id == later_id:
                    return True
                pending.append(step.later_id)
    return False
