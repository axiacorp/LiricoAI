import os

from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
)


FORMATS = {
    "MP3 (áudio)": (".mp3", ["-vn", "-codec:a", "libmp3lame", "-q:a", "2"]),
    "WAV (áudio)": (".wav", ["-vn", "-codec:a", "pcm_s16le"]),
    "M4A / AAC (áudio)": (".m4a", ["-vn", "-codec:a", "aac", "-b:a", "192k"]),
    "AAC (áudio)": (".aac", ["-vn", "-codec:a", "aac", "-b:a", "192k", "-f", "adts"]),
    "FLAC (áudio)": (".flac", ["-vn", "-codec:a", "flac"]),
    "OGG (áudio)": (".ogg", ["-vn", "-codec:a", "libvorbis", "-q:a", "5"]),
    "WMA (áudio)": (".wma", ["-vn", "-codec:a", "wmav2", "-b:a", "192k"]),
    "MP4 (áudio/vídeo)": (".mp4", ["-c:v", "mpeg4", "-q:v", "3", "-c:a", "aac", "-b:a", "192k"]),
}


class MediaConverterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Converter mídia")
        self.setMinimumWidth(560)

        self.process = QProcess(self)
        self.process.finished.connect(self.on_finished)
        self.process.readyReadStandardError.connect(self.on_stderr)

        self.input_edit = QLineEdit(self)
        self.output_edit = QLineEdit(self)

        browse_input = QPushButton("Selecionar arquivo", self)
        browse_input.clicked.connect(self.choose_input)

        browse_output = QPushButton("Escolher destino", self)
        browse_output.clicked.connect(self.choose_output)

        self.format_combo = QComboBox(self)
        for label in FORMATS:
            self.format_combo.addItem(label)
        self.format_combo.currentIndexChanged.connect(self.suggest_output)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_edit)
        input_row.addWidget(browse_input)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        output_row.addWidget(browse_output)

        form = QFormLayout()
        form.addRow("Arquivo de origem:", input_row)
        form.addRow("Converter para:", self.format_combo)
        form.addRow("Salvar como:", output_row)

        note = QLabel(
            "Conversão local e gratuita usando FFmpeg. "
            "Nenhum arquivo é enviado para a internet."
        )
        note.setWordWrap(True)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)

        self.convert_button = QPushButton("Converter", self)
        self.convert_button.clicked.connect(self.convert)

        close_button = QPushButton("Fechar", self)
        close_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_button)
        buttons.addWidget(self.convert_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addWidget(self.progress)
        layout.addLayout(buttons)

    def choose_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar mídia",
            "",
            "Mídia (*.mp3 *.wav *.m4a *.aac *.ogg *.flac *.wma *.mp4 *.mov *.mkv *.avi *.webm);;Todos os arquivos (*.*)",
        )
        if not path:
            return
        self.input_edit.setText(path)
        self.suggest_output()

    def suggest_output(self):
        source = self.input_edit.text().strip()
        if not source:
            return
        extension, _ = FORMATS[self.format_combo.currentText()]
        base, _ = os.path.splitext(source)
        self.output_edit.setText(base + "_convertido" + extension)

    def choose_output(self):
        extension, _ = FORMATS[self.format_combo.currentText()]
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar arquivo convertido",
            self.output_edit.text().strip(),
            f"Arquivo (*{extension})",
        )
        if path:
            if not path.lower().endswith(extension):
                path += extension
            self.output_edit.setText(path)

    def convert(self):
        source = self.input_edit.text().strip()
        target = self.output_edit.text().strip()

        if not source or not os.path.isfile(source):
            QMessageBox.warning(self, "Arquivo inválido", "Selecione um arquivo de origem válido.")
            return
        if not target:
            QMessageBox.warning(self, "Destino ausente", "Escolha onde salvar o arquivo convertido.")
            return

        _, format_args = FORMATS[self.format_combo.currentText()]
        args = ["-y", "-i", source, *format_args, target]

        self.convert_button.setEnabled(False)
        self.progress.setRange(0, 0)
        self.process.start("ffmpeg", args)

    def on_stderr(self):
        # Reading stderr continuously prevents FFmpeg from blocking on a full pipe.
        self.process.readAllStandardError()

    def on_finished(self, exit_code: int, _exit_status):
        self.progress.setRange(0, 1)
        self.convert_button.setEnabled(True)
        if exit_code == 0:
            self.progress.setValue(1)
            QMessageBox.information(
                self,
                "Conversão concluída",
                f"Arquivo salvo em:\n{self.output_edit.text().strip()}",
            )
        else:
            self.progress.setValue(0)
            QMessageBox.critical(
                self,
                "Falha na conversão",
                "O FFmpeg não conseguiu converter este arquivo/formato.",
            )
