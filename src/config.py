"""Carrega a configuracao a partir de variaveis de ambiente / arquivo .env."""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Camera:
    ip: str
    password: str
    username: str = "admin"
    caption: str = ""
    rotate_180: bool = False


@dataclass
class Config:
    cameras: List[Camera]
    twitch_stream_key: str
    twitch_server: str = "rtmp://live.twitch.tv/app"
    transport: str = "udp"             # Yoosee normalmente so aceita "udp"
    camera_quality: str = "onvif2"     # "onvif1" = alta | "onvif2" = baixa
    width_each: int = 960
    height_each: int = 540
    fps: int = 15
    video_bitrate: str = "2500k"
    mac_hw_acceleration: bool = True
    extras: dict = field(default_factory=dict)


def load_dotenv(path: Path) -> None:
    """Leitor simples de .env (sem dependencias). Nao sobrescreve variaveis ja definidas."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _parse_bool(value: Optional[str], default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "sim", "yes", "on")


def _fail(message: str) -> None:
    print(f"ERRO: {message}")
    sys.exit(1)


def load_config(env_file: Optional[Path] = None) -> Config:
    load_dotenv(env_file or Path.cwd() / ".env")
    env = os.environ

    cameras: List[Camera] = []
    for index in (1, 2):
        ip = env.get(f"CAMERA{index}_IP")
        password = env.get(f"CAMERA{index}_SENHA")
        if not ip or not password:
            _fail(f"defina CAMERA{index}_IP e CAMERA{index}_SENHA no arquivo .env (veja .env.example).")
        cameras.append(Camera(
            ip=ip,
            password=password,
            username=env.get(f"CAMERA{index}_USUARIO", "admin"),
            caption=env.get(f"CAMERA{index}_LEGENDA", f"Camera {index}"),
            rotate_180=_parse_bool(env.get(f"CAMERA{index}_GIRAR180"), False),
        ))

    stream_key = env.get("TWITCH_CHAVE", "")
    if not stream_key or "XXXX" in stream_key:
        _fail("defina TWITCH_CHAVE no arquivo .env (veja .env.example).")

    return Config(
        cameras=cameras,
        twitch_stream_key=stream_key,
        twitch_server=env.get("TWITCH_SERVIDOR", "rtmp://live.twitch.tv/app"),
        transport=env.get("TRANSPORTE", "udp"),
        camera_quality=env.get("QUALIDADE_CAMERA", "onvif2"),
        width_each=int(env.get("LARGURA_CADA", "960")),
        height_each=int(env.get("ALTURA_CADA", "540")),
        fps=int(env.get("FPS", "15")),
        video_bitrate=env.get("BITRATE_VIDEO", "2500k"),
        mac_hw_acceleration=_parse_bool(env.get("ACELERACAO_MAC"), True),
    )
