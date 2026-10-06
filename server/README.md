# Lírico AI — servidor local de transcrição

Primeira prova de conceito web usando o próprio Mac como servidor de transcrição.

## Fluxo

Navegador -> upload -> backend local -> OpenAI Whisper -> resultado no navegador.

## Mac

1. Abra a pasta `server`.
2. Execute `start_mac.command`.
3. Na primeira execução o ambiente Python e as dependências serão instalados.
4. O navegador abrirá em `http://127.0.0.1:8765`.
5. Comece com o modelo **Whisper Base**.

Cada modelo é baixado apenas na primeira utilização e fica em cache no Mac.

O backend tenta usar Apple MPS quando disponível. Se o Whisper/Torch falhar no MPS, a mesma transcrição é repetida automaticamente pela CPU para evitar perda do teste.

Para forçar CPU:

```bash
LIRICO_DEVICE=cpu ./start_mac.command
```
