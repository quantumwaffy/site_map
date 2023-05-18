from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Node:
    url: str
    children: tuple[Node, ...] = ()

    def __str__(self) -> str:
        return self.url
