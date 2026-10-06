from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QButtonGroup, QFrame
)

from buzz.model_loader import ModelType, WhisperModelSize, TranscriptionModel
from buzz.settings.settings import Settings
from buzz.transcriber.transcriber import (
    TranscriptionOptions, FileTranscriptionOptions, Task
)


CONTENT_PROMPTS = {
    "general": "",
    "class": (
        "Aula em português brasileiro. Transcreva fielmente o que foi falado, "
        "preservando termos técnicos, nomes próprios, números, doses e unidades. "
        "Não invente conteúdo quando o áudio estiver incerto."
    ),
    "medical_class": (
        "Aula médica em português brasileiro. Transcreva fielmente o áudio, "
        "preservando terminologia médica, nomes de medicamentos, doses, vias de "
        "administração, siglas, exames, anatomia e condutas. Corrija apenas o "
        "reconhecimento de fala com forte apoio fonético e contextual; não invente "
        "informações quando o áudio estiver incerto."
    ),
    "meeting": (
        "Reunião em português brasileiro. Preserve nomes, decisões, números, datas "
        "e termos profissionais exatamente como forem falados."
    ),
    "interview": (
        "Entrevista em português brasileiro. Preserve as falas com fidelidade, "
        "incluindo nomes próprios, números e termos específicos do assunto."
    ),
}

MODEL_OPTIONS = [
    ("Whisper.cpp Tiny — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.TINY, "", "Leve e rápido."),
    ("Whisper.cpp Base — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.BASE, "", "Modelo local leve."),
    ("Whisper.cpp Small — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.SMALL, "", "Bom equilíbrio entre velocidade e qualidade."),
    ("Whisper.cpp Medium — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.MEDIUM, "", "Maior precisão, com maior uso de memória."),
    ("Whisper.cpp Large V2 — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.LARGEV2, "", "Modelo Whisper grande."),
    ("Whisper.cpp Large V3 — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.LARGEV3, "", "Alta precisão."),
    ("Whisper.cpp Large V3 Turbo — baixado no primeiro uso", ModelType.WHISPER_CPP, WhisperModelSize.LARGEV3TURBO, "", "Alta qualidade com melhor velocidade."),

    ("OpenAI Whisper local Tiny — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.TINY, "", "Implementação local original do Whisper."),
    ("OpenAI Whisper local Base — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.BASE, "", "Whisper local Base."),
    ("OpenAI Whisper local Small — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.SMALL, "", "Whisper local Small."),
    ("OpenAI Whisper local Medium — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.MEDIUM, "", "Whisper local Medium."),
    ("OpenAI Whisper local Large V2 — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.LARGEV2, "", "Whisper local Large V2."),
    ("OpenAI Whisper local Large V3 — baixado no primeiro uso", ModelType.WHISPER, WhisperModelSize.LARGEV3, "", "Whisper local Large V3."),

    ("Faster Whisper Tiny — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.TINY, "", "Whisper otimizado com CTranslate2."),
    ("Faster Whisper Base — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.BASE, "", "Faster Whisper Base."),
    ("Faster Whisper Small — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.SMALL, "", "Faster Whisper Small."),
    ("Faster Whisper Medium — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.MEDIUM, "", "Faster Whisper Medium."),
    ("Faster Whisper Large V2 — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.LARGEV2, "", "Faster Whisper Large V2."),
    ("Faster Whisper Large V3 — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.LARGEV3, "", "Faster Whisper Large V3."),
    ("Faster Whisper Large V3 Turbo — baixado no primeiro uso", ModelType.FASTER_WHISPER, WhisperModelSize.LARGEV3TURBO, "", "Faster Whisper Large V3 Turbo."),

    ("Hugging Face Parakeet — instalado sob demanda", ModelType.HUGGING_FACE, None, "nvidia/parakeet-tdt-0.6b-v3", "Baixado na primeira utilização e executado localmente."),
    ("Hugging Face MMS — instalado sob demanda", ModelType.HUGGING_FACE, None, "facebook/mms-1b-all", "Modelo multilíngue baixado na primeira utilização."),
    ("Hugging Face VibeVoice ASR — instalado sob demanda", ModelType.HUGGING_FACE, None, "microsoft/VibeVoice-ASR-HF", "Baixado na primeira utilização e executado localmente."),
    ("Hugging Face Qwen ASR — instalado sob demanda", ModelType.HUGGING_FACE, None, "Qwen/Qwen3-ASR-1.7B-hf", "Baixado na primeira utilização e executado localmente."),
]


class FileTranscriptionFormWidget(QWidget):
    openai_access_token_changed = pyqtSignal(str)
    transcription_options_changed = pyqtSignal(tuple)

    def __init__(
        self,
        transcription_options: TranscriptionOptions,
        file_transcription_options: FileTranscriptionOptions,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.settings = Settings()
        self.transcription_options = transcription_options
        self.file_transcription_options = file_transcription_options
        self.content_type = self.settings.value(
            Settings.Key.FILE_TRANSCRIBER_CONTENT_TYPE, "general"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self.model_combo_box = QComboBox(self)
        for label, model_type, size, hf_id, description in MODEL_OPTIONS:
            self.model_combo_box.addItem(
                label,
                (model_type.value, size.value if size else None, hf_id, description),
            )
        current_model = self.transcription_options.model
        current_index = next(
            (
                i for i, item in enumerate(MODEL_OPTIONS)
                if item[1] == current_model.model_type
                and item[2] == current_model.whisper_model_size
                and (item[3] or "") == (current_model.hugging_face_model_id or "")
            ),
            -1,
        )
        default_index = next(
            (
                i for i, item in enumerate(MODEL_OPTIONS)
                if item[1] == ModelType.WHISPER_CPP
                and item[2] == WhisperModelSize.LARGEV3TURBO
            ),
            0,
        )
        self.model_combo_box.setCurrentIndex(
            current_index if current_index >= 0 else default_index
        )
        self.model_combo_box.currentIndexChanged.connect(self.on_model_changed)
        root.addWidget(self._field("Modelo de transcrição", self.model_combo_box))

        self.language_combo_box = QComboBox(self)
        for label, code in [
            ("Português (Brasil)", "pt"),
            ("Detectar automaticamente", None),
            ("Inglês", "en"),
            ("Espanhol", "es"),
            ("Francês", "fr"),
            ("Alemão", "de"),
            ("Italiano", "it"),
        ]:
            self.language_combo_box.addItem(label, code)
        self.language_combo_box.currentIndexChanged.connect(self.on_language_changed)
        root.addWidget(self._field("Idioma do áudio", self.language_combo_box))

        self.result_combo_box = QComboBox(self)
        self.result_combo_box.addItem("Transcrever áudio", Task.TRANSCRIBE.value)
        self.result_combo_box.addItem("Traduzir para inglês", Task.TRANSLATE.value)
        self.result_combo_box.currentIndexChanged.connect(self.on_result_changed)
        root.addWidget(self._field("Resultado", self.result_combo_box))

        self.description_card = QFrame()
        self.description_card.setObjectName("modelDescription")
        desc_layout = QVBoxLayout(self.description_card)
        desc_layout.setContentsMargins(16, 13, 16, 13)
        self.description_title = QLabel()
        self.description_title.setObjectName("descriptionTitle")
        self.description_text = QLabel()
        self.description_text.setWordWrap(True)
        self.description_text.setObjectName("descriptionText")
        desc_layout.addWidget(self.description_title)
        desc_layout.addWidget(self.description_text)
        root.addWidget(self.description_card)

        content_label = QLabel("Tipo de conteúdo")
        content_label.setObjectName("fieldLabel")
        root.addWidget(content_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.content_group = QButtonGroup(self)
        self.content_group.setExclusive(True)
        for label, value in [
            ("Geral", "general"),
            ("Aula", "class"),
            ("Aula médica", "medical_class"),
            ("Reunião", "meeting"),
            ("Entrevista", "interview"),
        ]:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setObjectName("contentButton")
            button.setProperty("contentValue", value)
            if value == self.content_type:
                button.setChecked(True)
            button.clicked.connect(self.on_content_changed)
            self.content_group.addButton(button)
            buttons.addWidget(button)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self.medical_note = QFrame()
        self.medical_note.setObjectName("medicalNote")
        note_layout = QHBoxLayout(self.medical_note)
        note_layout.setContentsMargins(14, 10, 14, 10)
        note_layout.addWidget(QLabel("●"))
        note_text = QLabel(
            "Contexto médico aplicado   Preserva termos médicos, medicamentos, "
            "doses, vias, siglas e exames."
        )
        note_text.setWordWrap(True)
        note_layout.addWidget(note_text, 1)
        root.addWidget(self.medical_note)

        self.on_model_changed(self.model_combo_box.currentIndex())
        self.on_language_changed(self.language_combo_box.currentIndex())
        self.on_result_changed(self.result_combo_box.currentIndex())
        self._apply_content_prompt()
        self._refresh_medical_note()

        self.setStyleSheet("""
            QLabel#fieldLabel { font-weight: 700; color: #2a2522; }
            QComboBox {
                min-height: 38px; padding: 4px 10px; border: 1px solid #ddd3cc;
                border-radius: 8px; background: white; color: #241f1c;
            }
            QFrame#modelDescription {
                background: #fbf9f7; border: 1px solid #e7ded7; border-radius: 10px;
            }
            QLabel#descriptionTitle { font-weight: 750; font-size: 15px; color: #2a2522; }
            QLabel#descriptionText { color: #7a7069; }
            QPushButton#contentButton {
                background: white; color: #342e2a; border: 1px solid #ddd3cc;
                border-radius: 8px; padding: 9px 14px;
            }
            QPushButton#contentButton:checked {
                background: #fff5ec; color: #e85f00; border: 1px solid #ff7a1a;
                font-weight: 700;
            }
            QFrame#medicalNote {
                background: #edf8f1; border: 1px solid #c8e9d2; border-radius: 8px;
                color: #254c32;
            }
        """)

    def _field(self, label_text: str, widget: QWidget) -> QWidget:
        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return wrapper

    def on_model_changed(self, _index: int):
        model_type_value, size_value, hf_id, description = self.model_combo_box.currentData()
        model_type = ModelType(model_type_value)
        size = WhisperModelSize(size_value) if size_value else None
        self.transcription_options.model = TranscriptionModel(
            model_type=model_type,
            whisper_model_size=size,
            hugging_face_model_id=hf_id,
        )
        self.description_title.setText(self.model_combo_box.currentText())
        self.description_text.setText(description)
        self._emit_change()

    def on_language_changed(self, _index: int):
        self.transcription_options.language = self.language_combo_box.currentData()
        self._emit_change()

    def on_result_changed(self, _index: int):
        self.transcription_options.task = Task(self.result_combo_box.currentData())
        self._emit_change()

    def on_content_changed(self):
        button = self.sender()
        if not isinstance(button, QPushButton):
            return
        self.content_type = button.property("contentValue") or "general"
        self.settings.set_value(
            Settings.Key.FILE_TRANSCRIBER_CONTENT_TYPE, self.content_type
        )
        self._apply_content_prompt()
        self._refresh_medical_note()
        self._emit_change()

    def _apply_content_prompt(self):
        self.transcription_options.initial_prompt = CONTENT_PROMPTS.get(
            self.content_type, ""
        )

    def _refresh_medical_note(self):
        self.medical_note.setVisible(self.content_type == "medical_class")

    def _emit_change(self):
        self.transcription_options_changed.emit(
            (self.transcription_options, self.file_transcription_options)
        )
