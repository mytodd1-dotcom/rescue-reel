# Rescue Reel

## Links

- Live product: https://rescue-reel-media.flyguy.chatgpt.site/
- Source code: https://github.com/mytodd1-dotcom/rescue-reel

## Tagline

Turn urgent animal-rescue notes into approved campaign media with a verifiable
chain of custody.

## Inspiration

Small rescue teams often have the facts, the urgency, and willing supporters,
but not enough time to turn scattered notes into trustworthy media for every
channel. Generic generation tools can move quickly while quietly changing a
deadline, inventing a medical detail, or losing the connection between the
approved message and the final asset.

Rescue Reel exists to make speed and accountability reinforce each other.

## What it does

Rescue Reel guides a rescue coordinator through one observable workflow:

1. Preserve the original intake.
2. Extract the confirmed need, deadline, resources, and next useful action.
3. Attach generated campaign media to a Genblaze run.
4. Require human approval for the exact campaign.
5. Archive the approved asset and canonical manifest in Backblaze B2.
6. Verify the stored manifest and expose a safe receipt with the run ID,
   object keys, provider/model, SHA-256 asset hash, and canonical manifest hash.

The public demo uses Maple, a shepherd mix who needs a foster and transport
support. The receipt shown in the interface corresponds to a real private B2
archive that was written and read back through Genblaze.

## How we built it

- Next.js, React, TypeScript, and vinext for the interactive product.
- Genblaze `RunBuilder`, `StepBuilder`, `Manifest`, `ObjectStorageSink`, and
  `S3StorageBackend.for_backblaze` for provenance and durable archival.
- Backblaze B2 for the approved generated asset and canonical manifest.
- OpenAI `gpt-image-2` for the approved Maple campaign image.
- An optional GMI Cloud image-to-video path configured through
  `GMICloudImageProvider` and `GMICloudVideoProvider`.

The production proof path uses a B2 application key restricted to one private
bucket. Credentials remain in Keychain locally and are never written into the
repository, manifest, public receipt, or browser.

## Meaningful Backblaze B2 usage

The approved media asset and its canonical manifest are stored together under
a hierarchical per-run prefix. The app displays the exact B2 object path and
integrity hashes without exposing a credential-bearing or expiring URL.

The archive command reads the stored manifest back from B2 and verifies its
canonical hash before producing the safe public receipt used by the demo.

## Meaningful Genblaze usage

Genblaze defines the media run, records the provider and model, transfers the
asset to B2, recomputes the manifest after the storage URL is attached, writes
the canonical manifest, and verifies the stored result.

The optional live path chains image and video providers through Genblaze and
uses explicit failure propagation. A provider budget failure cannot silently
be presented as a completed campaign.

## Production-minded behavior

- Human approval is required before the archive step completes.
- The source intake remains visible and unchanged.
- Asset and manifest hashes are displayed as judge-visible evidence.
- Paid-provider failures stop before any new payment or uncontrolled retry.
- The approved-asset archive path remains available when a generation provider
  is temporarily unavailable.
- The B2 key is restricted to the Rescue Reel application bucket.

## Challenges

The most important engineering challenge was separating three states that
media demos often blur together: generated, approved, and durably archived.
Rescue Reel treats them as distinct transitions with separate evidence.

A live provider also returned an insufficient-credit boundary during testing.
Instead of hiding it, the pipeline now propagates that failure cleanly and
preserves a safe path for archiving a previously approved generated asset.

## What we learned

The durable artifact is not only the image or video. It is the combination of
the source, the human decision, the generated asset, and a manifest that can
prove which exact bytes were approved.

## What's next

- Add a funded secondary generation provider and automatic provider failover.
- Generate natural narration and a composed vertical MP4.
- Stream live Genblaze progress events from a job worker to the interface.
- Add rescue-organization workspaces and reusable approval policies.
- Add B2 Event Notifications for post-archive distribution workflows.
