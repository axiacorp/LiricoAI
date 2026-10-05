from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from lirico_ai.core.ai_engine import GenerationRequest
from lirico_ai.core.embedded_llama import EmbeddedLlamaEngine


class GenerationWorker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(
        self,
        engine: EmbeddedLlamaEngine,
        request: GenerationRequest,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.request = request

    @pyqtSlot()
    def run(self) -> None:
        try:
            result = self.engine.generate(self.request)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
