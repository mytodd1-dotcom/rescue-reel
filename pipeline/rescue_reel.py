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
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path


CAMPAIGN_PROMPT = (
    "Documentary-style sunrise portrait of Maple, a gentle tan shepherd mix, "
    "stepping from a rescue transport van in Kansas City. Hopeful, truthful, "
    "dignified, no text, no distress, vertical social-video composition."
)


def build_approved_demo_run(source_path: Path | None = None):
    """Build the approved Maple run used by dry-run and B2 archive modes."""
    from genblaze_core import (
        Manifest,
        Modality,
        RunBuilder,
        RunStatus,
        StepBuilder,
        StepStatus,
    )

    source_path = (source_path or Path("public/og.png")).resolve()
    source_bytes = source_path.read_bytes()
    step = (
        StepBuilder("openai", "gpt-image-2")
        .prompt(CAMPAIGN_PROMPT)
        .modality(Modality.IMAGE)
        .params(size="1536x1024", purpose="rescue-campaign")
        .status(StepStatus.SUCCEEDED)
        .asset(
            source_path.as_uri(),
            "image/png",
            sha256=hashlib.sha256(source_bytes).hexdigest(),
        )
        .build()
    )
    run = (
        RunBuilder("rescue-reel-maple")
        .status(RunStatus.COMPLETED)
        .meta(
            approval="human-approved-demo",
            source="preserved-rescue-intake",
            purpose="foster-and-transport-campaign",
        )
        .add_step(step)
        .build()
    )
    manifest = Manifest.from_run(run)
    return run, manifest


def build_dry_run(output: Path) -> None:
    """Create the same canonical proof shape without network calls."""
    run, manifest = build_approved_demo_run()
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


def archive_approved_proof(output: Path) -> None:
    """Archive the approved demo asset and canonical manifest to Backblaze B2."""
    from genblaze_core import KeyStrategy, ObjectStorageSink
    from genblaze_s3 import S3StorageBackend

    bucket = os.environ["B2_BUCKET"]
    region = os.environ["B2_REGION"]
    backend = S3StorageBackend.for_backblaze(bucket)
    sink = ObjectStorageSink(
        backend,
        prefix="rescue-reel",
        key_strategy=KeyStrategy.HIERARCHICAL,
    )
    with tempfile.TemporaryDirectory(prefix="rescue-reel-proof-") as temp_dir:
        transfer_source = Path(temp_dir) / "maple-approved.png"
        shutil.copy2("public/og.png", transfer_source)
        run, manifest = build_approved_demo_run(transfer_source)
        sink.write_run(run, manifest)
        stored = sink.read_manifest(run, verify=True)

    asset = stored.run.steps[0].assets[0]
    asset_key = backend.key_from_url(asset.url)
    manifest_key = sink.manifest_key_for(run)
    proof = {
        "schema_version": "1.0",
        "archive_status": "verified",
        "archived_at": datetime.now(UTC).isoformat(),
        "approval": "human-approved-demo",
        "bucket": bucket,
        "region": region,
        "run_id": run.run_id,
        "run_name": run.name,
        "provider": stored.run.steps[0].provider,
        "model": stored.run.steps[0].model,
        "asset_key": asset_key,
        "asset_sha256": asset.sha256,
        "manifest_key": manifest_key,
        "manifest_uri": sink.manifest_url_for(run),
        "canonical_hash": stored.canonical_hash,
        "verified": stored.verify(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2))


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
        .run(sink=storage, timeout=900, raise_on_failure=True)
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--live",
        action="store_true",
        help="Generate media through GMI Cloud and store it in Backblaze B2.",
    )
    mode.add_argument(
        "--archive-proof",
        action="store_true",
        help="Archive the approved demo asset and canonical manifest to B2.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("public/demo-manifest.json"),
        help="Dry-run manifest destination.",
    )
    parser.add_argument(
        "--proof-output",
        type=Path,
        default=Path("public/live-proof.json"),
        help="Safe public receipt written after a verified B2 archive.",
    )
    args = parser.parse_args()

    if args.live:
        run_live()
    elif args.archive_proof:
        archive_approved_proof(args.proof_output)
    else:
        build_dry_run(args.output)


if __name__ == "__main__":
    main()
