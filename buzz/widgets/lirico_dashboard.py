from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QStackedWidget, QScrollArea
)

from buzz.assets import get_path


class LiricoDashboardWidget(QWidget):
    """Lírico AI desktop shell.

    Keeps the proven transcription/history engine underneath, while replacing
    the legacy Buzz table-only home screen with the approved Lírico AI layout.
    """

    def __init__(self, history_widget: QWidget, on_new_transcription, on_converter, on_quit, parent=None):
        super().__init__(parent)
        self.history_widget = history_widget
        self.on_new_transcription = on_new_transcription
        self.on_converter = on_converter
        self.on_quit = on_quit

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
        history_btn.clicked.connect(self.show_history)
        side.addWidget(history_btn)

        side.addStretch(1)

        quit_btn = QPushButton("Sair")
        quit_btn.setObjectName("quitNav")
        quit_btn.clicked.connect(self.on_quit)
        side.addWidget(quit_btn)

        footer = QLabel("Lírico AI")
        footer.setObjectName("sidebarFooter")
        side.addWidget(footer)
        root.addWidget(sidebar)

        self.pages = QStackedWidget()
        self.pages.setObjectName("liricoPages")

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
        body.addStretch(1)

        transcribe_page = QWidget()
        transcribe_page.setObjectName("liricoMain")
        transcribe_outer = QVBoxLayout(transcribe_page)
        transcribe_outer.setContentsMargins(34, 28, 34, 30)
        transcribe_outer.setSpacing(14)

        eyebrow = QLabel("NOVA TRANSCRIÇÃO")
        eyebrow.setObjectName("eyebrow")
        transcribe_outer.addWidget(eyebrow)

        transcribe_title = QLabel("Preparar arquivo")
        transcribe_title.setObjectName("pageTitle")
        transcribe_outer.addWidget(transcribe_title)

        transcribe_subtitle = QLabel(
            "Escolha o arquivo, o modelo de transcrição, o idioma e o tipo de conteúdo."
        )
        transcribe_subtitle.setObjectName("pageSubtitle")
        transcribe_outer.addWidget(transcribe_subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("transcribeScroll")

        scroll_body = QWidget()
        scroll_body.setObjectName("liricoMain")
        scroll_layout = QVBoxLayout(scroll_body)
        scroll_layout.setContentsMargins(0, 8, 0, 0)
        scroll_layout.setSpacing(16)

        file_card = QFrame()
        file_card.setObjectName("heroCard")
        file_layout = QVBoxLayout(file_card)
        file_layout.setContentsMargins(22, 18, 22, 18)
        file_layout.setSpacing(10)
        file_title = QLabel("1. Selecionar áudio ou vídeo")
        file_title.setObjectName("cardTitle")
        file_layout.addWidget(file_title)

        self.selected_file_label = QLabel("Nenhum arquivo selecionado")
        self.selected_file_label.setObjectName("selectedFile")
        self.selected_file_label.setWordWrap(True)
        file_layout.addWidget(self.selected_file_label)

        change_file_button = QPushButton("Trocar arquivo")
        change_file_button.setObjectName("secondaryAction")
        change_file_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        change_file_button.clicked.connect(self.on_new_transcription)
        file_layout.addWidget(change_file_button)
        scroll_layout.addWidget(file_card)

        config_card = QFrame()
        config_card.setObjectName("heroCard")
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(22, 18, 22, 18)
        config_layout.setSpacing(12)
        config_title = QLabel("2. Configurar transcrição")
        config_title.setObjectName("cardTitle")
        config_layout.addWidget(config_title)

        self.transcription_host = QWidget()
        self.transcription_host_layout = QVBoxLayout(self.transcription_host)
        self.transcription_host_layout.setContentsMargins(0, 0, 0, 0)
        self.transcription_host_layout.setSpacing(0)
        config_layout.addWidget(self.transcription_host)
        scroll_layout.addWidget(config_card)
        scroll_layout.addStretch(1)

        scroll.setWidget(scroll_body)
        transcribe_outer.addWidget(scroll, 1)

        history_page = QWidget()
        history_page.setObjectName("liricoMain")
        history_body = QVBoxLayout(history_page)
        history_body.setContentsMargins(34, 28, 34, 30)
        history_body.setSpacing(16)

        history_title = QLabel("Histórico")
        history_title.setObjectName("pageTitle")
        history_body.addWidget(history_title)

        history_header = QHBoxLayout()
        history_header.setSpacing(10)

        history_subtitle = QLabel(
            "Suas transcrições ficam organizadas aqui."
        )
        history_subtitle.setObjectName("pageSubtitle")
        history_header.addWidget(history_subtitle, 1)

        delete_history_button = QPushButton("Excluir selecionado")
        delete_history_button.setObjectName("dangerAction")
        delete_history_button.clicked.connect(
            self.history_widget.request_delete_selected
        )
        history_header.addWidget(delete_history_button)
        history_body.addLayout(history_header)

        history_frame = QFrame()
        history_frame.setObjectName("historyCard")
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_widget.setParent(history_frame)
        history_layout.addWidget(self.history_widget)
        history_body.addWidget(history_frame, 1)

        self.pages.addWidget(main)
        self.pages.addWidget(transcribe_page)
        self.pages.addWidget(history_page)
        root.addWidget(self.pages, 1)
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

    def show_transcriber(self, widget: QWidget, display_name: str):
        while self.transcription_host_layout.count():
            item = self.transcription_host_layout.takeAt(0)
            old = item.widget()
            if old is not None and old is not widget:
                old.setParent(None)

        widget.setParent(self.transcription_host)
        self.transcription_host_layout.addWidget(widget)
        self.selected_file_label.setText(display_name or "Arquivo selecionado")
        self.pages.setCurrentIndex(1)

    def show_history(self):
        self.pages.setCurrentIndex(2)
        self.history_widget.setFocus()
        self.history_widget.scrollToTop()

    def show_home(self):
        self.pages.setCurrentIndex(0)

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
        QPushButton#quitNav {
            background: transparent;
            color: #cbbfb8;
            border: 1px solid #4a403b;
            border-radius: 9px;
            padding: 10px 14px;
            font-size: 14px;
            text-align: left;
        }
        QPushButton#quitNav:hover {
            background: #3a322e;
            color: white;
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
        QLabel#eyebrow {
            color: #ff6b00; font-size: 12px; font-weight: 800; letter-spacing: 1px;
        }
        QLabel#selectedFile {
            background: #fffaf6; border: 1px dashed #ffb47d; border-radius: 10px;
            padding: 16px; color: #3a332f; font-size: 14px;
        }
        QScrollArea#transcribeScroll { background: transparent; }
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
        QPushButton#dangerAction {
            background: #fff3f2;
            color: #b42318;
            border: 1px solid #f0b8b2;
            border-radius: 8px;
            padding: 9px 13px;
            font-weight: 700;
        }
        QPushButton#dangerAction:hover {
            background: #ffe7e4;
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
