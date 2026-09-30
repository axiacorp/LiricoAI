from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


ORANGE = "#ff5a1f"
ORANGE_DARK = "#e9470f"
INK = "#111827"
MUTED = "#667085"
BORDER = "#e6e8ec"
SOFT = "#fff5ef"
PANEL = "#fffaf7"
BG = "#fbfbfc"
GREEN = "#16a34a"


class SidebarButton(QToolButton):
    def __init__(self, text: str, glyph: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setText(f"{glyph}   {text}")
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(46)
        self.setStyleSheet(
            f"""
            QToolButton {{
                border: 0;
                border-radius: 12px;
                padding: 0 16px;
                text-align: left;
                color: #344054;
                font-size: 14px;
                background: transparent;
            }}
            QToolButton:hover {{
                background: #fff7f2;
                color: {ORANGE_DARK};
            }}
            QToolButton:checked {{
                background: #fff0e8;
                color: {ORANGE};
                font-weight: 600;
            }}
            """
        )


class Card(QFrame):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            f"""
            QFrame#card {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            """
        )


class ModernDashboard(QWidget):
    """Modern Lírico AI shell for the existing Buzz transcription engine."""

    def __init__(
        self,
        history_widget: QWidget,
        on_select_file: Callable[[], None],
        on_record: Callable[[], None],
        on_preferences: Callable[[], None],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.history_widget = history_widget
        self.on_select_file = on_select_file
        self.on_record = on_record
        self.on_preferences = on_preferences

        self.setObjectName("liricoRoot")
        self.setStyleSheet(
            f"""
            QWidget#liricoRoot {{
                background: {BG};
                color: {INK};
            }}
            QLabel {{
                color: {INK};
            }}
            QPushButton {{
                font-size: 13px;
            }}
            """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_home_page())
        self.stack.addWidget(self._build_history_page())
        root.addWidget(self.stack, 1)

        self.show_home()

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(248)
        sidebar.setStyleSheet(
            f"""
            QFrame {{
                background: #ffffff;
                border-right: 1px solid {BORDER};
            }}
            """
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 28, 22, 24)
        layout.setSpacing(6)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        mark = QLabel("▥")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(42, 42)
        mark.setStyleSheet(
            f"""
            QLabel {{
                color: white;
                background: {ORANGE};
                border-radius: 12px;
                font-size: 22px;
                font-weight: 700;
            }}
            """
        )
        brand_row.addWidget(mark)

        brand = QVBoxLayout()
        brand.setSpacing(0)
        title = QLabel("Lírico AI")
        title.setStyleSheet("font-size: 22px; font-weight: 750; color: #101828;")
        subtitle = QLabel("Suas ideias, em texto.")
        subtitle.setStyleSheet("font-size: 11px; color: #98a2b3;")
        brand.addWidget(title)
        brand.addWidget(subtitle)
        brand_row.addLayout(brand, 1)
        layout.addLayout(brand_row)
        layout.addSpacing(24)

        self.home_button = SidebarButton("Início", "⌂")
        self.transcribe_button = SidebarButton("Transcrever", "≋")
        self.history_button = SidebarButton("Histórico", "◷")
        self.models_button = SidebarButton("Modelos", "▧")
        self.settings_button = SidebarButton("Configurações", "⚙")

        for button in (
            self.home_button,
            self.transcribe_button,
            self.history_button,
            self.models_button,
            self.settings_button,
        ):
            layout.addWidget(button)

        self.home_button.clicked.connect(self.show_home)
        self.transcribe_button.clicked.connect(self._start_transcription)
        self.history_button.clicked.connect(self.show_history)
        self.models_button.clicked.connect(self._open_preferences)
        self.settings_button.clicked.connect(self._open_preferences)

        layout.addStretch(1)

        pro = QFrame()
        pro.setStyleSheet(
            f"""
            QFrame {{
                background: {PANEL};
                border: 1px solid #ffe2d2;
                border-radius: 14px;
            }}
            """
        )
        pro_layout = QVBoxLayout(pro)
        pro_layout.setContentsMargins(16, 15, 16, 15)
        pro_layout.setSpacing(8)

        pro_title = QLabel("♛  Lírico AI Pro")
        pro_title.setStyleSheet(f"font-weight: 700; color: {ORANGE}; font-size: 14px;")
        pro_copy = QLabel("Mais transcrições, modelos\ne recursos avançados.")
        pro_copy.setStyleSheet("color: #667085; font-size: 11px; line-height: 1.35;")
        pro_button = QPushButton("Fazer upgrade")
        pro_button.setCursor(Qt.CursorShape.PointingHandCursor)
        pro_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {ORANGE};
                color: white;
                border: 0;
                border-radius: 9px;
                padding: 10px 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background: {ORANGE_DARK}; }}
            """
        )
        pro_layout.addWidget(pro_title)
        pro_layout.addWidget(pro_copy)
        pro_layout.addWidget(pro_button)
        layout.addWidget(pro)

        return sidebar

    def _build_home_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page.setStyleSheet(f"background: {BG};")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(34, 28, 34, 34)
        outer.setSpacing(18)

        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        greeting = QLabel("⌂  Olá, bem-vindo(a) de volta!")
        greeting.setStyleSheet("font-size: 12px; color: #667085;")

        headline = QLabel('Transcrição <span style="color:#ff5a1f;">inteligente</span> de áudio e vídeo')
        headline.setTextFormat(Qt.TextFormat.RichText)
        headline.setStyleSheet("font-size: 30px; font-weight: 800; color: #101828;")

        sub = QLabel("Transforme seus áudios e vídeos em texto com rapidez, precisão e o poder da IA.")
        sub.setStyleSheet("font-size: 14px; color: #667085;")

        header_text.addWidget(greeting)
        header_text.addWidget(headline)
        header_text.addWidget(sub)
        header.addLayout(header_text, 1)

        theme = QLabel("☼")
        theme.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme.setFixedSize(36, 36)
        theme.setStyleSheet("font-size: 20px; color: #667085;")
        header.addWidget(theme)

        avatar = QLabel("L")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(34, 34)
        avatar.setStyleSheet(
            f"background:{ORANGE}; color:white; border-radius:17px; font-weight:700;"
        )
        header.addWidget(avatar)

        profile = QLabel("Lírico AI ⌄")
        profile.setStyleSheet("font-size: 13px; color: #344054; font-weight: 600;")
        header.addWidget(profile)
        outer.addLayout(header)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._build_upload_card(), 2)
        top_row.addWidget(self._build_feature_card(), 1)
        outer.addLayout(top_row)

        lower_row = QHBoxLayout()
        lower_row.setSpacing(16)
        lower_row.addWidget(self._build_preview_card(), 2)

        info_col = QVBoxLayout()
        info_col.setSpacing(14)
        info_col.addWidget(self._build_info_card())
        info_col.addWidget(self._build_export_card())
        lower_row.addLayout(info_col, 1)

        outer.addLayout(lower_row)
        outer.addStretch(1)

        scroll.setWidget(page)
        return scroll

    def _build_upload_card(self) -> QWidget:
        card = Card()
        card.setMinimumHeight(260)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cloud = QLabel("↥")
        cloud.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cloud.setFixedSize(72, 72)
        cloud.setStyleSheet(
            f"""
            QLabel {{
                background: #fff1e9;
                color: {ORANGE};
                border-radius: 36px;
                font-size: 34px;
                font-weight: 700;
            }}
            """
        )
        layout.addWidget(cloud, 0, Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Arraste seu arquivo aqui")
        title.setStyleSheet("font-size: 17px; font-weight: 750; color: #101828;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        formats = QLabel("Suporta MP3, M4A, WAV, MP4, MOV e mais.")
        formats.setStyleSheet("font-size: 12px; color: #98a2b3;")
        formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(formats)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        select = QPushButton("▣  Selecionar arquivo")
        select.setCursor(Qt.CursorShape.PointingHandCursor)
        select.setMinimumHeight(44)
        select.setStyleSheet(
            f"""
            QPushButton {{
                background: {ORANGE};
                color: white;
                border: 0;
                border-radius: 11px;
                padding: 0 22px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background: {ORANGE_DARK}; }}
            """
        )
        select.clicked.connect(self.on_select_file)

        record = QPushButton("♩  Gravar ao vivo")
        record.setCursor(Qt.CursorShape.PointingHandCursor)
        record.setMinimumHeight(44)
        record.setStyleSheet(
            f"""
            QPushButton {{
                background: white;
                color: {ORANGE};
                border: 1px solid #ffd3be;
                border-radius: 11px;
                padding: 0 22px;
                font-weight: 650;
            }}
            QPushButton:hover {{ background: #fff7f2; }}
            """
        )
        record.clicked.connect(self.on_record)

        buttons.addStretch(1)
        buttons.addWidget(select)
        buttons.addWidget(record)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        hint = QLabel("Você também pode soltar arquivos diretamente nesta janela.")
        hint.setStyleSheet("font-size: 11px; color: #b0b7c3;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        return card

    def _build_feature_card(self) -> QWidget:
        card = Card()
        card.setMinimumHeight(260)
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background: {PANEL};
                border: 1px solid #f3e6df;
                border-radius: 16px;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(11)

        icons = QLabel("▤   →   ▣   →   ▶")
        icons.setStyleSheet(f"font-size: 22px; color: {ORANGE};")
        layout.addWidget(icons)

        title = QLabel("Áudio ou vídeo, sem complicação")
        title.setStyleSheet("font-size: 15px; font-weight: 750; color: #101828;")
        layout.addWidget(title)

        copy = QLabel("Transcreva reuniões, aulas, entrevistas,\npodcasts e muito mais.")
        copy.setStyleSheet("font-size: 12px; color: #667085;")
        layout.addWidget(copy)

        for text in (
            "Alta precisão com IA",
            "Suporte a múltiplos formatos",
            "Identificação de falantes",
            "Exportação em vários formatos",
        ):
            item = QLabel(f"●  {text}")
            item.setStyleSheet(f"font-size: 12px; color: #667085;")
            layout.addWidget(item)

        layout.addStretch(1)
        return card

    def _build_preview_card(self) -> QWidget:
        card = Card()
        card.setMinimumHeight(350)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()
        title = QLabel("▤  Prévia da transcrição")
        title.setStyleSheet("font-size: 14px; font-weight: 750; color: #101828;")
        edit = QPushButton("✎  Editar")
        edit.setStyleSheet(
            f"background:white; border:1px solid {BORDER}; border-radius:8px; padding:6px 10px; color:#667085;"
        )
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(edit)
        layout.addLayout(top)

        rows = (
            ("00:00", "Olá, pessoal! Bom dia a todos. Hoje vamos conversar sobre como a inteligência artificial está transformando a forma como trabalhamos."),
            ("00:12", "Nos últimos anos, vimos um grande avanço nas ferramentas de IA, que ajudam a automatizar tarefas e aumentar a nossa produtividade."),
            ("00:27", "Mas é importante lembrar que a tecnologia é apenas uma ferramenta. O mais importante continua sendo o fator humano."),
            ("00:45", "O Lírico AI ajuda a economizar tempo transcrevendo áudios, reuniões, aulas e entrevistas."),
            ("01:03", "O objetivo é simples: transformar voz em texto com uma experiência clara, rápida e organizada."),
        )

        for stamp, text in rows:
            row = QHBoxLayout()
            badge = QLabel(stamp)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedWidth(48)
            badge.setStyleSheet(
                f"background:#fff0e8; color:{ORANGE}; border-radius:9px; padding:4px; font-size:10px; font-weight:650;"
            )
            body = QLabel(text)
            body.setWordWrap(True)
            body.setStyleSheet("font-size: 11px; color: #475467;")
            row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
            row.addWidget(body, 1)
            layout.addLayout(row)

        layout.addStretch(1)

        player = QHBoxLayout()
        play = QLabel("▶")
        play.setAlignment(Qt.AlignmentFlag.AlignCenter)
        play.setFixedSize(36, 36)
        play.setStyleSheet(
            f"background:{ORANGE}; color:white; border-radius:18px; font-size:13px;"
        )
        time = QLabel("00:00 / 01:28")
        time.setStyleSheet("font-size: 11px; color: #667085;")
        wave = QLabel("▁▂▅▇▃▆▂▅▇▃▂▆▃▅▇▂▃▁▅▇▆▃▂▁▂▃")
        wave.setStyleSheet(f"font-size: 16px; color: {ORANGE}; letter-spacing: 1px;")
        speed = QLabel("1×")
        speed.setStyleSheet("font-size: 10px; color:#667085;")
        player.addWidget(play)
        player.addWidget(time)
        player.addWidget(wave, 1)
        player.addWidget(speed)
        layout.addLayout(player)

        return card

    def _build_info_card(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(9)

        title = QLabel("▤  Informações do arquivo")
        title.setStyleSheet("font-size: 14px; font-weight: 750;")
        layout.addWidget(title)
        layout.addSpacing(4)

        for label, value in (
            ("Nome", "Selecione um arquivo para começar"),
            ("Tipo", "Áudio ou vídeo"),
            ("Idioma", "Português (Brasil)"),
            ("Duração", "—"),
            ("Status", "Pronto para transcrever"),
        ):
            row = QHBoxLayout()
            left = QLabel(label)
            left.setStyleSheet("font-size: 11px; color:#98a2b3;")
            right = QLabel(value)
            right.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.setStyleSheet(
                f"font-size: 11px; color:{GREEN if label == 'Status' else '#475467'};"
            )
            row.addWidget(left)
            row.addStretch(1)
            row.addWidget(right)
            layout.addLayout(row)

        return card

    def _build_export_card(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title = QLabel("⇧  Exportar transcrição")
        title.setStyleSheet("font-size: 14px; font-weight: 750;")
        subtitle = QLabel("Abra uma transcrição concluída para exportar.")
        subtitle.setStyleSheet("font-size: 10px; color:#98a2b3;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        row = QHBoxLayout()
        for name in ("TXT", "PDF", "DOCX"):
            button = QPushButton(name)
            button.setEnabled(False)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: white;
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 7px 12px;
                    color: #98a2b3;
                    font-weight: 650;
                }}
                """
            )
            row.addWidget(button)
        layout.addLayout(row)
        return card

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(16)

        title = QLabel("Histórico de transcrições")
        title.setStyleSheet("font-size: 27px; font-weight: 800; color:#101828;")
        subtitle = QLabel("Acompanhe, abra e organize todas as transcrições feitas no Lírico AI.")
        subtitle.setStyleSheet("font-size: 13px; color:#667085;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        wrapper = Card()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(8, 8, 8, 8)
        wrapper_layout.addWidget(self.history_widget)
        layout.addWidget(wrapper, 1)

        return page

    def _set_active(self, active: QToolButton):
        for button in (
            self.home_button,
            self.transcribe_button,
            self.history_button,
            self.models_button,
            self.settings_button,
        ):
            button.setChecked(button is active)

    def show_home(self):
        self.stack.setCurrentIndex(0)
        self._set_active(self.home_button)

    def show_history(self):
        self.stack.setCurrentIndex(1)
        self._set_active(self.history_button)

    def _start_transcription(self):
        self.stack.setCurrentIndex(0)
        self._set_active(self.transcribe_button)
        self.on_select_file()

    def _open_preferences(self):
        self.on_preferences()
