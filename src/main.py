"""Transmissao de 2 cameras Yoosee para a Twitch (lado a lado, em tempo real)."""

import shutil
import subprocess
import sys
import time

from .config import load_config
from .ffmpeg import build_command, default_font, has_drawtext


def _now() -> str:
    return time.strftime("%H:%M:%S")


def main() -> None:
    if not shutil.which("ffmpeg"):
        print("ERRO: FFmpeg nao encontrado. Instale e adicione ao PATH (veja README).")
        sys.exit(1)

    config = load_config()
    use_hw = config.mac_hw_acceleration and sys.platform == "darwin"

    drawtext_available = has_drawtext()
    if not drawtext_available and any(camera.caption for camera in config.cameras):
        print("Aviso: este FFmpeg nao suporta legendas; transmitindo sem elas. "
              "(No Mac: brew install ffmpeg-full para ter legendas)")
    font = default_font() if drawtext_available else None

    attempt = 0
    while True:
        attempt += 1
        print(f"[{_now()}] Iniciando transmissao (tentativa {attempt})...")
        start_time = time.time()
        try:
            exit_code = subprocess.run(build_command(config, use_hw, font)).returncode
        except KeyboardInterrupt:
            print("\nTransmissao encerrada pelo usuario.")
            break
        if use_hw and time.time() - start_time < 15:
            use_hw = False
            print("Aviso: aceleracao por hardware falhou; usando o processador.")
        if time.time() - start_time > 60:
            attempt = 0
        retry_delay = min(5 * max(attempt, 1), 60)
        print(f"[{_now()}] Transmissao caiu (codigo {exit_code}). "
              f"Reconectando em {retry_delay}s... (Ctrl+C para sair)")
        try:
            time.sleep(retry_delay)
        except KeyboardInterrupt:
            print("\nTransmissao encerrada pelo usuario.")
            break


if __name__ == "__main__":
    main()
