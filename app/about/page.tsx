import Link from "next/link";

/* vinext serves this already-optimized local portrait directly. */
/* eslint-disable @next/next/no-img-element */

const eddieLinkedInUrl = "https://www.linkedin.com/in/edward-abiodun-09600a10/";
const macLinkedInUrl = "https://www.linkedin.com/in/macdonald-mide-madariola/";

export const metadata = {
  title: "About Us",
  description:
    "Meet the people behind RunRate Advisory, a business operations and systems advisory firm helping companies build clearer decisions and stronger operating systems.",
};

const capabilities = [
  {
    label: "Commercial clarity",
    title: "See demand and the market more clearly.",
    copy: "Forecasting, S&OP, and market intelligence become useful when they connect commercial assumptions and help leaders decide where to focus.",
    details: "Demand planning · Forecasting and S&OP · Market and competitive intelligence",
  },
  {
    label: "Executive visibility",
    title: "Turn reporting into a management instrument.",
    copy: "KPI frameworks and executive reporting should expose the few conditions that require judgment. They should not create another layer of information to interpret.",
    details: "KPI frameworks · Executive reporting · Decision-ready synthesis",
  },
  {
    label: "Scalable execution",
    title: "Make recurring work easier to scale.",
    copy: "Practical process design, automation, and AI can remove recurring friction once the decision, owner, and operating constraint are understood.",
    details: "Process design · Automation · AI-enabled decision systems",
  },
];

export default function AboutUs() {
  return (
    <>
      <header className="about-hero shell">
        <div className="about-portrait-wrap">
          <div className="about-portrait-frame">
            <img
              src="/edward-abiodun-identity-locked.png"
              alt="Edward Abiodun"
            />
          </div>
          <div className="about-profile-note">
            <span>Edward “Eddie” Abiodun</span>
            <span>Charleston, South Carolina</span>
          </div>
        </div>
        <div className="about-intro">
          <div className="eyebrow">About RunRate Advisory</div>
          <h1>Clearer decisions. Stronger operating systems. Less dependence on one person.</h1>
          <p className="lede">
            We help leaders turn fragmented information, unclear accountability, and founder dependency
            into practical management systems.
          </p>
          <div className="actions">
            <Link className="button" href="/contact">Start a focused conversation →</Link>
            <Link className="button secondary" href="/diagnostic">See the diagnostic</Link>
          </div>
          <a className="about-linkedin" href={eddieLinkedInUrl} target="_blank" rel="noreferrer">
            View Eddie&apos;s LinkedIn profile →
          </a>
        </div>
        <aside className="about-margin" aria-label="Decision margin">
          <div className="utility">Decision margin</div>
          <p>Good systems do not replace judgment. They create room for better judgment.</p>
        </aside>
      </header>

      <section className="about-story shell">
        <div>
          <div className="eyebrow">The perspective behind the work</div>
          <h2 className="display">Our work turns commercial questions into operating decisions.</h2>
        </div>
        <div className="about-biography">
          <p>
            RunRate Advisory is built around a practical operating belief: growth gets harder when
            decisions, reporting, workflows, and critical knowledge remain concentrated in too few people.
          </p>
          <p>
            Eddie&apos;s background spans commercial planning, demand forecasting, S&amp;OP, market and competitive
            intelligence, executive reporting, and commercial strategy. Across that work, the recurring
            challenge is rarely a lack of data. It is the absence of a shared view that leaders can use to
            make and follow through on decisions.
          </p>
          <p>
            We begin with the business decision, workflow, accountability, or information gap. Technology
            comes second. Automation and AI earn a place only when they remove recurring friction and leave
            the leadership team with a better operating system.
          </p>
        </div>
      </section>

      <section className="about-team shell">
        <div className="about-section-head">
          <div className="about-section-kicker">
            <div className="eyebrow">The team</div>
          </div>
          <h2 className="display">A growing advisory team built around operations, clarity, and execution.</h2>
        </div>
        <div className="about-team-grid">
          <article className="about-team-card about-team-card-featured">
            <div className="about-team-photo">
              <img src="/edward-abiodun-identity-locked.png" alt="Edward Abiodun" />
            </div>
            <div>
              <div className="utility">Founder / Principal Advisor</div>
              <h3>Edward “Eddie” Abiodun</h3>
              <p>
                Commercial planning, forecasting, S&amp;OP, market intelligence, executive reporting,
                and decision-system experience applied to founder-led operating complexity.
              </p>
              <a className="about-linkedin" href={eddieLinkedInUrl} target="_blank" rel="noreferrer">
                View LinkedIn profile →
              </a>
            </div>
          </article>
          <article className="about-team-card">
            <div className="about-team-photo">
              <img src="/macdonald-mide-madariola.jpeg" alt="Macdonald Mide-Madariola" />
            </div>
            <div>
              <div className="utility">Business development / Growth strategy</div>
              <h3>Macdonald “Mac” Mide-Madariola</h3>
              <p>
                Mac brings a business development and client-solutions background, supported by artificial
                intelligence studies, market research, data analysis, and business strategy experience.
              </p>
              <a className="about-linkedin" href={macLinkedInUrl} target="_blank" rel="noreferrer">
                View LinkedIn profile →
              </a>
            </div>
          </article>
        </div>
      </section>

      <section className="about-capabilities">
        <div className="shell">
          <div className="about-section-head">
            <div className="about-section-kicker">
              <div className="eyebrow">What we bring</div>
            </div>
            <h2 className="display">Cross-functional experience, organized around management outcomes.</h2>
          </div>
          <div className="about-capability-grid">
            {capabilities.map((capability) => (
              <article className="about-capability" key={capability.label}>
                <div className="utility">{capability.label}</div>
                <h3>{capability.title}</h3>
                <p>{capability.copy}</p>
                <div className="about-detail">{capability.details}</div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="about-method shell">
        <div className="about-method-intro">
          <div className="eyebrow">How we work</div>
          <h2 className="display">Business problem first. Technology second.</h2>
          <p>
            The goal is not a more sophisticated dashboard or an AI demonstration. It is a lighter,
            more dependable way to run the business.
          </p>
        </div>
        <ol className="about-steps">
          <li><span>Begin</span> with the business decision or operating constraint.</li>
          <li><span>Identify</span> the missing information, ownership, or workflow.</li>
          <li><span>Design</span> the lightest system that improves the decision.</li>
          <li><span>Automate</span> only where recurring friction can be removed safely.</li>
        </ol>
        <div className="about-decision">
          <div>
            <div className="utility">What changes</div>
            <p>A clearer operating picture, ownership structure, and decision cadence.</p>
          </div>
          <div>
            <div className="utility">What remains</div>
            <p>Judgment, accountability, and final decisions stay with the leadership team.</p>
          </div>
        </div>
      </section>

      <section className="about-proof">
        <div className="shell">
          <div className="about-section-head">
            <div className="eyebrow">Professional perspective</div>
            <h2 className="display">What colleagues say about the work.</h2>
          </div>
          <div className="about-quotes">
            <figure>
              <blockquote>
                “Eddie combines analytical skill, reliability, and professionalism with an ability to
                distill complex data into actionable insights that support sales strategy.”
              </blockquote>
              <figcaption>
                <strong>Christoph Brand</strong>
                <span>Former colleague at KION North America</span>
              </figcaption>
            </figure>
            <figure>
              <blockquote>
                “Edward brought strong rigor to forecasting, competitor analysis, and order-intake
                planning while improving reporting and supporting important strategic initiatives.”
              </blockquote>
              <figcaption>
                <strong>Christian Bischof</strong>
                <span>Former manager at KION Group</span>
              </figcaption>
            </figure>
          </div>
          <a className="about-linkedin" href={eddieLinkedInUrl} target="_blank" rel="noreferrer">
            Read Eddie&apos;s full recommendations on LinkedIn →
          </a>
        </div>
      </section>

      <section className="about-boundary shell">
        <div className="utility">A clear professional boundary</div>
        <p>
          Independent advisory work does not use confidential employer information. RunRate Advisory does
          not accept engagements involving KION dealers, direct competitor dealer networks, or
          material-handling pricing, competitive strategy, or intelligence work that overlaps with Eddie&apos;s
          employment responsibilities.
        </p>
      </section>

      <section className="about-closing">
        <div className="shell">
          <div>
            <div className="eyebrow">A practical starting point</div>
            <h2 className="display">If the business has outgrown informal coordination, start there.</h2>
          </div>
          <div>
            <p>
              The first conversation is used to understand the dependency, clarify the desired outcome,
              and determine whether the Business Independence Diagnostic is the right next step.
            </p>
            <Link className="button" href="/contact">Start a focused conversation →</Link>
          </div>
        </div>
      </section>
    </>
  );
}
