from __future__ import annotations

import sys

from PyQt6.QtCore import QThread, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from lirico_ai.core.ai_engine import GenerationRequest
from lirico_ai.core.embedded_llama import EmbeddedLlamaEngine
from lirico_ai.core.paths import default_model_path, runtime_executable
from lirico_ai.prompts import SYSTEM_PROMPT
from lirico_ai.workers import GenerationWorker


class HomePage(QWidget):
    generate_lesson_requested = __import__(
        "PyQt6.QtCore", fromlist=["pyqtSignal"]
    ).pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Lírico AI")
        title.setStyleSheet("font-size: 28px; font-weight: 600;")
        subtitle = QLabel(
            "Transcreva, estude, organize e transforme conteúdo com IA local."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        transcribe = QPushButton("Transcrever áudio ou vídeo")
        lesson = QPushButton("Gerar aula completa")
        lesson.clicked.connect(self.generate_lesson_requested.emit)

        for button in (
            transcribe,
            lesson,
            QPushButton("Criar resumo"),
            QPushButton("Gerar questões"),
            QPushButton("Criar flashcards"),
            QPushButton("Conversar com documentos"),
        ):
            button.setMinimumHeight(42)
            layout.addWidget(button)

        layout.addStretch()


class LessonPage(QWidget):
    back_requested = __import__(
        "PyQt6.QtCore", fromlist=["pyqtSignal"]
    ).pyqtSignal()

    def __init__(self, engine: EmbeddedLlamaEngine) -> None:
        super().__init__()
        self.engine = engine
        self.thread: QThread | None = None
        self.worker: GenerationWorker | None = None

        layout = QVBoxLayout(self)
        title = QLabel("Gerar aula completa")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(title)

        help_text = QLabel(
            "Cole uma transcrição ou material abaixo. O Lírico AI irá organizar "
            "o conteúdo e gerar uma aula didática usando somente a IA local."
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("Cole aqui a transcrição...")
        layout.addWidget(self.input, 2)

        actions = QHBoxLayout()
        back = QPushButton("Voltar")
        back.clicked.connect(self.back_requested.emit)
        self.generate = QPushButton("Gerar aula")
        self.generate.clicked.connect(self.generate_lesson)
        actions.addWidget(back)
        actions.addStretch()
        actions.addWidget(self.generate)
        layout.addLayout(actions)

        self.status = QLabel("")
        layout.addWidget(self.status)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("A aula gerada aparecerá aqui.")
        layout.addWidget(self.output, 3)

    def generate_lesson(self) -> None:
        source = self.input.toPlainText().strip()
        if not source:
            QMessageBox.information(
                self,
                "Lírico AI",
                "Cole uma transcrição ou material antes de gerar a aula.",
            )
            return

        if not self.engine.is_available():
            QMessageBox.warning(
                self,
                "IA local não instalada",
                "O runtime ou o modelo local ainda não foi instalado neste computador.",
            )
            return

        prompt = (
            "Transforme o conteúdo abaixo em uma aula completa e didática. "
            "Organize por títulos e subtítulos, preserve todas as informações "
            "relevantes, elimine repetições sem perder conteúdo e sinalize "
            "qualquer trecho duvidoso da transcrição.\n\n"
            "CONTEÚDO:\n"
            f"{source}"
        )
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=4096,
        )

        self.generate.setEnabled(False)
        self.status.setText("Lírico AI está gerando a aula localmente...")
        self.output.clear()

        self.thread = QThread(self)
        self.worker = GenerationWorker(self.engine, request)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._generation_finished)
        self.worker.failed.connect(self._generation_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_worker)
        self.thread.start()

    def _generation_finished(self, text: str) -> None:
        self.output.setPlainText(text)
        self.status.setText("Aula gerada com IA local.")
        self.generate.setEnabled(True)

    def _generation_failed(self, message: str) -> None:
        self.status.setText("Não foi possível gerar a aula.")
        self.generate.setEnabled(True)
        QMessageBox.critical(self, "Erro na IA local", message)

    def _cleanup_worker(self) -> None:
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.worker = None
        self.thread = None


class StatusPage(QWidget):
    def __init__(self, engine: EmbeddedLlamaEngine) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Inteligência local")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(title)

        available = engine.is_available()
        status = QLabel(
            "Motor local e modelo encontrados. O Lírico pode trabalhar offline."
            if available
            else "Estrutura pronta. Instale o runtime/modelo local para ativar a IA."
        )
        status.setWordWrap(True)
        layout.addWidget(status)
        layout.addWidget(QLabel(f"Runtime: {engine.runtime_path}"))
        layout.addWidget(QLabel(f"Modelo: {engine.model_path}"))
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Lírico AI")
        self.resize(1180, 760)

        self.engine = EmbeddedLlamaEngine(
            runtime_path=runtime_executable(),
            model_path=default_model_path(),
        )

        container = QWidget()
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)

        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        brand = QLabel("LÍRICO AI")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("font-size: 18px; font-weight: 700; padding: 16px;")
        side.addWidget(brand)

        self.stack = QStackedWidget()
        self.home = HomePage()
        self.lesson = LessonPage(self.engine)
        self.status = StatusPage(self.engine)
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.lesson)
        self.stack.addWidget(self.status)

        self.home.generate_lesson_requested.connect(
            lambda: self.stack.setCurrentWidget(self.lesson)
        )
        self.lesson.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.home)
        )

        home_btn = QPushButton("Início")
        ai_btn = QPushButton("IA local")
        home_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.home))
        ai_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.status))
        side.addWidget(home_btn)
        side.addWidget(ai_btn)
        side.addStretch()

        root.addWidget(sidebar)
        root.addWidget(self.stack, 1)
        self.setCentralWidget(container)

    def closeEvent(self, event) -> None:
        self.engine.stop()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Lírico AI")
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())
