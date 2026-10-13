import { PageHero } from "../../components/SiteParts";

export default function Privacy() {
  return (
    <>
      <PageHero eyebrow="Privacy" title="A restrained approach to personal information.">
        Only the information needed to respond to inquiries and provide the assessment is collected.
      </PageHero>
      <article className="content shell resource-body">
        <h2>Inquiry information</h2>
        <ul className="privacy-list">
          <li>Name, work email, company, role, employee count, bottleneck, and desired outcome are used to assess and respond to your inquiry.</li>
          <li>Resend may process the message for email delivery.</li>
        </ul>
        <h2>Business Independence Assessment</h2>
        <ul className="privacy-list">
          <li>If you request your report, a compact D1 record retains your assessment reference, methodology version, timestamp, component and overall scores, score and impact confidence, summarized capacity estimate, up to three risk codes, routed next step, consent choices, delivery metadata, and the contact details you provide.</li>
          <li>Complete assessment answers, report snapshot, generated PDF, and accepted AI/rules narrative are stored in encrypted Cloudflare R2 storage for 90 days and removed by the next daily cleanup, normally within 24 hours after the 90-day mark.</li>
          <li>Access is limited to the respondent report link and authorized RunRate follow-up. You may request deletion of this assessment information using the contact page.</li>
          <li>After the deterministic result is created, an internal assessment notification is emailed through Resend to info@runrategroup.com. It includes the respondent&apos;s name, email, company, role, deterministic result, and the accepted AI or rules-based narrative so the inquiry can be reviewed and followed up.</li>
          <li>Phone numbers, raw answers, and free-text operating responses are excluded from this notification.</li>
          <li>Report consent and marketing consent are collected separately. Report consent is required to generate and email your report and send the internal assessment notification; marketing consent is optional.</li>
          <li>The assessment applies deterministic rules to self-reported information. It is not an audit and does not independently validate root causes, implementation effort, savings, revenue, valuation, legal compliance, tax treatment, or other financial outcomes.</li>
        </ul>
        <h2>AI narrative handling</h2>
        <ul className="privacy-list">
          <li>OpenAI receives no respondent identity, raw answers, raw evidence, numeric results, or prose.</li>
          <li>OpenAI receives only finite candidate block IDs selected from locally approved narrative text.</li>
          <li>Any missing, duplicate, unknown, or incompatible ID causes a complete rules-based fallback, and the deterministic result remains authoritative.</li>
          <li>Narrative prose is not stored in D1; D1 retains only compact metadata and validated selection fields needed for controlled retries.</li>
        </ul>
        <h2>Retention</h2>
        <ul className="privacy-list">
          <li>Compact D1 assessment records, related assessment events, and Cloudflare R2 report objects follow the same 90-day retention policy.</li>
          <li>The D1 and R2 cleanup is scheduled for 03:17 UTC each day and records deletion counts for auditability.</li>
          <li>Mailbox deletion follows the same 90-day operational policy managed outside the website application; it is not application-enforced.</li>
        </ul>
        <h2>Video and analytics</h2>
        <ul className="privacy-list">
          <li>YouTube videos use privacy-enhanced embeds and are not loaded until requested.</li>
          <li>Website analytics, if enabled, are used to understand page and referral traffic and are not used to sell personal information.</li>
          <li>Site analytics events are stored separately from lead and assessment records.</li>
          <li>Analytics events use anonymous browser and session identifiers, page paths, referral or UTM source, coarse device context, download clicks, form interaction milestones, assessment step movement, and API performance or error signals.</li>
          <li>Analytics events do not store contact details, form values, raw assessment answers, free-text responses, IP address, or full user-agent strings.</li>
        </ul>
        <h2>Deletion</h2>
        <p>You may request correction or deletion of inquiry or assessment information during the retention period by using the contact page.</p>
      </article>
    </>
  );
}
