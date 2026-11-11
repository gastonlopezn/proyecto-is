from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class PredictionAuthor(ABC):
    nombre: str
    id: UUID = field(default_factory=uuid4)

    @abstractmethod
    def createQuestion(self) -> Question:
        ...
