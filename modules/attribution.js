export function initAttribution() {
  const campaign = new URLSearchParams(window.location.search);
  const fields = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "gbraid", "wbraid", "fbclid"];
  const sanitize = (value, limit = 120) => (value || "").slice(0, limit).replace(/[^\p{L}\p{N} _.-]/gu, "").trim();
  const current = Object.fromEntries(fields.map((key) => [key, sanitize(campaign.get(key))]));
  let stored = {};

  try {
    stored = JSON.parse(sessionStorage.getItem("bdm_attribution") || "{}");
  } catch {
    stored = {};
  }

  const campaignValues = Object.fromEntries(fields.map((key) => [key, current[key] || sanitize(stored[key])]));
  const attribution = {
    ...campaignValues,
    landing_path: sanitize(stored.landing_path || window.location.pathname, 160),
    referrer_host: sanitize(stored.referrer_host || (() => {
      try { return document.referrer ? new URL(document.referrer).hostname : "direct"; }
      catch { return "direct"; }
    })(), 100),
  };

  try { sessionStorage.setItem("bdm_attribution", JSON.stringify(attribution)); } catch { /* storage is optional */ }

  const pushEvent = (payload) => {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
    if (typeof window.gtag === "function") window.gtag("event", payload.event, payload);
    if (typeof window.fbq === "function") window.fbq("trackCustom", payload.event, payload);
  };

  const slug = (value) => sanitize(value, 80).toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");

  document.querySelectorAll('a[href^="https://wa.me/5544988018242"]').forEach((link) => {
    const originalHref = link.href;
    link.addEventListener("click", () => {
      const section = link.closest("section")?.id || (link.closest("header") ? "header" : "footer");
      const ctaId = link.dataset.ctaId || `${section}_${slug(link.textContent)}`;
      pushEvent({
        event: "bdm_partner_cta_click",
        event_id: typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `${Date.now()}_${ctaId}`,
        conversion_destination: "whatsapp",
        cta_id: ctaId,
        section,
        label: link.textContent.trim(),
        ...attribution,
      });

      const target = new URL(originalHref);
      const origin = [attribution.utm_source, attribution.utm_medium, attribution.utm_campaign]
        .filter(Boolean).join(" / ");
      const context = [`Interesse: ${ctaId}`];
      if (origin) context.push(`Origem: ${origin}`);
      target.searchParams.set("text", `${target.searchParams.get("text") || ""}\n${context.join("\n")}`);
      link.href = target.toString();
    });
  });
}
