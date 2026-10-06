#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "========================================"
echo " Lírico AI — servidor local de teste"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 não foi encontrado neste Mac."
  echo "Instale Python 3 e tente novamente."
  read -n 1
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Preparando o ambiente pela primeira vez..."
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "Abrindo o Lírico AI no navegador..."
(sleep 2; open "http://127.0.0.1:8765") &
python -m uvicorn app:app --host 127.0.0.1 --port 8765
