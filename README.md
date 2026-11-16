# Transmissão Twitch – Câmeras Yoosee

Transmite 2 câmeras Yoosee (RTSP) lado a lado, em tempo real, para a Twitch usando FFmpeg.
Reconecta sozinho se a transmissão cair e usa aceleração por hardware no Mac (Apple Silicon).

## Requisitos

- Python 3.8+
- FFmpeg no PATH
  - macOS: `brew install ffmpeg` (ou `brew install ffmpeg-full` para ter legendas)
  - Windows: https://www.gyan.dev/ffmpeg/builds/
  - Linux: `sudo apt install ffmpeg`

## Configuração

```bash
cp .env.example .env
```

Edite o `.env` com os IPs/senhas das câmeras e a chave de transmissão da Twitch.
O `.env` está no `.gitignore` e **nunca** deve ser enviado ao git.

## Uso

Sem instalar:

```bash
python transmitir_twitch.py
```

Ou instalando como comando:

```bash
pip install -e .
transmitir-twitch
```

Pressione `Ctrl+C` para encerrar.

## Estrutura

```
.
├── src/
│   ├── config.py      # leitura do .env / variáveis de ambiente
│   ├── ffmpeg.py      # montagem do comando FFmpeg
│   └── main.py        # loop de transmissão e reconexão
├── transmitir_twitch.py  # atalho para rodar sem instalar
├── .env.example
└── pyproject.toml
```
