import json
import subprocess
from typing import Any


"""
Flags retornáveis:

camera_model_absent:
    Não foi identificado modelo/fabricante/codificador relacionado à câmera.

gps_absent:
    Não foram encontrados metadados de localização GPS.

creation_timestamp_absent:
    Não foi encontrado timestamp de criação do vídeo.

codec_inconsistency:
    Há ausência ou inconsistência em informações básicas do codec de vídeo.

audio_codec_mismatch:
    O codec de áudio declarado não é compatível com a tag do codec.

container_metadata_stripped:
    O container do vídeo não possui tags/metadados relevantes.
"""


def _run_ffprobe(video_path: str) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return {}

    try:
        return json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def _get_format_tags(metadata: dict[str, Any]) -> dict[str, Any]:
    return metadata.get("format", {}).get("tags", {}) or {}


def _has_camera_model(metadata: dict[str, Any]) -> bool:
    tags = _get_format_tags(metadata)

    camera_keys = [
        "make",
        "model",
        "encoder",
        "com.apple.quicktime.make",
        "com.apple.quicktime.model",
    ]

    return any(tags.get(key) for key in camera_keys)


def _has_gps(metadata: dict[str, Any]) -> bool:
    tags = _get_format_tags(metadata)

    gps_keys = [
        "location",
        "location-eng",
        "com.apple.quicktime.location.ISO6709",
    ]

    return any(tags.get(key) for key in gps_keys)


def _has_creation_timestamp(metadata: dict[str, Any]) -> bool:
    tags = _get_format_tags(metadata)

    timestamp_keys = [
        "creation_time",
        "date",
        "com.apple.quicktime.creationdate",
    ]

    return any(tags.get(key) for key in timestamp_keys)


def _has_codec_inconsistency(metadata: dict[str, Any]) -> bool:
    streams = metadata.get("streams", []) or []

    video_streams = [
        stream for stream in streams
        if stream.get("codec_type") == "video"
    ]

    if not video_streams:
        return True

    for stream in video_streams:
        if not stream.get("codec_name") or not stream.get("codec_long_name"):
            return True

    return False


def _has_audio_codec_mismatch(metadata: dict[str, Any]) -> bool:
    streams = metadata.get("streams", []) or []

    audio_streams = [
        stream for stream in streams
        if stream.get("codec_type") == "audio"
    ]

    for stream in audio_streams:
        codec_name = str(stream.get("codec_name", "")).lower()
        codec_tag_string = str(stream.get("codec_tag_string", "")).lower()

        if codec_name and codec_tag_string:
            if codec_name not in codec_tag_string and codec_tag_string not in codec_name:
                return True

    return False


def _is_container_metadata_stripped(metadata: dict[str, Any]) -> bool:
    tags = _get_format_tags(metadata)
    return len(tags) == 0


def analyze(video_path: str) -> dict[str, Any]:
    metadata = _run_ffprobe(video_path)
    metadata_flags: list[str] = []

    if not metadata:
        metadata_flags = [
            "camera_model_absent",
            "gps_absent",
            "creation_timestamp_absent",
            "container_metadata_stripped",
        ]

        return {
            "metadata_flags": metadata_flags,
            "metadata_score": round(len(metadata_flags) / 6, 2),
        }

    if not _has_camera_model(metadata):
        metadata_flags.append("camera_model_absent")

    if not _has_gps(metadata):
        metadata_flags.append("gps_absent")

    if not _has_creation_timestamp(metadata):
        metadata_flags.append("creation_timestamp_absent")

    if _has_codec_inconsistency(metadata):
        metadata_flags.append("codec_inconsistency")

    if _has_audio_codec_mismatch(metadata):
        metadata_flags.append("audio_codec_mismatch")

    if _is_container_metadata_stripped(metadata):
        metadata_flags.append("container_metadata_stripped")

    metadata_score = round(len(metadata_flags) / 6, 2)

    return {
        "metadata_flags": metadata_flags,
        "metadata_score": metadata_score,
    }