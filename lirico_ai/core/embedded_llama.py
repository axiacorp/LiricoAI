from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from pathlib import Path

import requests

from lirico_ai.core.ai_engine import AIEngine, GenerationRequest


class EmbeddedLlamaEngine(AIEngine):
    """Executa um llama.cpp empacotado junto com o Lírico.

    O usuário não instala nem interage com Ollama. O processo local é iniciado
    e encerrado pelo próprio Lírico e escuta somente em 127.0.0.1.
    """

    def __init__(
        self,
        runtime_path: Path,
        model_path: Path,
        host: str = "127.0.0.1",
        port: int = 18431,
    ) -> None:
        self.runtime_path = runtime_path
        self.model_path = model_path
        self.host = host
        self.port = port
        self._process: subprocess.Popen | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def is_available(self) -> bool:
        return self.runtime_path.exists() and self.model_path.exists()

    def _port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((self.host, self.port)) == 0

    def start(self) -> None:
        if self._process and self._process.poll() is None:
            return
        if not self.is_available():
            raise FileNotFoundError(
                "Runtime ou modelo local do Lírico AI não encontrado."
            )
        if self._port_in_use():
            raise RuntimeError(
                f"A porta local {self.port} já está em uso."
            )

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        self._process = subprocess.Popen(
            [
                str(self.runtime_path),
                "--model",
                str(self.model_path),
                "--host",
                self.host,
                "--port",
                str(self.port),
                "--ctx-size",
                "8192",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )

        deadline = time.time() + 30
        while time.time() < deadline:
            if self._process.poll() is not None:
                raise RuntimeError("O motor local encerrou durante a inicialização.")
            try:
                response = requests.get(f"{self.base_url}/health", timeout=0.5)
                if response.ok:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.25)

        self.stop()
        raise TimeoutError("Tempo excedido ao iniciar o motor local do Lírico AI.")

    def stop(self) -> None:
        if not self._process:
            return
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

    def generate(self, request: GenerationRequest) -> str:
        self.start()
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]
