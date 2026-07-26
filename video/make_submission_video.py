from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
CAPTURES = ROOT / "captures"
RENDER = ROOT / "render"
NARRATION = ROOT / "audio" / "rescue-reel-narration.wav"
MUSIC = ROOT.parents[1] / "hackathon-assets" / "cat-context-agent-premium-music-bed.wav"
SILENT = RENDER / "rescue-reel-submission.silent.mp4"
OUTPUT = RENDER / "rescue-reel-submission-final.mp4"
MANIFEST = RENDER / "rescue-reel-video-manifest.json"

W, H, FPS = 1280, 720, 24
SCREEN = (1200, 610)
SCREEN_ORIGIN = (40, 42)


SCENES = [
    {
        "image": "01-hero.png",
        "duration": 10,
        "chapter": "01 / THE NEED",
        "headline": "Urgency deserves more than a content generator.",
        "chip": "REAL RESCUE WORKFLOW",
        "focus": (0.50, 0.48),
        "title": True,
    },
    {
        "image": "01-hero.png",
        "duration": 14,
        "chapter": "02 / RESCUE REEL",
        "headline": "One urgent note. One verified campaign.",
        "chip": "LIVE PRODUCT",
        "focus": (0.52, 0.50),
    },
    {
        "image": "02-grounded.png",
        "duration": 24,
        "chapter": "03 / GROUND THE CLAIMS",
        "headline": "Preserve the note. Extract only what is true.",
        "chip": "FRIDAY · INJURY · $200",
        "focus": (0.52, 0.38),
    },
    {
        "image": "03-generated.png",
        "duration": 24,
        "chapter": "04 / BUILD THE MEDIA",
        "headline": "Generated media stays attached to its source.",
        "chip": "GENBLAZE RUN",
        "focus": (0.66, 0.56),
    },
    {
        "image": "04-approved.png",
        "duration": 20,
        "chapter": "05 / HUMAN BOUNDARY",
        "headline": "Generated does not mean approved.",
        "chip": "EXACT DRAFT APPROVED",
        "focus": (0.55, 0.48),
    },
    {
        "image": "05-proof.png",
        "duration": 18,
        "chapter": "06 / PROOF TRAIL",
        "headline": "Every transition leaves evidence.",
        "chip": "5 CHECKS VERIFIED",
        "focus": (0.62, 0.48),
    },
    {
        "image": "06-receipt-pipeline.png",
        "duration": 24,
        "chapter": "07 / REAL B2 RECEIPT",
        "headline": "The archive was written, read back, and verified.",
        "chip": "BACKBLAZE B2",
        "focus": (0.65, 0.42),
    },
    {
        "image": "07-pipeline.png",
        "duration": 15,
        "chapter": "08 / OBSERVABLE PIPELINE",
        "headline": "Failures stop safely. Approved assets stay usable.",
        "chip": "NO SURPRISE SPEND",
        "focus": (0.54, 0.52),
    },
    {
        "image": "08-purpose.png",
        "duration": 24,
        "chapter": "09 / THE STANDARD",
        "headline": "The story can be emotional. The evidence cannot be imaginary.",
        "chip": "RESCUE REEL",
        "focus": (0.50, 0.58),
        "ending": True,
    },
]


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Helvetica.ttf"
        ),
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONTS = {
    "micro": get_font(14, True),
    "chapter": get_font(17, True),
    "headline": get_font(32, True),
    "title": get_font(72, True),
    "body": get_font(23, False),
}


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    font: ImageFont.ImageFont,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def load_capture(name: str) -> Image.Image:
    cache = getattr(load_capture, "_cache", {})
    if name not in cache:
        cache[name] = Image.open(CAPTURES / name).convert("RGB")
        load_capture._cache = cache
    return cache[name].copy()


def camera_crop(
    image: Image.Image,
    progress: float,
    focus_x: float,
    focus_y: float,
) -> Image.Image:
    target_w, target_h = SCREEN
    zoom = 1.015 + 0.085 * ease(progress)
    scale = max(target_w / image.width, target_h / image.height) * zoom
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    max_x = max(0, resized.width - target_w)
    max_y = max(0, resized.height - target_h)
    drift = 0.055 * (progress - 0.5)
    left = round(max_x * min(1, max(0, focus_x + drift)))
    top = round(max_y * min(1, max(0, focus_y)))
    return resized.crop((left, top, left + target_w, top + target_h))


def background() -> Image.Image:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :, 0] = (5 + 10 * x).astype(np.uint8)
    arr[:, :, 1] = (12 + 11 * (1 - y)).astype(np.uint8)
    arr[:, :, 2] = (24 + 18 * y).astype(np.uint8)
    base = Image.fromarray(arr, "RGB").convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((-220, -280, 520, 430), fill=(238, 156, 47, 42))
    draw.ellipse((850, -210, 1480, 460), fill=(36, 168, 139, 34))
    return Image.alpha_composite(
        base,
        glow.filter(ImageFilter.GaussianBlur(95)),
    ).convert("RGB")


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius=radius, fill=255)
    return mask


def draw_live_screen(
    frame: Image.Image,
    scene: dict[str, object],
    progress: float,
) -> None:
    focus_x, focus_y = scene["focus"]
    content = camera_crop(
        load_capture(str(scene["image"])),
        progress,
        float(focus_x),
        float(focus_y),
    ).convert("RGBA")
    x, y = SCREEN_ORIGIN
    shadow = Image.new(
        "RGBA",
        (SCREEN[0] + 48, SCREEN[1] + 48),
        (0, 0, 0, 0),
    )
    ImageDraw.Draw(shadow).rounded_rectangle(
        (24, 24, SCREEN[0] + 24, SCREEN[1] + 24),
        radius=26,
        fill=(0, 0, 0, 170),
    )
    frame.alpha_composite(
        shadow.filter(ImageFilter.GaussianBlur(15)),
        (x - 24, y - 12),
    )
    frame.paste(content, (x, y), rounded_mask(SCREEN, 18))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle(
        (x, y, x + SCREEN[0], y + SCREEN[1]),
        radius=18,
        outline=(247, 177, 67, 165),
        width=2,
    )
    draw.rounded_rectangle(
        (x + 20, y + 18, x + 128, y + 48),
        radius=15,
        fill=(4, 18, 31, 224),
        outline=(129, 224, 193, 150),
        width=1,
    )
    pulse = 140 + int(100 * abs(math.sin(progress * math.pi * 2)))
    draw.ellipse(
        (x + 32, y + 29, x + 40, y + 37),
        fill=(105, 232, 177, pulse),
    )
    draw.text(
        (x + 49, y + 25),
        "LIVE PRODUCT",
        font=FONTS["micro"],
        fill=(226, 250, 242, 255),
    )


def draw_lower_third(
    frame: Image.Image,
    scene: dict[str, object],
    local_progress: float,
    global_progress: float,
) -> None:
    draw = ImageDraw.Draw(frame)
    panel_y = 548
    alpha = int(
        232
        * min(
            1,
            local_progress * 6,
            max(0.16, (1 - local_progress) * 6),
        )
    )
    draw.rounded_rectangle(
        (28, panel_y, W - 28, H - 24),
        radius=20,
        fill=(4, 12, 24, max(205, alpha)),
        outline=(239, 166, 56, 125),
        width=1,
    )
    draw.text(
        (54, panel_y + 17),
        str(scene["chapter"]),
        font=FONTS["chapter"],
        fill=(247, 176, 65, 255),
    )
    headline_y = panel_y + 47
    for line in wrap(
        draw,
        str(scene["headline"]),
        790,
        FONTS["headline"],
    ):
        draw.text(
            (54, headline_y),
            line,
            font=FONTS["headline"],
            fill=(249, 247, 239, 255),
        )
        headline_y += 38
    chip = str(scene["chip"])
    chip_w = min(
        340,
        round(draw.textlength(chip, font=FONTS["chapter"]) + 58),
    )
    chip_x = W - chip_w - 52
    draw.rounded_rectangle(
        (chip_x, panel_y + 50, W - 52, panel_y + 91),
        radius=21,
        fill=(176, 97, 29, 232),
    )
    draw.text(
        (chip_x + 24, panel_y + 61),
        chip,
        font=FONTS["chapter"],
        fill=(255, 246, 227, 255),
    )
    tracker_y = H - 35
    for index in range(len(SCENES)):
        x = 850 + index * 36
        active = index <= int(global_progress * len(SCENES))
        draw.rounded_rectangle(
            (x, tracker_y, x + 24, tracker_y + 4),
            radius=2,
            fill=(247, 176, 65, 255) if active else (55, 70, 87, 230),
        )


def draw_title_overlay(
    frame: Image.Image,
    local_progress: float,
) -> None:
    dark = Image.new("RGBA", (W, H), (2, 7, 15, 135))
    frame.alpha_composite(dark)
    draw = ImageDraw.Draw(frame)
    y = 145
    for line in ["RESCUE", "REEL"]:
        draw.text(
            (80, y),
            line,
            font=FONTS["title"],
            fill=(250, 247, 237, 255),
        )
        y += 78
    draw.rounded_rectangle(
        (82, 330, 505, 383),
        radius=26,
        fill=(216, 127, 34, 235),
    )
    draw.text(
        (113, 344),
        "TURN URGENT NEED INTO VERIFIED ACTION",
        font=FONTS["micro"],
        fill=(255, 249, 237, 255),
    )
    if local_progress > 0.45:
        draw.text(
            (83, 410),
            "Built with Genblaze + Backblaze B2",
            font=FONTS["body"],
            fill=(225, 235, 235, 255),
        )


def draw_ending(frame: Image.Image, progress: float) -> None:
    if progress < 0.58:
        return
    alpha = round(235 * ease((progress - 0.58) / 0.42))
    overlay = Image.new("RGBA", (W, H), (4, 11, 22, alpha))
    frame.alpha_composite(overlay)
    draw = ImageDraw.Draw(frame)
    draw.text(
        (72, 142),
        "RESCUE REEL",
        font=FONTS["title"],
        fill=(249, 247, 239, 255),
    )
    y = 270
    for line in wrap(
        draw,
        "The story can be emotional. The evidence cannot be imaginary.",
        1040,
        FONTS["headline"],
    ):
        draw.text(
            (75, y),
            line,
            font=FONTS["headline"],
            fill=(247, 176, 65, 255),
        )
        y += 42
    draw.text(
        (76, 450),
        "rescue-reel-media.flyguy.chatgpt.site",
        font=FONTS["body"],
        fill=(207, 223, 225, 255),
    )
    draw.text(
        (76, 490),
        "github.com/mytodd1-dotcom/rescue-reel",
        font=FONTS["body"],
        fill=(207, 223, 225, 255),
    )


def compose(
    scene: dict[str, object],
    local_progress: float,
    global_progress: float,
) -> Image.Image:
    frame = background().convert("RGBA")
    draw_live_screen(frame, scene, local_progress)
    if scene.get("title"):
        draw_title_overlay(frame, local_progress)
    else:
        draw_lower_third(frame, scene, local_progress, global_progress)
    if scene.get("ending"):
        draw_ending(frame, local_progress)
    return frame.convert("RGB")


def render_silent() -> None:
    RENDER.mkdir(parents=True, exist_ok=True)
    total_frames = sum(
        int(scene["duration"]) * FPS
        for scene in SCENES
    )
    completed = 0
    with imageio.get_writer(
        SILENT,
        fps=FPS,
        codec="libx264",
        quality=9,
        macro_block_size=1,
        ffmpeg_log_level="error",
    ) as writer:
        for scene in SCENES:
            scene_frames = int(scene["duration"]) * FPS
            for index in range(scene_frames):
                local_progress = (index + 1) / scene_frames
                writer.append_data(
                    np.asarray(
                        compose(
                            scene,
                            local_progress,
                            completed / total_frames,
                        )
                    )
                )
                completed += 1


def mix_audio() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    total_seconds = sum(int(scene["duration"]) for scene in SCENES)
    narration_delay_ms = 900
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(SILENT),
        "-i",
        str(NARRATION),
        "-stream_loop",
        "-1",
        "-i",
        str(MUSIC),
        "-filter_complex",
        (
            f"[1:a]adelay={narration_delay_ms}|{narration_delay_ms},"
            "volume=1.08,afade=t=in:st=0:d=0.18,"
            "apad=pad_dur=12[narr];"
            f"[2:a]volume=0.095,afade=t=in:st=0:d=1.3,"
            f"afade=t=out:st={total_seconds - 4}:d=4[music];"
            "[narr][music]amix=inputs=2:duration=longest:"
            "dropout_transition=1[a]"
        ),
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-t",
        str(total_seconds),
        "-movflags",
        "+faststart",
        str(OUTPUT),
    ]
    subprocess.run(command, check=True)


def write_manifest() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    probe = subprocess.run(
        [
            ffmpeg,
            "-i",
            str(OUTPUT),
        ],
        capture_output=True,
        text=True,
    )
    MANIFEST.write_text(
        json.dumps(
            {
                "output": str(OUTPUT),
                "resolution": f"{W}x{H}",
                "fps": FPS,
                "duration_seconds": sum(
                    int(scene["duration"])
                    for scene in SCENES
                ),
                "narration": str(NARRATION),
                "music": str(MUSIC),
                "captures": [
                    str(CAPTURES / str(scene["image"]))
                    for scene in SCENES
                ],
                "ffmpeg_verified": "Video:" in probe.stderr
                and "Audio:" in probe.stderr,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    required = [
        NARRATION,
        MUSIC,
        *[
            CAPTURES / str(scene["image"])
            for scene in SCENES
        ],
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing: " + ", ".join(missing))
    render_silent()
    mix_audio()
    write_manifest()
    print(OUTPUT)


if __name__ == "__main__":
    main()
