import Script from "next/script";

const configuredProjectId = process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID;
const projectId = /^[a-z0-9]+$/i.test(configuredProjectId ?? "")
  ? configuredProjectId!
  : "yq6mx7qz2f";

export function MicrosoftClarity() {
  return (
    <Script id="microsoft-clarity" strategy="afterInteractive">
      {`
        (function(c,l,a,r,i,t,y){
          c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
          t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
          y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        })(window, document, "clarity", "script", "${projectId}");
      `}
    </Script>
  );
}
