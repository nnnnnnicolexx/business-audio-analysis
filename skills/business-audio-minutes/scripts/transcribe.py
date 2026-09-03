#!/usr/bin/env python3
"""Cross-platform local transcription with MLX or faster-whisper."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_NAME = "business-audio-minutes"
QUALITY_LEVELS = {"fast", "balanced", "accurate"}
MLX_MODELS = {
    "fast": "mlx-community/whisper-small-mlx",
    "balanced": "mlx-community/whisper-large-v3-turbo",
    "accurate": "mlx-community/whisper-large-v3-turbo",
}
FASTER_MODELS = {
    "fast": "base",
    "balanced": "small",
    "accurate": "large-v3-turbo",
}


def get_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def load_config(path: Path | None) -> dict:
    config_path = path or get_codex_home() / SKILL_NAME / "config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^\w\-.]+", "_", value, flags=re.UNICODE).strip("_.")
    return cleaned or "recording"


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except (TypeError, ValueError):
            pass
    return str(value)


def inspect_audio(audio: Path) -> dict:
    result: dict[str, Any] = {"path": str(audio), "size_bytes": audio.stat().st_size}
    try:
        import av

        with av.open(str(audio)) as container:
            stream = next((item for item in container.streams if item.type == "audio"), None)
            if container.duration is not None:
                result["duration_seconds"] = float(container.duration / av.time_base)
            if stream is not None:
                result["sample_rate"] = stream.codec_context.sample_rate
                result["channels"] = stream.codec_context.channels
                result["codec"] = stream.codec_context.name
    except Exception as exc:  # Inspection failure must not block decoding.
        result["inspection_warning"] = str(exc)
    return result


def choose_backend(requested: str) -> str:
    apple_silicon = sys.platform == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}
    mlx_available = importlib.util.find_spec("mlx_whisper") is not None
    faster_available = importlib.util.find_spec("faster_whisper") is not None

    if requested == "mlx":
        if not apple_silicon:
            raise SystemExit("MLX backend requires Apple Silicon macOS.")
        if not mlx_available:
            raise SystemExit("mlx_whisper is not installed. Rerun the skill installer.")
        return "mlx"
    if requested == "faster":
        if not faster_available:
            raise SystemExit("faster_whisper is not installed. Rerun the skill installer.")
        return "faster"
    if apple_silicon and mlx_available:
        return "mlx"
    if faster_available:
        return "faster"
    raise SystemExit("No local ASR backend is installed. Run the skill installer.")


def convert_for_mlx(audio: Path, work_dir: Path) -> Path:
    if sys.platform != "darwin":
        raise SystemExit("MLX audio conversion is supported on macOS only.")
    converter = Path("/usr/bin/afconvert")
    if not converter.exists():
        raise SystemExit("macOS afconvert was not found.")
    work_dir.mkdir(parents=True, exist_ok=True)
    output = work_dir / f"{safe_name(audio.stem)}_16k.wav"
    if output.exists():
        output.unlink()
    subprocess.run(
        [str(converter), "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(audio), str(output)],
        check=True,
    )
    return output


def transcribe_mlx(
    audio: Path,
    work_dir: Path,
    quality: str,
    model_name: str | None,
    language: str,
    initial_prompt: str | None,
) -> tuple[dict, str, str]:
    import mlx_whisper
    import numpy as np
    from scipy.io import wavfile

    wav_path = convert_for_mlx(audio, work_dir)
    _, samples = wavfile.read(wav_path)
    if getattr(samples, "ndim", 1) > 1:
        samples = samples.mean(axis=1)
    if np.issubdtype(samples.dtype, np.integer):
        scale = float(max(abs(np.iinfo(samples.dtype).min), np.iinfo(samples.dtype).max))
        samples = samples.astype("float32") / scale
    else:
        samples = samples.astype("float32")

    selected_model = model_name or MLX_MODELS[quality]
    result = mlx_whisper.transcribe(
        samples,
        path_or_hf_repo=selected_model,
        language=language,
        task="transcribe",
        condition_on_previous_text=False,
        temperature=0.0,
        no_speech_threshold=0.6,
        logprob_threshold=-1.0,
        compression_ratio_threshold=2.4,
        initial_prompt=initial_prompt,
        verbose=False,
    )
    return json_safe(result), selected_model, "metal"


def auto_faster_device(requested: str) -> tuple[str, str]:
    if requested in {"cpu", "cuda"}:
        return requested, "int8" if requested == "cpu" else "float16"
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def transcribe_faster(
    audio: Path,
    quality: str,
    model_name: str | None,
    language: str,
    initial_prompt: str | None,
    device_request: str,
    vad_filter: bool,
) -> tuple[dict, str, str]:
    from faster_whisper import WhisperModel

    selected_model = model_name or FASTER_MODELS[quality]
    device, compute_type = auto_faster_device(device_request)
    model_root = get_codex_home() / "runtime" / SKILL_NAME / "models" / "faster-whisper"
    model_root.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(
        selected_model,
        device=device,
        compute_type=compute_type,
        download_root=str(model_root),
    )
    segment_iter, info = model.transcribe(
        str(audio),
        language=language,
        beam_size=5,
        vad_filter=vad_filter,
        condition_on_previous_text=False,
        initial_prompt=initial_prompt,
    )
    segments = []
    texts = []
    for segment in segment_iter:
        text = segment.text.strip()
        texts.append(text)
        segments.append(
            {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": text,
                "avg_logprob": segment.avg_logprob,
                "compression_ratio": segment.compression_ratio,
                "no_speech_prob": segment.no_speech_prob,
            }
        )
    result = {
        "text": " ".join(texts),
        "segments": segments,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
    }
    return result, selected_model, f"{device}/{compute_type}"


def format_timestamp(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{remainder:05.2f}"
    return f"{minutes:02d}:{remainder:05.2f}"


def quality_report(result: dict, audio_info: dict, backend: str, model: str, execution_device: str) -> dict:
    segments = result.get("segments", [])
    texts = [(segment.get("text") or "").strip() for segment in segments]
    full_text = "".join(texts)
    normalized = [re.sub(r"\s+", "", text) for text in texts if len(re.sub(r"\s+", "", text)) >= 4]
    repeated = [{"text": text, "count": count} for text, count in Counter(normalized).most_common() if count >= 5]
    duration = audio_info.get("duration_seconds") or result.get("duration")
    if not duration and segments:
        duration = max(float(segment.get("end", 0)) for segment in segments)
    density = len(re.sub(r"\s+", "", full_text)) / duration if duration else None
    logprobs = [segment.get("avg_logprob") for segment in segments if segment.get("avg_logprob") is not None]
    avg_logprob = sum(logprobs) / len(logprobs) if logprobs else None

    flags = []
    if not full_text.strip():
        flags.append("empty_transcript")
    if density is not None and density < 0.2:
        flags.append("sparse_transcript")
    if repeated:
        flags.append("repeated_phrases_review_required")
    if avg_logprob is not None and avg_logprob < -1.0:
        flags.append("low_average_log_probability")

    return {
        "backend": backend,
        "model": model,
        "execution_device": execution_device,
        "audio": audio_info,
        "segment_count": len(segments),
        "text_characters": len(re.sub(r"\s+", "", full_text)),
        "characters_per_second": round(density, 4) if density is not None else None,
        "average_log_probability": round(avg_logprob, 4) if avg_logprob is not None else None,
        "repeated_phrases": repeated[:20],
        "flags": flags,
    }


def process_audio(audio: Path, args: argparse.Namespace, config: dict) -> dict:
    audio = audio.expanduser().resolve()
    if not audio.is_file():
        raise SystemExit(f"Audio file not found: {audio}")

    quality = args.quality or config.get("quality", "balanced")
    if quality not in QUALITY_LEVELS:
        raise SystemExit(f"Unsupported quality setting: {quality}")
    backend = choose_backend(args.backend or config.get("backend", "auto"))
    language = args.language or config.get("language", "zh")

    if args.output_dir:
        output_dir = args.output_dir.expanduser().resolve()
    else:
        root = Path(config.get("output_root", Path.home() / "Documents" / "Codex" / SKILL_NAME)).expanduser()
        output_dir = root / f"{safe_name(audio.stem)}_{datetime.now():%Y%m%d}"
    work_dir = args.work_dir.expanduser().resolve() if args.work_dir else output_dir / "work"
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    audio_info = inspect_audio(audio)
    if backend == "mlx":
        result, selected_model, execution_device = transcribe_mlx(
            audio, work_dir, quality, args.model, language, args.initial_prompt
        )
    else:
        result, selected_model, execution_device = transcribe_faster(
            audio,
            quality,
            args.model,
            language,
            args.initial_prompt,
            args.device,
            not args.no_vad,
        )

    base = safe_name(audio.stem)
    transcript_path = output_dir / f"{base}_transcript.txt"
    raw_path = output_dir / f"{base}_raw.json"
    quality_path = output_dir / f"{base}_quality.json"

    lines = []
    for segment in result.get("segments", []):
        text = (segment.get("text") or "").strip()
        if text:
            lines.append(
                f"[{format_timestamp(segment.get('start', 0))}-{format_timestamp(segment.get('end', 0))}] {text}"
            )
    transcript_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    raw_payload = {
        "local_only": True,
        "source_audio": str(audio),
        "backend": backend,
        "model": selected_model,
        "execution_device": execution_device,
        "result": result,
    }
    raw_path.write_text(json.dumps(json_safe(raw_payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = quality_report(result, audio_info, backend, selected_model, execution_device)
    quality_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "audio": str(audio),
        "transcript": str(transcript_path),
        "raw_json": str(raw_path),
        "quality_json": str(quality_path),
        "backend": backend,
        "model": selected_model,
        "execution_device": execution_device,
        "quality_flags": report["flags"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe recordings locally without cloud ASR.")
    parser.add_argument("audio", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--backend", choices=["auto", "mlx", "faster"])
    parser.add_argument("--quality", choices=sorted(QUALITY_LEVELS))
    parser.add_argument("--model")
    parser.add_argument("--language")
    parser.add_argument("--initial-prompt")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--no-vad", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    summaries = [process_audio(audio, args, config) for audio in args.audio]
    print(json.dumps({"local_only": True, "outputs": summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
