"""Montagem do comando FFmpeg (2 cameras lado a lado -> Twitch)."""

import os
import subprocess
from typing import List, Optional
from urllib.parse import quote

from .config import Camera, Config


def build_rtsp_url(camera: Camera, quality: str) -> str:
    password = quote(camera.password, safe="")
    return f"rtsp://{camera.username}:{password}@{camera.ip}:554/{quality}"


def default_font() -> Optional[str]:
    """Fonte para as legendas (drawtext). Retorna None se nao achar."""
    candidates = [
        "C\\:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for font_path in candidates:
        if os.path.exists(font_path.replace("\\:", ":")):
            return font_path
    return None


def has_drawtext() -> bool:
    """Verifica se o FFmpeg instalado tem o filtro de texto (legendas)."""
    try:
        output = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                                capture_output=True, text=True).stdout
        return " drawtext " in output
    except Exception:
        return False


def build_filters(config: Config, font: Optional[str]) -> str:
    filters = []
    for index, camera in enumerate(config.cameras):
        rotate = "hflip,vflip," if camera.rotate_180 else ""
        camera_filter = (
            f"[{index}:v]{rotate}scale={config.width_each}:{config.height_each}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={config.width_each}:{config.height_each}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={config.fps}"
        )
        if camera.caption and font:
            camera_filter += (
                f",drawtext=fontfile='{font}':text='{camera.caption}':x=15:y=15:"
                f"fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6"
            )
        filters.append(camera_filter + f"[v{index}]")
    filters.append("[v0][v1]hstack=inputs=2[out]")
    return ";".join(filters)


def build_command(config: Config, use_hw: bool, font: Optional[str]) -> List[str]:
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
    for camera in config.cameras:
        if use_hw:
            command += ["-hwaccel", "videotoolbox"]   # decodifica no chip de video do Mac
        command += ["-rtsp_transport", config.transport, "-timeout", "10000000",
                    "-buffer_size", "8388608",          # buffer UDP maior
                    "-max_delay", "1000000",            # espera ate 1s por pacotes atrasados
                    "-reorder_queue_size", "4000",      # reordena pacotes fora de ordem
                    "-fflags", "+genpts+discardcorrupt",
                    "-i", build_rtsp_url(camera, config.camera_quality)]
    command += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    command += [
        "-filter_complex", build_filters(config, font),
        "-map", "[out]", "-map", f"{len(config.cameras)}:a",
    ]
    if use_hw:
        command += ["-c:v", "h264_videotoolbox", "-realtime", "1", "-profile:v", "high",
                    "-b:v", config.video_bitrate, "-maxrate", config.video_bitrate]
    else:
        command += ["-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
                    "-b:v", config.video_bitrate, "-maxrate", config.video_bitrate,
                    "-bufsize", "5000k"]
    command += [
        "-pix_fmt", "yuv420p", "-g", str(config.fps * 2), "-keyint_min", str(config.fps * 2),
        "-c:a", "aac", "-b:a", "96k",
        "-f", "flv", f"{config.twitch_server}/{config.twitch_stream_key}",
    ]
    return command
