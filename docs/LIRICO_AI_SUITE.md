# Lírico AI Suite

Este diretório inicia o segundo aplicativo do projeto.

## Separação de produtos

- O transcritor existente continua no pacote `buzz` e não é alterado por esta etapa.
- O novo aplicativo vive no pacote `lirico_ai`.
- O objetivo é reutilizar a capacidade de transcrição existente por uma camada de integração, sem duplicar o motor.
- A IA local é tratada por uma interface `AIEngine`, permitindo trocar o runtime no futuro.

## IA local embarcada

A implementação inicial usa um adaptador `EmbeddedLlamaEngine` preparado para
iniciar um `llama-server` do llama.cpp distribuído junto com o aplicativo.

Estrutura esperada no pacote final:

```
runtime/
  llama/
    windows/llama-server.exe
    macos/llama-server
    linux/llama-server
models/
  lirico-default.gguf
```

O processo é iniciado pelo próprio Lírico, sem exigir Ollama instalado.

## Próximas etapas

1. Empacotar os binários adequados do llama.cpp por plataforma.
2. Definir e validar o modelo GGUF padrão e sua licença.
3. Criar o adaptador estável para reutilizar a transcrição do pacote `buzz`.
4. Implementar geração de aula, resumo, questões e flashcards.
5. Implementar biblioteca local/RAG.
6. Adicionar pesquisa web opcional com autorização explícita do usuário.
7. Criar pipelines de build separados para o transcritor e para o Lírico AI Suite.

## Execução de desenvolvimento

```bash
python -m lirico_ai
```


## Etapa 2 implementada

- Modelo padrão inicial definido: Qwen3 8B Q4_K_M.
- Manifesto local do modelo criado.
- Script Windows criado para instalar o llama.cpp e o modelo no diretório do Lírico.
- Tela "Gerar aula completa" conectada ao motor local.
- Geração executada em thread separada para não bloquear a interface.
- O motor continua preso a 127.0.0.1 e é encerrado pelo aplicativo.
