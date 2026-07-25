#!/usr/bin/env python3
"""Build Rescue Reel media with Genblaze and archive it to Backblaze B2.

Dry-run mode creates a hash-verifiable Genblaze manifest without credentials.
Live mode runs an image-to-video GMI Cloud pipeline and stores the generated
assets plus canonical provenance manifest in Backblaze B2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


CAMPAIGN_PROMPT = (
    "Documentary-style sunrise portrait of Maple, a gentle tan shepherd mix, "
    "stepping from a rescue transport van in Kansas City. Hopeful, truthful, "
    "dignified, no text, no distress, vertical social-video composition."
)


def build_dry_run(output: Path) -> None:
    """Create the same canonical proof shape without network calls."""
    from genblaze_core import Manifest, Modality, RunBuilder, StepBuilder, StepStatus

    source_bytes = Path("public/og.png").read_bytes()
    step = (
        StepBuilder("openai", "gpt-image-2")
        .prompt(CAMPAIGN_PROMPT)
        .modality(Modality.IMAGE)
        .params(size="1536x1024", purpose="rescue-campaign")
        .status(StepStatus.SUCCEEDED)
        .asset(
            "file://public/og.png",
            "image/png",
            sha256=hashlib.sha256(source_bytes).hexdigest(),
        )
        .build()
    )
    run = RunBuilder("rescue-reel-maple").add_step(step).build()
    manifest = Manifest.from_run(run)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(manifest.to_canonical_json(), encoding="utf-8")
    print(
        json.dumps(
            {
                "mode": "dry-run",
                "run_id": run.run_id,
                "manifest": str(output),
                "canonical_hash": manifest.canonical_hash,
                "verified": manifest.verify(),
            },
            indent=2,
        )
    )


def run_live() -> None:
    """Run the official Genblaze pipeline against GMI Cloud and Backblaze B2."""
    from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline
    from genblaze_gmicloud import GMICloudImageProvider, GMICloudVideoProvider
    from genblaze_s3 import S3StorageBackend

    bucket = os.environ["B2_BUCKET"]
    storage = ObjectStorageSink(
        S3StorageBackend.for_backblaze(bucket),
        key_strategy=KeyStrategy.HIERARCHICAL,
    )

    result = (
        Pipeline("rescue-reel-maple", chain=True)
        .step(
            GMICloudImageProvider(),
            model="seedream-5.0-lite",
            prompt=CAMPAIGN_PROMPT,
            modality=Modality.IMAGE,
            aspect_ratio="9:16",
        )
        .step(
            GMICloudVideoProvider(),
            model="Kling-Image2Video-V2.1-Master",
            prompt=(
                "Slow documentary push-in. Maple looks toward the volunteer, "
                "tail moves gently, warm sunrise catches the van door. "
                "Natural motion, no text, no invented people."
            ),
            modality=Modality.VIDEO,
        )
        .run(sink=storage, timeout=900)
    )

    first_asset = result.run.steps[-1].assets[0]
    print(
        json.dumps(
            {
                "mode": "live",
                "run_id": result.run.run_id,
                "asset_url": first_asset.url,
                "asset_sha256": first_asset.sha256,
                "manifest_uri": result.manifest.manifest_uri,
                "canonical_hash": result.manifest.canonical_hash,
                "verified": result.manifest.verify(),
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="Generate media through GMI Cloud and store it in Backblaze B2.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("public/demo-manifest.json"),
        help="Dry-run manifest destination.",
    )
    args = parser.parse_args()

    if args.live:
        run_live()
    else:
        build_dry_run(args.output)


if __name__ == "__main__":
    main()
