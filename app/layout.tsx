import type { Metadata } from "next";
import { Space_Grotesk } from "next/font/google";
import Link from "next/link";
import { BackToTop } from "../components/SiteParts";
import { Logo } from "../components/Logo";
import { NavMenu } from "../components/NavMenu";
import { SiteAnalyticsTracker } from "../components/SiteAnalyticsTracker";
import { GoogleAnalytics } from "../components/GoogleAnalytics";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  weight: ["500", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "RunRate Advisory | Business Independence & Decision Systems",
    template: "%s | RunRate Advisory",
  },
  description:
    "Helping owner-led businesses reduce founder dependency, improve executive decisions, and remove recurring operational friction.",
  openGraph: { images: ["/og.png"], type: "website" },
  twitter: { card: "summary_large_image", images: ["/og.png"] },
};

const outcomeNav = [
  ["/how-i-help#dependency", "Reduce Owner Dependency"],
  ["/how-i-help#decisions", "Improve Executive Decisions"],
  ["/how-i-help#automation", "Automate Manual Operations"],
] as const;

const primaryNav = [
  ["/founder-resources", "Insights"],
  ["/about", "About Us"],
] as const;

const footerNav = [
  ["/how-i-help", "How I Help"],
  ...outcomeNav,
  ...primaryNav,
  ["/assessment", "Take the Assessment"],
] as const;

const socialLinks = [
  { href: "https://www.linkedin.com/company/143104903/", label: "LinkedIn", icon: "linkedin" },
  { href: "https://www.youtube.com/@RunRateAdvisory", label: "YouTube", icon: "youtube" },
  { href: "https://www.facebook.com/share/1FEtbyy3eu/", label: "Facebook", icon: "facebook" },
  { href: "https://www.instagram.com/runrateadvisory?igsh=YTMzaXRpMWZ5MjRn", label: "Instagram", icon: "instagram" },
  { href: "https://x.com/RunRateAdvisory", label: "X", icon: "x" },
] as const;

type SocialIconName = (typeof socialLinks)[number]["icon"];

function SocialIcon({ name }: { name: SocialIconName }) {
  switch (name) {
    case "linkedin":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6.94 8.96H3.8v10.32h3.14V8.96ZM5.37 7.56a1.82 1.82 0 1 0 0-3.64 1.82 1.82 0 0 0 0 3.64Zm14.83 6.08c0-3.16-1.69-4.63-3.94-4.63a3.4 3.4 0 0 0-3.07 1.69h-.04V8.96h-3.02v10.32h3.14v-5.1c0-1.34.25-2.64 1.91-2.64 1.64 0 1.66 1.53 1.66 2.73v5.01h3.14l.22-5.64Z" />
        </svg>
      );
    case "youtube":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M21.58 7.2a2.68 2.68 0 0 0-1.89-1.9C18.02 4.86 12 4.86 12 4.86s-6.02 0-7.69.45A2.68 2.68 0 0 0 2.42 7.2 27.97 27.97 0 0 0 1.97 12c0 1.7.15 3.4.45 4.8a2.68 2.68 0 0 0 1.89 1.89c1.67.45 7.69.45 7.69.45s6.02 0 7.69-.45a2.68 2.68 0 0 0 1.89-1.89c.3-1.4.45-3.1.45-4.8s-.15-3.4-.45-4.8ZM9.98 15.17V8.83L15.24 12l-5.26 3.17Z" />
        </svg>
      );
    case "facebook":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M14.04 8.65V7.1c0-.74.49-.91.84-.91h2.14V3.04L14.08 3c-3.27 0-4.01 2.45-4.01 4.02v1.63H7.5v3.25h2.57V21h3.97v-9.1h2.69l.36-3.25h-3.05Z" />
        </svg>
      );
    case "instagram":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            clipRule="evenodd"
            d="M7.8 3.25h8.4a4.55 4.55 0 0 1 4.55 4.55v8.4a4.55 4.55 0 0 1-4.55 4.55H7.8a4.55 4.55 0 0 1-4.55-4.55V7.8A4.55 4.55 0 0 1 7.8 3.25Zm0 1.9A2.65 2.65 0 0 0 5.15 7.8v8.4a2.65 2.65 0 0 0 2.65 2.65h8.4a2.65 2.65 0 0 0 2.65-2.65V7.8a2.65 2.65 0 0 0-2.65-2.65H7.8Zm8.96 1.48a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2ZM12 8.17a3.83 3.83 0 1 0 0 7.66 3.83 3.83 0 0 0 0-7.66Zm0 1.9a1.93 1.93 0 1 1 0 3.86 1.93 1.93 0 0 1 0-3.86Z"
            fillRule="evenodd"
          />
        </svg>
      );
    case "x":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M14.18 10.35 21.7 2h-1.78l-6.53 7.26L8.17 2H2.16l7.88 10.97L2.16 22h1.78l6.89-7.89L16.34 22h6.01l-8.17-11.65Zm-2.44 2.71-.8-1.1L4.6 3.35h2.72l5.13 6.97.8 1.1 6.66 9.05h-2.72l-5.45-7.41Z" />
        </svg>
      );
  }
}

function SocialLinks({ className }: { className: string }) {
  return (
    <div className={className} aria-label="RunRate Advisory social media">
      {socialLinks.map(({ href, label, icon }) => (
        <a key={href} href={href} aria-label={`RunRate Advisory on ${label}`} target="_blank" rel="noreferrer">
          <SocialIcon name={icon} />
        </a>
      ))}
    </div>
  );
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={spaceGrotesk.variable}>
        <div id="top" />
        <SiteAnalyticsTracker />
        <GoogleAnalytics />
        <header className="site-header">
          <Logo />
          <nav aria-label="Primary navigation">
            <NavMenu label="How I Help" links={outcomeNav} />
            {primaryNav.map(([href, label]) => <Link key={href} href={href}>{label}</Link>)}
            <SocialLinks className="header-social" />
            <Link className="nav-primary" href="/assessment">Take the Assessment</Link>
            <Link className="nav-cta" href="/contact">Start a Conversation</Link>
          </nav>
        </header>
        <main>{children}</main>
        <BackToTop />
        <footer>
          <div>
            <strong className="footer-brand">RunRate Advisory</strong>
            <p>Business independence through executive visibility, operating systems, and practical automation.</p>
            <div className="footer-contact" aria-label="RunRate Advisory contact details">
              <a href="tel:+18433127323">+1 843-312-7323</a>
              <span>Charleston, SC</span>
            </div>
            <SocialLinks className="footer-social" />
          </div>
          <div className="footer-links">
            {footerNav.map(([href, label]) => <Link key={href} href={href}>{label}</Link>)}
            <Link href="/contact">Start a Conversation</Link>
            <Link href="/privacy">Privacy</Link>
          </div>
          <p className="boundary">
            Independent advisory work only. No confidential employer information is used, and engagements
            within prohibited competitive areas are not accepted.
          </p>
        </footer>
      </body>
    </html>
  );
}
