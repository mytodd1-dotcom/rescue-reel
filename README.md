# Rescue Reel

**Turn urgent rescue needs into verified action.**

[Open the live product](https://rescue-reel-media.flyguy.chatgpt.site/) ·
[View the source on GitHub](https://github.com/mytodd1-dotcom/rescue-reel)

Rescue Reel converts a messy animal-rescue intake into ready-to-approve
campaign media while preserving the source facts, the human approval, and the
provenance of every generated asset.

## Why it exists

Small rescue teams lose critical time rewriting the same urgent need for every
channel. Generic AI tools can move faster, but they can also invent facts,
misstate deadlines, or make an emotional story impossible to audit.

Rescue Reel separates those concerns:

1. Preserve the original intake.
2. Extract only confirmed needs, deadlines, resources, and calls to action.
3. Use Genblaze to coordinate media generation and create a canonical manifest.
4. Require a human approval for the exact campaign draft.
5. Store approved assets and the provenance manifest together in Backblaze B2.

## Product demo

```bash
npm install
npm run dev:local
```

The interactive demo includes the complete intake-to-approval workflow. It
never publishes externally.

## Genblaze proof

Install the official SDK packages:

```bash
python3 -m venv .venv
.venv/bin/pip install -r pipeline/requirements.txt
```

Create and verify a deterministic local Genblaze manifest with no API keys:

```bash
.venv/bin/python pipeline/rescue_reel.py
```

Archive the approved demo asset and a canonical, hash-verified manifest to the
restricted B2 bucket without starting a new paid generation:

```bash
./pipeline/run_live_from_keychain.sh --archive-proof
```

This writes a safe public receipt to `public/live-proof.json`. The receipt
contains object keys and integrity hashes, never credentials or presigned URLs.

Run the live image-to-video pipeline and archive its asset plus canonical
manifest to B2:

```bash
./pipeline/run_live_from_keychain.sh
```

The Keychain runner loads the bucket-scoped GMI Cloud and Backblaze B2
credentials without writing secrets to the repository or a local `.env` file.

For environments without macOS Keychain, use an ignored `.env` file:

```bash
cp .env.example .env
# Add narrowly scoped GMI Cloud and Backblaze B2 credentials.
set -a && source .env && set +a
.venv/bin/python pipeline/rescue_reel.py --live
```

The live pipeline uses:

- `Pipeline` with chained image and video steps
- `GMICloudImageProvider` and `GMICloudVideoProvider`
- `ObjectStorageSink`
- `S3StorageBackend.for_backblaze`
- `KeyStrategy.HIERARCHICAL`
- Genblaze's canonical, hash-verifiable provenance manifest
- Explicit failure propagation so unavailable providers cannot masquerade as
  completed media

## Safety model

- Source notes remain unchanged.
- Generated copy is always labeled as a draft.
- The demo does not post, message, or charge anyone.
- Live credentials stay in ignored environment files.
- B2 keys should be restricted to one application bucket.
- A changed draft requires a new approval.
- Provider budget failures stop before any new payment or silent retry.

## Stack

- Next.js / React / TypeScript
- Genblaze Python SDK
- Backblaze B2
- GMI Cloud (optional live generation provider)
- OpenAI image generation for the initial campaign art

## License

MIT
