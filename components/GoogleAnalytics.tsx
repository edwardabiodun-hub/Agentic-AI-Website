import Script from "next/script";

const configuredMeasurementId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
const measurementId = /^G-[A-Z0-9]+$/.test(configuredMeasurementId ?? "")
  ? configuredMeasurementId!
  : "G-VPP81LYJ0Y";

export function GoogleAnalytics() {
  return (
    <>
      <Script
        async
        src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}');
        `}
      </Script>
    </>
  );
}
