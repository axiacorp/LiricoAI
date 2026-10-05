from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from lirico_ai.core.embedded_llama import EmbeddedLlamaEngine
from lirico_ai.core.paths import default_model_path, runtime_executable


class HomePage(QWidget):
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

        for text in (
            "Transcrever áudio ou vídeo",
            "Gerar aula completa",
            "Criar resumo",
            "Gerar questões",
            "Criar flashcards",
            "Conversar com documentos",
        ):
            button = QPushButton(text)
            button.setMinimumHeight(42)
            layout.addWidget(button)

        layout.addStretch()


class StatusPage(QWidget):
    def __init__(self, engine: EmbeddedLlamaEngine) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Inteligência local")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(title)

        available = engine.is_available()
        status = QLabel(
            "Motor local pronto para uso."
            if available
            else "Estrutura pronta. Runtime/modelo ainda não empacotados."
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
        self.status = StatusPage(self.engine)
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.status)

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
