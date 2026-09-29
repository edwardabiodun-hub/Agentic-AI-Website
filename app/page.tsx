import Link from "next/link";
import { DiagnosticCta } from "../components/SiteParts";
import { resources } from "../content/resources";

const journey = [
  {
    stage: "Assess",
    name: "5-minute Business Independence Assessment",
    question: "Where is owner dependency, reporting friction, or manual work likely showing up?",
    status: "Free directional score and next-step route",
  },
  {
    stage: "Diagnose",
    name: "10-day Business Independence Diagnostic",
    question: "What is actually happening, what is it costing, and what should be fixed first?",
    status: "Bounded executive assessment",
  },
  {
    stage: "Improve",
    name: "Operating system and automation roadmap",
    question: "Which reporting cadence, decision rights, workflows, or automations will reduce avoidable owner involvement?",
    status: "Implementation path when justified",
  },
];

export default function Home() {
  return (
    <>
      <section className="shell hero">
        <div>
          <div className="eyebrow">For owner-led businesses with growing operating complexity</div>
          <h1>Find out why your business still depends on you, what it may be costing, and what to fix first.</h1>
          <p className="lede">
            RunRate Advisory helps founders, CEOs, and CFOs identify owner dependency, reporting
            bottlenecks, and manual operating friction before investing in automation, AI, or another
            management tool.
          </p>
          <div className="actions">
            <Link className="button" href="/assessment">Take the 5-Minute Assessment</Link>
            <Link className="button secondary" href="/diagnostic">See the 10-Day Diagnostic</Link>
          </div>
          <p className="hero-reassurance">No sales call required to see your initial score.</p>
          <div className="signal-strip" aria-label="RunRate engagement pathway">
            <div className="signal-card"><strong>5 minutes</strong><span>Start with a directional Business Independence Assessment.</span></div>
            <div className="signal-card"><strong>10 business days</strong><span>Validate dependency, cost, and operating constraints through the Diagnostic.</span></div>
            <div className="signal-card"><strong>90 days</strong><span>Leave with a prioritized plan for reducing owner involvement.</span></div>
          </div>
        </div>
        <aside className="hero-scorecard" aria-label="Assessment output preview">
          <div className="eyebrow">What the assessment shows</div>
          <h2>Business Independence Score</h2>
          <div className="score-preview" aria-label="Example assessment result">
            <strong><span>Example:</span> <b>58</b><em>/100</em></strong>
            <span>Medium confidence, reporting and owner-dependency risk</span>
          </div>
          <ul>
            <li>Owner Dependency Score</li>
            <li>Operating-System Maturity Score</li>
            <li>Information Visibility Score</li>
            <li>Top bottlenecks and confidence level</li>
            <li>Recommended next step</li>
          </ul>
          <p>Before adding another tool, confirm whether the real constraint is ownership, reporting cadence, or decisions that keep returning to the founder.</p>
        </aside>
      </section>

      <section className="recognition">
        <div className="shell recognition-grid">
          <div><div className="eyebrow">Where RunRate fits</div><h2>You may need this if the founder is still the operating system.</h2></div>
          <div><h3>Visibility bottleneck</h3><p>Reports arrive late, conflict, or require the owner to assemble the real picture.</p></div>
          <div><h3>Decision bottleneck</h3><p>Managers wait because authority and escalation rules remain unclear.</p></div>
          <div><h3>Operating friction</h3><p>Routine approvals, relationships, and recurring work keep returning to the owner.</p></div>
        </div>
      </section>

      <section className="section shell">
        <div className="section-head">
          <div><div className="eyebrow">Three business outcomes</div><h2>Make independence practical.</h2></div>
          <p>Start with the operating constraint, not a dashboard, automation, or AI tool.</p>
        </div>
        <div className="lever-grid">
          <div className="lever"><h3>Reduce owner dependency</h3><p>Expose the decisions, knowledge, relationships, and work that still require owner intervention.</p><div className="lever-fit">Best when critical work still returns to the founder.</div></div>
          <div className="lever"><h3>Improve executive decisions</h3><p>Create a decision-ready view of performance, risk, accountability, and next actions.</p><div className="lever-fit">Best when leaders spend too much time reconciling the truth.</div></div>
          <div className="lever"><h3>Automate manual operations</h3><p>Remove recurring reporting and workflow friction after the underlying process is clear.</p><div className="lever-fit">Best when manual work is repeatable but not yet clean enough to automate.</div></div>
        </div>
      </section>

      <section className="journey section">
        <div className="shell">
          <div className="section-head">
            <div><div className="eyebrow">How RunRate helps</div><h2>Move from signal to operating change.</h2></div>
            <p>The free assessment reveals likely pressure points. The Diagnostic validates causes, estimates impact, and defines the highest-value sequence for change.</p>
          </div>
          <div className="journey-grid">
            {journey.map((item, index) => (
              <article className="journey-stage" key={item.stage}>
                <div className="utility">0{index + 1} · {item.stage}</div>
                <h3>{item.name}</h3>
                <p>{item.question}</p>
                <div className="journey-status">{item.status}</div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="proof-band">
        <div className="shell proof-grid">
          <div>
            <div className="eyebrow">Built from operating experience</div>
            <h2>Real operating work, not software-first consulting.</h2>
            <div className="proof-chips" aria-label="Relevant operating experience">
              <span>Forecasting</span>
              <span>S&amp;OP</span>
              <span>Executive reporting</span>
              <span>Market intelligence</span>
              <span>Decision systems</span>
            </div>
          </div>
          <figure className="proof-quote">
            <blockquote>
              &ldquo;Eddie combines analytical skill, reliability, and professionalism with an ability to distill
              complex data into actionable insights.&rdquo;
            </blockquote>
            <figcaption>Former colleague, KION North America</figcaption>
          </figure>
        </div>
      </section>
      <DiagnosticCta />

      <section className="section shell">
        <div className="section-head">
          <div><div className="eyebrow">Insights</div><h2>Start with the pressure point.</h2></div>
          <Link href="/founder-resources">View all insights →</Link>
        </div>
        <div className="resource-grid">
          {resources.slice(0, 3).map((resource) => (
            <Link className="resource-card" href={`/founder-resources/${resource.slug}`} key={resource.slug}>
              <div className="meta">{resource.type}</div>
              <h3>{resource.title}</h3>
              <p>{resource.summary}</p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}




