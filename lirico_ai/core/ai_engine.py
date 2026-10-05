from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    system_prompt: str = ""
    temperature: float = 0.2
    max_tokens: int = 2048


class AIEngine(ABC):
    """Contrato estável entre o Lírico e qualquer runtime de IA local."""

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate(self, request: GenerationRequest) -> str:
        raise NotImplementedError

    def models(self) -> Iterable[str]:
        return ()
