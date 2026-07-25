"use client";

import { useMemo, useState } from "react";

const sampleIntake =
  "URGENT — Maple needs a foster by Friday. She is a gentle 3-year-old shepherd mix, good with kids, and recovering from a leg injury. Transport from Wichita to Kansas City is the blocker. A donor pledged $200 for fuel and medication. Contact the foster coordinator before 6 PM.";

const proofSteps = [
  {
    label: "Source intake",
    detail: "Rescue note preserved unchanged",
  },
  {
    label: "Campaign brief",
    detail: "Need, deadline, facts, and CTA extracted",
  },
  {
    label: "Genblaze run",
    detail: "Image + narration provenance captured",
  },
  {
    label: "B2 archive",
    detail: "Assets and manifest stored durably",
  },
];

function Mark({ children }: { children: React.ReactNode }) {
  return <span className="mark">{children}</span>;
}

export function RescueReelApp() {
  const [intake, setIntake] = useState(sampleIntake);
  const [phase, setPhase] = useState(0);
  const [view, setView] = useState<"campaign" | "proof">("campaign");

  const urgency = useMemo(
    () => (intake.toLowerCase().includes("urgent") ? "Critical" : "High"),
    [intake],
  );

  const advance = () => setPhase((value) => Math.min(value + 1, 3));
  const reset = () => setPhase(0);

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Rescue Reel home">
          <span className="brand-paw" aria-hidden="true">
            ●
          </span>
          <span>RESCUE REEL</span>
        </a>
        <div className="topbar-status">
          <span className="pulse" />
          Genblaze pipeline ready
        </div>
        <a className="quiet-link" href="#how-it-works">
          How it works
        </a>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">MEDIA THAT MOVES AT RESCUE SPEED</p>
          <h1>
            One urgent note.
            <br />
            One <em>verified</em> campaign.
          </h1>
          <p className="lede">
            Rescue Reel turns scattered shelter updates into ready-to-approve
            adoption and fundraising media—without losing the facts, the source,
            or the human decision.
          </p>
          <div className="hero-stats" aria-label="Product safeguards">
            <div>
              <strong>1 click</strong>
              <span>from intake to draft</span>
            </div>
            <div>
              <strong>0 posts</strong>
              <span>without approval</span>
            </div>
            <div>
              <strong>100%</strong>
              <span>traceable assets</span>
            </div>
          </div>
        </div>

        <div className="hero-visual" aria-label="Generated Rescue Reel campaign">
          <img
            src="/og.png"
            alt="A tan rescue dog stepping from a transport van at sunrise"
          />
          <div className="media-receipt">
            <span>PROVENANCE ATTACHED</span>
            <strong>SHA-256 · 8F2A…91C7</strong>
          </div>
        </div>
      </section>

      <section className="workspace" aria-labelledby="workspace-title">
        <div className="workspace-heading">
          <div>
            <p className="eyebrow">LIVE PRODUCT WALKTHROUGH</p>
            <h2 id="workspace-title">Build Maple&apos;s rescue campaign</h2>
          </div>
          <button className="text-button" type="button" onClick={reset}>
            Reset demo
          </button>
        </div>

        <div className="work-grid">
          <article className="intake-panel">
            <div className="panel-label">
              <span>01</span>
              <div>
                <strong>Paste the real rescue note</strong>
                <small>Messy is okay. The source stays intact.</small>
              </div>
            </div>
            <textarea
              aria-label="Rescue intake note"
              value={intake}
              onChange={(event) => {
                setIntake(event.target.value);
                setPhase(0);
              }}
            />
            <div className="fact-row">
              <Mark>{urgency} urgency</Mark>
              <Mark>Friday deadline</Mark>
              <Mark>$200 pledged</Mark>
            </div>
            <button
              className="primary-button"
              type="button"
              onClick={advance}
              disabled={phase >= 3 || intake.trim().length < 20}
            >
              {phase === 0 && "Extract a truthful campaign"}
              {phase === 1 && "Run Genblaze media pipeline"}
              {phase === 2 && "Approve & archive to B2"}
              {phase === 3 && "Campaign verified"}
              <span aria-hidden="true">→</span>
            </button>
            <p className="button-note">
              {phase < 2
                ? "No public post is created during this demo."
                : "The final archive is locked to this approved draft."}
            </p>
          </article>

          <article className="result-panel">
            <div className="view-tabs" role="tablist" aria-label="Result view">
              <button
                role="tab"
                aria-selected={view === "campaign"}
                className={view === "campaign" ? "active" : ""}
                onClick={() => setView("campaign")}
                type="button"
              >
                Campaign
              </button>
              <button
                role="tab"
                aria-selected={view === "proof"}
                className={view === "proof" ? "active" : ""}
                onClick={() => setView("proof")}
                type="button"
              >
                Proof trail
              </button>
            </div>

            {view === "campaign" ? (
              <div className={`campaign-output phase-${phase}`}>
                {phase === 0 ? (
                  <div className="empty-state">
                    <span>◌</span>
                    <h3>The campaign begins with the source.</h3>
                    <p>
                      Rescue Reel will separate confirmed facts from persuasive
                      language before generating a single asset.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="campaign-topline">
                      <span className="urgent-badge">FOSTER NEEDED BY FRIDAY</span>
                      <span>Draft #{phase === 1 ? "01" : "02"}</span>
                    </div>
                    <h3>Maple has the ride. She needs the landing place.</h3>
                    <p className="campaign-body">
                      Maple is a gentle three-year-old shepherd mix recovering
                      from a leg injury. A donor has covered fuel and medication.
                      Now one Kansas City foster can complete her trip to safety.
                    </p>
                    <div className="campaign-cta">
                      <div>
                        <small>NEXT USEFUL ACTION</small>
                        <strong>Offer a 14-day foster home</strong>
                      </div>
                      <span>Contact coordinator →</span>
                    </div>
                    {phase >= 2 && (
                      <div className="generation-row">
                        <span>Image</span>
                        <span>Narration</span>
                        <span>9:16 cut</span>
                        <strong>Generated with provenance</strong>
                      </div>
                    )}
                    {phase === 3 && (
                      <div className="verified-banner">
                        <span>✓</span>
                        <div>
                          <strong>Approved archive verified</strong>
                          <small>
                            b2://rescue-reel/maple/2026-07-25/manifest.json
                          </small>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <div className="proof-trail">
                {proofSteps.map((step, index) => {
                  const complete = phase > index - 1;
                  return (
                    <div className={complete ? "proof-step complete" : "proof-step"} key={step.label}>
                      <span>{complete ? "✓" : index + 1}</span>
                      <div>
                        <strong>{step.label}</strong>
                        <small>{step.detail}</small>
                      </div>
                      <code>{complete ? "VERIFIED" : "WAITING"}</code>
                    </div>
                  );
                })}
                <div className="manifest-card">
                  <div>
                    <span>CANONICAL MANIFEST</span>
                    <strong>rr_01JZ8MAPLE</strong>
                  </div>
                  <dl>
                    <div>
                      <dt>Provider</dt>
                      <dd>Genblaze / OpenAI</dd>
                    </div>
                    <div>
                      <dt>Storage</dt>
                      <dd>Backblaze B2</dd>
                    </div>
                    <div>
                      <dt>Integrity</dt>
                      <dd>{phase >= 3 ? "hash verified" : "pending approval"}</dd>
                    </div>
                  </dl>
                </div>
              </div>
            )}
          </article>
        </div>
      </section>

      <section className="how" id="how-it-works">
        <div>
          <p className="eyebrow">WHY THIS IS DIFFERENT</p>
          <h2>The story can be emotional. The evidence cannot be imaginary.</h2>
        </div>
        <div className="how-grid">
          <article>
            <span>01</span>
            <h3>Ground every claim</h3>
            <p>
              Deadlines, medical details, locations, and offers stay linked to
              the original intake instead of being embellished by a model.
            </p>
          </article>
          <article>
            <span>02</span>
            <h3>Generate as a pipeline</h3>
            <p>
              Genblaze coordinates image, narration, and format variants while
              producing a canonical manifest for every run.
            </p>
          </article>
          <article>
            <span>03</span>
            <h3>Archive what was approved</h3>
            <p>
              Backblaze B2 stores the media, source receipt, and manifest
              together so teams can reproduce exactly what went public.
            </p>
          </article>
        </div>
      </section>

      <footer>
        <div className="brand">
          <span className="brand-paw">●</span>
          <span>RESCUE REEL</span>
        </div>
        <p>Built so rescue teams can spend less time formatting urgency and more time answering it.</p>
        <div className="footer-stack">
          <span>GENBLAZE</span>
          <span>BACKBLAZE B2</span>
          <span>HUMAN APPROVAL</span>
        </div>
      </footer>
    </main>
  );
}
