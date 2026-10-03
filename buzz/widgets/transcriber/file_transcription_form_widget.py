from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
)

from buzz.locale import _
from buzz.model_loader import (
    ModelType,
    WhisperModelSize,
    TranscriptionModel,
)
from buzz.settings.settings import Settings
from buzz.transcriber.transcriber import (
    TranscriptionOptions,
    FileTranscriptionOptions,
    OutputFormat,
)
from buzz.widgets.transcriber.transcription_options_group_box import (
    TranscriptionOptionsGroupBox,
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

        layout = QVBoxLayout(self)

        simple_form = QFormLayout()

        self.mode_combo_box = QComboBox(self)
        self.mode_combo_box.addItem("Automático (recomendado)", "auto")
        self.mode_combo_box.addItem("Offline", "offline")
        self.mode_combo_box.addItem("Avançado", "advanced")
        saved_mode = self.settings.value(
            Settings.Key.FILE_TRANSCRIBER_UI_MODE, "auto"
        )
        mode_index = self.mode_combo_box.findData(saved_mode)
        self.mode_combo_box.setCurrentIndex(mode_index if mode_index >= 0 else 0)
        self.mode_combo_box.currentIndexChanged.connect(self.on_mode_changed)
        simple_form.addRow("Modo:", self.mode_combo_box)

        self.offline_engine_combo_box = QComboBox(self)
        self.offline_engine_combo_box.addItem("Whisper.cpp", ModelType.WHISPER_CPP.value)
        self.offline_engine_combo_box.addItem("OpenAI Whisper local", ModelType.WHISPER.value)
        self.offline_engine_combo_box.addItem("Faster Whisper", ModelType.FASTER_WHISPER.value)
        saved_offline_engine = self.settings.value(
            Settings.Key.FILE_TRANSCRIBER_OFFLINE_ENGINE,
            ModelType.WHISPER_CPP.value,
        )
        offline_engine_index = self.offline_engine_combo_box.findData(saved_offline_engine)
        self.offline_engine_combo_box.setCurrentIndex(
            offline_engine_index if offline_engine_index >= 0 else 0
        )
        self.offline_engine_combo_box.currentIndexChanged.connect(
            self.on_offline_engine_changed
        )
        simple_form.addRow("Motor offline:", self.offline_engine_combo_box)

        self.offline_model_size_combo_box = QComboBox(self)
        for size in (
            WhisperModelSize.TINY,
            WhisperModelSize.BASE,
            WhisperModelSize.SMALL,
            WhisperModelSize.MEDIUM,
            WhisperModelSize.LARGEV2,
            WhisperModelSize.LARGEV3,
            WhisperModelSize.LARGEV3TURBO,
        ):
            self.offline_model_size_combo_box.addItem(size.value, size.value)
        saved_offline_size = self.settings.value(
            Settings.Key.FILE_TRANSCRIBER_OFFLINE_MODEL_SIZE,
            WhisperModelSize.LARGEV3TURBO.value,
        )
        offline_size_index = self.offline_model_size_combo_box.findData(saved_offline_size)
        self.offline_model_size_combo_box.setCurrentIndex(
            offline_size_index if offline_size_index >= 0 else
            self.offline_model_size_combo_box.findData(WhisperModelSize.LARGEV3TURBO.value)
        )
        self.offline_model_size_combo_box.currentIndexChanged.connect(
            self.on_offline_model_size_changed
        )
        simple_form.addRow("Modelo offline:", self.offline_model_size_combo_box)

        self.content_type_combo_box = QComboBox(self)
        self.content_type_combo_box.addItem("Geral", "general")
        self.content_type_combo_box.addItem("Aula", "class")
        self.content_type_combo_box.addItem("Aula médica", "medical_class")
        self.content_type_combo_box.addItem("Reunião", "meeting")
        self.content_type_combo_box.addItem("Entrevista", "interview")
        saved_content_type = self.settings.value(
            Settings.Key.FILE_TRANSCRIBER_CONTENT_TYPE, "general"
        )
        content_index = self.content_type_combo_box.findData(saved_content_type)
        self.content_type_combo_box.setCurrentIndex(
            content_index if content_index >= 0 else 0
        )
        self.content_type_combo_box.currentIndexChanged.connect(
            self.on_content_type_changed
        )
        simple_form.addRow("Tipo de conteúdo:", self.content_type_combo_box)

        self.mode_status_label = QLabel(self)
        self.mode_status_label.setWordWrap(True)
        simple_form.addRow("", self.mode_status_label)

        layout.addLayout(simple_form)

        self._apply_mode_to_options(emit=False)

        self.transcription_options_group_box = TranscriptionOptionsGroupBox(
            default_transcription_options=self.transcription_options, parent=self
        )
        self.transcription_options_group_box.transcription_options_changed.connect(
            self.on_transcription_options_changed
        )
        layout.addWidget(self.transcription_options_group_box)

        self.word_level_timings_checkbox = QCheckBox(_("Word-level timings"))
        self.word_level_timings_checkbox.setChecked(
            self.transcription_options.word_level_timings
        )
        self.word_level_timings_checkbox.stateChanged.connect(
            self.on_word_level_timings_changed
        )

        file_transcription_layout = QFormLayout()
        file_transcription_layout.addRow("", self.word_level_timings_checkbox)

        self.extract_speech_checkbox = QCheckBox(_("Extract speech"))
        self.extract_speech_checkbox.setChecked(
            self.transcription_options.extract_speech
        )
        self.extract_speech_checkbox.stateChanged.connect(
            self.on_extract_speech_changed
        )

        file_transcription_layout.addRow("", self.extract_speech_checkbox)

        export_format_layout = QHBoxLayout()
        for output_format in OutputFormat:
            export_format_checkbox = QCheckBox(
                f"{output_format.value.upper()}", parent=self
            )
            export_format_checkbox.setChecked(
                output_format in self.file_transcription_options.output_formats
            )
            export_format_checkbox.stateChanged.connect(
                self.get_on_checkbox_state_changed_callback(output_format)
            )
            export_format_layout.addWidget(export_format_checkbox)

        file_transcription_layout.addRow(_("Export:"), export_format_layout)

        layout.addLayout(file_transcription_layout)
        self.setLayout(layout)

        self._apply_content_prompt(emit=False)
        self._update_simple_mode_visibility()

    def _current_mode(self) -> str:
        return self.mode_combo_box.currentData() or "auto"

    def _apply_mode_to_options(self, emit: bool = True):
        mode = self._current_mode()

        if mode == "auto":
            # Automatic mode is intentionally OpenAI-only. Never silently fall
            # back to a local Whisper model: users choosing the recommended mode
            # must get the same AI transcription pipeline every time.
            self.transcription_options.model = TranscriptionModel(
                model_type=ModelType.OPEN_AI_WHISPER_API,
                whisper_model_size=None,
            )
            if self.transcription_options.openai_access_token:
                self.mode_status_label.setText(
                    "IA OpenAI ativada. O Lírico AI enviará o áudio para o "
                    "modelo de transcrição da OpenAI."
                )
            else:
                self.mode_status_label.setText(
                    "IA OpenAI obrigatória. Configure uma chave da OpenAI para "
                    "iniciar a transcrição."
                )
        elif mode == "offline":
            try:
                offline_engine = ModelType(
                    self.offline_engine_combo_box.currentData()
                    or ModelType.WHISPER_CPP.value
                )
            except ValueError:
                offline_engine = ModelType.WHISPER_CPP
            try:
                offline_size = WhisperModelSize(
                    self.offline_model_size_combo_box.currentData()
                    or WhisperModelSize.LARGEV3TURBO.value
                )
            except ValueError:
                offline_size = WhisperModelSize.LARGEV3TURBO

            self.transcription_options.model = TranscriptionModel(
                model_type=offline_engine,
                whisper_model_size=offline_size,
            )
            self.mode_status_label.setText(
                f"Modo offline: {offline_engine.value} · {offline_size.value}. "
                "O áudio permanece no computador."
            )
        else:
            self.mode_status_label.setText(
                "Modo avançado: escolha manualmente modelo, idioma e demais opções."
            )

        ui_locale = self.settings.value(Settings.Key.UI_LOCALE, "")
        if not self.transcription_options.language and str(ui_locale).startswith("pt"):
            self.transcription_options.language = "pt"

        if emit:
            self.transcription_options_changed.emit(
                (self.transcription_options, self.file_transcription_options)
            )

    def _apply_content_prompt(self, emit: bool = True):
        content_type = self.content_type_combo_box.currentData() or "general"
        prompt = CONTENT_PROMPTS.get(content_type, "")
        if content_type != "general" or self._current_mode() != "advanced":
            self.transcription_options.initial_prompt = prompt

        if emit:
            self.transcription_options_changed.emit(
                (self.transcription_options, self.file_transcription_options)
            )

    def _update_simple_mode_visibility(self):
        mode = self._current_mode()
        advanced = mode == "advanced"
        offline = mode == "offline"
        self.offline_engine_combo_box.setVisible(offline)
        self.offline_model_size_combo_box.setVisible(offline)
        self.transcription_options_group_box.setVisible(advanced)
        self.word_level_timings_checkbox.setVisible(advanced)
        self.extract_speech_checkbox.setVisible(advanced)

    def on_mode_changed(self, _index: int):
        self.settings.set_value(
            Settings.Key.FILE_TRANSCRIBER_UI_MODE, self._current_mode()
        )
        self._apply_mode_to_options()
        self._update_simple_mode_visibility()

    def on_offline_engine_changed(self, _index: int):
        self.settings.set_value(
            Settings.Key.FILE_TRANSCRIBER_OFFLINE_ENGINE,
            self.offline_engine_combo_box.currentData(),
        )
        if self._current_mode() == "offline":
            self._apply_mode_to_options()

    def on_offline_model_size_changed(self, _index: int):
        self.settings.set_value(
            Settings.Key.FILE_TRANSCRIBER_OFFLINE_MODEL_SIZE,
            self.offline_model_size_combo_box.currentData(),
        )
        if self._current_mode() == "offline":
            self._apply_mode_to_options()

    def on_content_type_changed(self, _index: int):
        content_type = self.content_type_combo_box.currentData() or "general"
        self.settings.set_value(
            Settings.Key.FILE_TRANSCRIBER_CONTENT_TYPE, content_type
        )
        self._apply_content_prompt()

    def on_transcription_options_changed(
        self, transcription_options: TranscriptionOptions
    ):
        self.transcription_options = transcription_options
        self.transcription_options_changed.emit(
            (self.transcription_options, self.file_transcription_options)
        )
        if self.transcription_options.openai_access_token != "":
            self.openai_access_token_changed.emit(
                self.transcription_options.openai_access_token
            )

    def on_word_level_timings_changed(self, value: int):
        self.transcription_options.word_level_timings = (
            value == Qt.CheckState.Checked.value
        )

        self.transcription_options_changed.emit(
            (self.transcription_options, self.file_transcription_options)
        )

    def on_extract_speech_changed(self, value: int):
        self.transcription_options.extract_speech = (
            value == Qt.CheckState.Checked.value
        )

        self.transcription_options_changed.emit(
            (self.transcription_options, self.file_transcription_options)
        )

    def get_on_checkbox_state_changed_callback(self, output_format: OutputFormat):
        def on_checkbox_state_changed(state: int):
            if state == Qt.CheckState.Checked.value:
                self.file_transcription_options.output_formats.add(output_format)
            elif state == Qt.CheckState.Unchecked.value:
                self.file_transcription_options.output_formats.remove(output_format)

            self.transcription_options_changed.emit(
                (self.transcription_options, self.file_transcription_options)
            )

        return on_checkbox_state_changed
