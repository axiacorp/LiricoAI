from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy
)

from buzz.assets import get_path


class LiricoDashboardWidget(QWidget):
    """Lírico AI desktop shell.

    Keeps the proven transcription/history engine underneath, while replacing
    the legacy Buzz table-only home screen with the approved Lírico AI layout.
    """

    def __init__(self, history_widget: QWidget, on_new_transcription, on_converter, parent=None):
        super().__init__(parent)
        self.history_widget = history_widget
        self.on_new_transcription = on_new_transcription
        self.on_converter = on_converter

        self.setObjectName("liricoRoot")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("liricoSidebar")
        sidebar.setFixedWidth(250)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(24, 28, 24, 24)
        side.setSpacing(14)

        logo = QLabel()
        pix = QPixmap(get_path("assets/liricoai-logo.png"))
        if not pix.isNull():
            logo.setPixmap(
                pix.scaledToWidth(
                    180, Qt.TransformationMode.SmoothTransformation
                )
            )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side.addWidget(logo)
        side.addSpacing(16)

        new_btn = QPushButton("+ Nova transcrição")
        new_btn.setObjectName("primaryNav")
        new_btn.clicked.connect(self.on_new_transcription)
        side.addWidget(new_btn)

        transcribe_btn = QPushButton("Transcrever")
        transcribe_btn.setObjectName("navButton")
        transcribe_btn.clicked.connect(self.on_new_transcription)
        side.addWidget(transcribe_btn)

        converter_btn = QPushButton("Converter mídia")
        converter_btn.setObjectName("navButton")
        converter_btn.clicked.connect(self.on_converter)
        side.addWidget(converter_btn)

        history_btn = QPushButton("Histórico")
        history_btn.setObjectName("navButton")
        history_btn.clicked.connect(self.focus_history)
        side.addWidget(history_btn)

        side.addStretch(1)
        footer = QLabel("Lírico AI")
        footer.setObjectName("sidebarFooter")
        side.addWidget(footer)
        root.addWidget(sidebar)

        main = QWidget()
        main.setObjectName("liricoMain")
        body = QVBoxLayout(main)
        body.setContentsMargins(34, 28, 34, 30)
        body.setSpacing(18)

        title = QLabel("Lírico AI")
        title.setObjectName("pageTitle")
        body.addWidget(title)

        subtitle = QLabel(
            "Transcrição de áudio e vídeo, modelos locais e conversão de mídia."
        )
        subtitle.setObjectName("pageSubtitle")
        body.addWidget(subtitle)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(26, 22, 26, 22)
        hero_layout.setSpacing(10)

        hero_title = QLabel("Nova transcrição")
        hero_title.setObjectName("cardTitle")
        hero_layout.addWidget(hero_title)

        hero_text = QLabel(
            "Selecione um áudio ou vídeo e configure o modelo, idioma e resultado."
        )
        hero_text.setWordWrap(True)
        hero_text.setObjectName("cardText")
        hero_layout.addWidget(hero_text)

        hero_action = QPushButton("Selecionar áudio ou vídeo")
        hero_action.setObjectName("primaryAction")
        hero_action.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hero_action.clicked.connect(self.on_new_transcription)
        hero_layout.addWidget(hero_action)
        body.addWidget(hero)

        section_row = QHBoxLayout()
        section_row.setSpacing(14)

        trans_card = self._action_card(
            "Transcrever",
            "Use Whisper local, Whisper.cpp, Faster Whisper e outros modelos suportados.",
            "Nova transcrição",
            self.on_new_transcription,
        )
        conv_card = self._action_card(
            "Converter mídia",
            "Converta arquivos de áudio e vídeo diretamente no computador.",
            "Abrir conversor",
            self.on_converter,
        )
        section_row.addWidget(trans_card)
        section_row.addWidget(conv_card)
        body.addLayout(section_row)

        history_label = QLabel("Histórico")
        history_label.setObjectName("sectionTitle")
        body.addWidget(history_label)

        history_frame = QFrame()
        history_frame.setObjectName("historyCard")
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_widget.setParent(history_frame)
        history_layout.addWidget(self.history_widget)
        body.addWidget(history_frame, 1)

        root.addWidget(main, 1)
        self.setStyleSheet(self._stylesheet())

    def _action_card(self, title, text, button_text, callback):
        card = QFrame()
        card.setObjectName("actionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)

        desc = QLabel(text)
        desc.setWordWrap(True)
        desc.setObjectName("cardText")
        layout.addWidget(desc)

        button = QPushButton(button_text)
        button.setObjectName("secondaryAction")
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return card

    def focus_history(self):
        self.history_widget.setFocus()
        self.history_widget.scrollToTop()

    @staticmethod
    def _stylesheet():
        return """
        QWidget#liricoRoot {
            background: #f7f4f1;
            color: #201d1b;
        }
        QFrame#liricoSidebar {
            background: #28221f;
            border: none;
        }
        QLabel#sidebarFooter {
            color: #a99f99;
            font-size: 12px;
        }
        QPushButton#primaryNav {
            background: #ff6b00;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 13px 16px;
            font-size: 15px;
            font-weight: 700;
            text-align: left;
        }
        QPushButton#primaryNav:hover {
            background: #e85f00;
        }
        QPushButton#navButton {
            background: #3a322e;
            color: #f5f1ee;
            border: none;
            border-radius: 9px;
            padding: 12px 14px;
            font-size: 14px;
            text-align: left;
        }
        QPushButton#navButton:hover {
            background: #4a403b;
        }
        QWidget#liricoMain {
            background: #faf8f6;
        }
        QLabel#pageTitle {
            font-size: 28px;
            font-weight: 800;
            color: #211e1c;
        }
        QLabel#pageSubtitle {
            font-size: 14px;
            color: #756c66;
        }
        QFrame#heroCard, QFrame#actionCard, QFrame#historyCard {
            background: white;
            border: 1px solid #e7ded7;
            border-radius: 14px;
        }
        QLabel#cardTitle, QLabel#sectionTitle {
            font-size: 18px;
            font-weight: 750;
            color: #211e1c;
        }
        QLabel#sectionTitle {
            margin-top: 4px;
        }
        QLabel#cardText {
            color: #756c66;
            font-size: 13px;
        }
        QPushButton#primaryAction {
            background: #ff6b00;
            color: white;
            border: none;
            border-radius: 9px;
            padding: 11px 16px;
            font-weight: 700;
        }
        QPushButton#primaryAction:hover {
            background: #e85f00;
        }
        QPushButton#secondaryAction {
            background: #fff7f1;
            color: #d95400;
            border: 1px solid #ffc89f;
            border-radius: 8px;
            padding: 9px 13px;
            font-weight: 650;
        }
        QPushButton#secondaryAction:hover {
            background: #ffefe2;
        }
        QFrame#historyCard QTableView {
            background: white;
            alternate-background-color: #fbf8f6;
            border: none;
            gridline-color: #eee5df;
            selection-background-color: #fff0e5;
            selection-color: #201d1b;
        }
        QFrame#historyCard QHeaderView::section {
            background: #f7f2ee;
            color: #5e5550;
            border: none;
            border-bottom: 1px solid #e7ded7;
            padding: 8px;
            font-weight: 650;
        }
        """
