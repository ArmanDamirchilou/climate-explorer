"""Make an automatic timing draft for review, not a verified human transcript."""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def transcribe(source, output, model_name="base.en"):
    model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
    pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(source),
                                   "-f", "f32le", "-ac", "1", "-ar", "16000", "-"])
    samples = np.frombuffer(pcm, dtype=np.float32)
    segments, info = model.transcribe(samples, language="en", beam_size=5,
                                      word_timestamps=True, vad_filter=False)
    records = [{"start": row.start, "end": row.end, "text": row.text,
                "words": [{"start": word.start, "end": word.end, "word": word.word,
                           "probability": word.probability} for word in row.words or []]}
               for row in segments]
    result = {"method": "faster-whisper 1.2.1", "model": model_name,
              "scope": "Automatic draft. Inspect the actual speech and correct captions before publishing.",
              "duration": info.duration, "segments": records,
              "text": " ".join(row["text"].strip() for row in records)}
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(result["text"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="base.en")
    args = parser.parse_args()
    transcribe(args.source, args.output, args.model)
