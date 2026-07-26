"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import liveProof from "../public/live-proof.json";

const sampleIntake =
  "URGENT — Maple needs a foster by Friday. She is a gentle 3-year-old shepherd mix, good with kids, and recovering from a leg injury. Transport from Wichita to Kansas City is the blocker. A donor pledged $200 for fuel and medication. Contact the foster coordinator before 6 PM.";

const proofSteps = [
  {
    label: "Source intake",
    detail: "Rescue note preserved unchanged",
    requiredPhase: 0,
  },
  {
    label: "Grounded campaign",
    detail: "Need, deadline, facts, and CTA extracted",
    requiredPhase: 1,
  },
  {
    label: "Generated media",
    detail: "Approved image attached to a Genblaze run",
    requiredPhase: 2,
  },
  {
    label: "Human approval",
    detail: "Exact campaign draft approved before release",
    requiredPhase: 3,
  },
  {
    label: "B2 archive",
    detail: "Asset and canonical manifest verified in B2",
    requiredPhase: 3,
  },
];

const eventSteps = [
  "Source receipt locked",
  "Claims grounded to intake",
  "Generated asset attached",
  "Human approval recorded",
  "B2 archive hash verified",
];

function Mark({ children }: { children: React.ReactNode }) {
  return <span className="mark">{children}</span>;
}

export function RescueReelApp() {
  const [intake, setIntake] = useState(sampleIntake);
  const [phase, setPhase] = useState(0);
  const [view, setView] = useState<"campaign" | "proof">("campaign");
  const [isAdvancing, setIsAdvancing] = useState(false);

  const urgency = useMemo(
    () => (intake.toLowerCase().includes("urgent") ? "Critical" : "High"),
    [intake],
  );

  const advance = async () => {
    setIsAdvancing(true);
    await new Promise((resolve) => window.setTimeout(resolve, phase === 1 ? 850 : 450));
    setPhase((value) => Math.min(value + 1, 3));
    setIsAdvancing(false);
  };
  const reset = () => {
    setPhase(0);
    setView("campaign");
  };
  const shortHash = `${liveProof.canonical_hash.slice(0, 12)}…${liveProof.canonical_hash.slice(-8)}`;

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
          Verified B2 proof ready
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
          <Image
            src="/og.png"
            alt="A tan rescue dog stepping from a transport van at sunrise"
            fill
            priority
            sizes="(max-width: 1040px) 95vw, 54vw"
          />
          <div className="media-receipt">
            <span>LIVE PROVENANCE ATTACHED</span>
            <strong>SHA-256 · {shortHash}</strong>
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
              disabled={phase >= 3 || intake.trim().length < 20 || isAdvancing}
            >
              {isAdvancing && "Processing verified step…"}
              {!isAdvancing && phase === 0 && "Extract a truthful campaign"}
              {!isAdvancing && phase === 1 && "Build the generated rescue reel"}
              {!isAdvancing && phase === 2 && "Approve & verify the B2 archive"}
              {!isAdvancing && phase === 3 && "Campaign verified"}
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
                      <div className="generated-reel">
                        <div className="reel-frame">
                          <Image
                            src="/og.png"
                            alt="Approved generated campaign image of Maple arriving at sunrise"
                            fill
                            sizes="(max-width: 1040px) 90vw, 48vw"
                          />
                          <div className="reel-copy">
                            <span>FOSTER NEEDED BY FRIDAY</span>
                            <strong>One safe landing place completes the trip.</strong>
                          </div>
                        </div>
                        <div className="generation-row">
                          <span>Generated image</span>
                          <span>Grounded narration</span>
                          <span>9:16 motion preview</span>
                          <strong>Genblaze provenance</strong>
                        </div>
                      </div>
                    )}
                    {phase === 3 && (
                      <div className="verified-banner">
                        <span>✓</span>
                        <div>
                          <strong>Approved archive verified</strong>
                          <small>
                            b2://{liveProof.bucket}/{liveProof.manifest_key}
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
                  const complete = phase >= step.requiredPhase;
                  return (
                    <div className={complete ? "proof-step complete" : "proof-step"} key={step.label}>
                      <span>{complete ? "✓" : index + 1}</span>
                      <div>
                        <strong>{step.label}</strong>
                        <small>{step.detail}</small>
                      </div>
                      <code>{complete ? (index === 3 ? "APPROVED" : "VERIFIED") : "WAITING"}</code>
                    </div>
                  );
                })}
                <div className="manifest-card">
                  <div>
                    <span>LIVE B2 RECEIPT</span>
                    <strong>{liveProof.run_id.slice(0, 12)}…</strong>
                  </div>
                  <dl>
                    <div>
                      <dt>Provider</dt>
                      <dd>{liveProof.provider} / {liveProof.model}</dd>
                    </div>
                    <div>
                      <dt>Storage</dt>
                      <dd>{liveProof.bucket}</dd>
                    </div>
                    <div>
                      <dt>Integrity</dt>
                      <dd>{phase >= 3 ? shortHash : "pending approval"}</dd>
                    </div>
                  </dl>
                  <div className="receipt-path">
                    <span>MANIFEST OBJECT</span>
                    <code>{liveProof.manifest_key}</code>
                  </div>
                </div>
              </div>
            )}
          </article>
        </div>
      </section>

      <section className="operations" aria-labelledby="operations-title">
        <div className="operations-heading">
          <p className="eyebrow">THE PIPELINE IS THE PRODUCT</p>
          <h2 id="operations-title">Every transition leaves evidence.</h2>
          <p>
            Rescue Reel treats generation as an observable workflow—not a
            mystery spinner. Cost boundaries stop unapproved spend, approved
            assets remain usable, and every archive can be verified later.
          </p>
        </div>
        <div className="event-stream" aria-label="Pipeline event stream">
          {eventSteps.map((event, index) => {
            const requiredPhase = index <= 2 ? index : 3;
            const complete = phase >= requiredPhase;
            return (
              <div className={complete ? "event complete" : "event"} key={event}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{event}</strong>
                <code>{complete ? "event.completed" : "event.waiting"}</code>
              </div>
            );
          })}
        </div>
        <div className="resilience-card">
          <span>BUDGET-AWARE FALLBACK</span>
          <strong>No surprise generation charge.</strong>
          <p>
            If a paid provider is unavailable, Rescue Reel stops that request,
            preserves the failure state, and keeps the approved asset ready for
            a verified B2 archive.
          </p>
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
              Genblaze coordinates generated media, observable events, and
              provider boundaries while producing a canonical manifest.
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
