from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


ORANGE = "#ff5a1f"
ORANGE_DARK = "#e9470f"
INK = "#101828"
MUTED = "#667085"


class LiricoSplash(QWidget):
    """Four-second startup splash for Lírico AI."""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(620, 390)

        shell = QFrame(self)
        shell.setObjectName("splashShell")
        shell.setGeometry(0, 0, 620, 390)
        shell.setStyleSheet(
            f"""
            QFrame#splashShell {{
                background: white;
                border: 1px solid #eceef2;
                border-radius: 26px;
            }}
            """
        )

        layout = QVBoxLayout(shell)
        layout.setContentsMargins(52, 46, 52, 40)
        layout.setSpacing(0)

        brand = QHBoxLayout()
        brand.setSpacing(14)

        mark = QLabel("▥")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(58, 58)
        mark.setStyleSheet(
            f"""
            QLabel {{
                background: {ORANGE};
                color: white;
                border-radius: 16px;
                font-size: 28px;
                font-weight: 800;
            }}
            """
        )
        brand.addWidget(mark)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)

        name = QLabel("Lírico AI")
        name.setStyleSheet(
            f"font-size: 27px; font-weight: 800; color: {INK};"
        )
        tagline = QLabel("Suas ideias, em texto.")
        tagline.setStyleSheet(
            f"font-size: 12px; color: {MUTED};"
        )

        brand_text.addWidget(name)
        brand_text.addWidget(tagline)
        brand.addLayout(brand_text)
        brand.addStretch(1)

        layout.addLayout(brand)
        layout.addStretch(1)

        hero = QLabel(
            'Transcrição <span style="color:#ff5a1f;">inteligente</span><br>'
            'de áudio e vídeo'
        )
        hero.setTextFormat(Qt.TextFormat.RichText)
        hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero.setStyleSheet(
            f"font-size: 30px; font-weight: 800; color: {INK};"
        )
        layout.addWidget(hero)

        subtitle = QLabel(
            "Preparando sua experiência de transcrição com IA"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: 13px; color: {MUTED}; margin-top: 10px;"
        )
        layout.addWidget(subtitle)

        layout.addStretch(1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(7)
        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                background: #fff0e8;
                border: 0;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {ORANGE};
                border-radius: 3px;
            }}
            """
        )
        layout.addWidget(self.progress)

        status = QLabel("Iniciando Lírico AI...")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet(
            f"font-size: 11px; color: {MUTED}; margin-top: 10px;"
        )
        layout.addWidget(status)

        footer = QLabel("AXIA CORP")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "font-size: 9px; color: #b5bcc7; letter-spacing: 2px; margin-top: 10px;"
        )
        layout.addWidget(footer)

    def show_centered(self):
        screen = self.screen() or self.windowHandle().screen() if self.windowHandle() else None
        if screen is None:
            from PyQt6.QtWidgets import QApplication

            screen = QApplication.primaryScreen()

        if screen is not None:
            area = screen.availableGeometry()
            self.move(
                area.center().x() - self.width() // 2,
                area.center().y() - self.height() // 2,
            )

        self.show()
        self.raise_()
        self.activateWindow()
