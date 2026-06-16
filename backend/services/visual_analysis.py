import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch

try:
    import timm
except ImportError:
    timm = None


CHUNK_FPS = 1
IMAGE_SIZE = 299
MODEL_CACHE = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def extract_frames(video_path: str) -> tuple[list[str], str]:
    temp_dir = tempfile.mkdtemp(prefix="visual_frames_")
    output_pattern = os.path.join(temp_dir, "frame_%06d.jpg")

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"fps={CHUNK_FPS}",
        "-q:v",
        "2",
        output_pattern,
        "-hide_banner",
        "-loglevel",
        "error",
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return [], temp_dir

    frames = sorted(str(path) for path in Path(temp_dir).glob("*.jpg"))

    return frames, temp_dir


def preprocess_frames(frame_paths: list[str]) -> torch.Tensor:
    processed_frames = []

    for frame_path in frame_paths:
        image = cv2.imread(frame_path)

        if image is None:
            continue

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
        image = image.astype(np.float32) / 255.0
        image = (image - 0.5) / 0.5
        image = np.transpose(image, (2, 0, 1))

        processed_frames.append(image)

    if not processed_frames:
        return torch.empty((0, 3, IMAGE_SIZE, IMAGE_SIZE), dtype=torch.float32)

    return torch.tensor(np.array(processed_frames), dtype=torch.float32)


def load_model():
    global MODEL_CACHE

    if MODEL_CACHE is not None:
        return MODEL_CACHE

    if timm is None:
        raise RuntimeError("A biblioteca timm não está instalada.")

    model = timm.create_model(
        "xception",
        pretrained=False,
        num_classes=2,
    )

    weights_path = os.getenv("XCEPTION_WEIGHTS_PATH")

    if weights_path and os.path.exists(weights_path):
        state_dict = torch.load(weights_path, map_location=DEVICE)
        model.load_state_dict(state_dict, strict=False)

    model.to(DEVICE)
    model.eval()

    MODEL_CACHE = model

    return MODEL_CACHE


def run_inference(frames_tensor: torch.Tensor) -> list[float]:
    if frames_tensor.shape[0] == 0:
        return []

    model = load_model()
    frames_tensor = frames_tensor.to(DEVICE)

    with torch.no_grad():
        outputs = model(frames_tensor)
        probabilities = torch.softmax(outputs, dim=1)

    return probabilities[:, 1].detach().cpu().numpy().tolist()


def aggregate_frame_scores(scores: list[float]) -> dict[str, Any]:
    if not scores:
        return {
            "visual_score": 0.0,
            "manipulation_detected": False,
            "manipulation_type": "no_frames",
            "frames_analyzed": 0,
        }

    mean_score = float(np.mean(scores))
    std_score = float(np.std(scores))

    manipulation_detected = mean_score >= 0.70

    if manipulation_detected:
        manipulation_type = "visual_deepfake"
    elif mean_score >= 0.40:
        manipulation_type = "suspicious_visual_pattern"
    else:
        manipulation_type = "authentic"

    return {
        "visual_score": round(mean_score, 4),
        "manipulation_detected": manipulation_detected,
        "manipulation_type": manipulation_type,
        "frames_analyzed": len(scores),
        "score_std": round(std_score, 4),
    }


def analyze(video_path: str) -> dict[str, Any]:
    frames_dir = None

    try:
        frame_paths, frames_dir = extract_frames(video_path)

        if not frame_paths:
            return {
                "visual_score": 0.0,
                "manipulation_detected": False,
                "manipulation_type": "no_frames",
                "frames_analyzed": 0,
            }

        frames_tensor = preprocess_frames(frame_paths)
        scores = run_inference(frames_tensor)

        return aggregate_frame_scores(scores)

    except Exception as error:
        return {
            "visual_score": 0.0,
            "manipulation_detected": False,
            "manipulation_type": "visual_analysis_error",
            "frames_analyzed": 0,
            "error": str(error),
        }

    finally:
        if frames_dir:
            shutil.rmtree(frames_dir, ignore_errors=True)