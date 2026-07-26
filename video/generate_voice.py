from __future__ import annotations

import json
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import certifi


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "narration.txt"
OUTPUT = ROOT / "audio" / "rescue-reel-narration.wav"
KEYCHAIN_SERVICE = "impact-compass-openai-api-key"


def read_api_key() -> str:
    result = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    key = result.stdout.strip()
    if not key:
        raise RuntimeError("The saved OpenAI API key is empty.")
    return key


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "model": "gpt-4o-mini-tts",
            "voice": "cedar",
            "input": SCRIPT.read_text(encoding="utf-8"),
            "instructions": (
                "Speak like a thoughtful human founder explaining a product they "
                "deeply believe in. Warm, natural, compassionate, and quietly "
                "confident. Avoid an announcer voice, exaggerated drama, or robotic "
                "cadence. Use meaningful pauses and slightly emphasize the rescue "
                "facts, human approval, Backblaze B2, Genblaze, and the final line."
            ),
            "response_format": "wav",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=payload,
        headers={
            "Authorization": f"Bearer {read_api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        tls_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(
            request,
            timeout=180,
            context=tls_context,
        ) as response:
            OUTPUT.write_bytes(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(detail).get("error", {}).get("message", detail)
        except json.JSONDecodeError:
            message = detail
        raise RuntimeError(f"OpenAI voice generation failed: {message}") from error

    if OUTPUT.stat().st_size < 10_000:
        raise RuntimeError("Generated narration file is unexpectedly small.")
    print(OUTPUT)


if __name__ == "__main__":
    main()
