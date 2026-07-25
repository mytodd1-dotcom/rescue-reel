import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("https://rescue-reel.test/", {
      headers: { accept: "text/html", host: "rescue-reel.test" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the Rescue Reel product", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(
    html,
    /<title>Rescue Reel — Verified media for urgent animal rescue<\/title>/i,
  );
  assert.match(html, /One urgent note\./);
  assert.match(html, /Build Maple/);
  assert.match(html, /Genblaze/);
  assert.match(html, /Backblaze B2/);
  assert.match(html, /Human approval/i);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton/i);
});

test("ships the provenance pipeline and project assets", async () => {
  const [pipeline, readme, manifest, hosting] = await Promise.all([
    readFile(new URL("../pipeline/rescue_reel.py", import.meta.url), "utf8"),
    readFile(new URL("../README.md", import.meta.url), "utf8"),
    readFile(new URL("../public/demo-manifest.json", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
  ]);

  assert.match(pipeline, /Pipeline\("rescue-reel-maple", chain=True\)/);
  assert.match(pipeline, /S3StorageBackend\.for_backblaze/);
  assert.match(pipeline, /ObjectStorageSink/);
  assert.match(readme, /human approval/i);
  const parsedManifest = JSON.parse(manifest);
  assert.equal(parsedManifest.schema_version, "1.5");
  assert.equal(parsedManifest.run.name, "rescue-reel-maple");
  assert.equal(parsedManifest.run.steps[0].provider, "openai");
  assert.match(parsedManifest.canonical_hash, /^[a-f0-9]{64}$/);
  assert.match(JSON.parse(hosting).project_id, /^appgprj_/);
  await access(new URL("../public/og.png", import.meta.url));
  await assert.rejects(
    access(new URL("../app/_sites-preview", import.meta.url)),
  );
});
