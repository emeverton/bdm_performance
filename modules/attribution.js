export function initAttribution() {
  const campaign = new URLSearchParams(window.location.search);
  const fields = ["utm_source", "utm_medium", "utm_campaign"];
  const campaignValues = Object.fromEntries(fields.map((key) => [
    key,
    (campaign.get(key) || "").slice(0, 80).replace(/[^\p{L}\p{N} _.-]/gu, "").trim(),
  ]));

  document.querySelectorAll('a[href^="https://wa.me/5544988018242"]').forEach((link) => {
    const originalHref = link.href;
    link.addEventListener("click", () => {
      const section = link.closest("section")?.id || (link.closest("header") ? "header" : "footer");
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: "bdm_partner_cta_click",
        section,
        label: link.textContent.trim(),
        ...campaignValues,
      });

      if (!campaignValues.utm_source && !campaignValues.utm_medium && !campaignValues.utm_campaign) return;
      const target = new URL(originalHref);
      const origin = [campaignValues.utm_source, campaignValues.utm_medium, campaignValues.utm_campaign]
        .filter(Boolean).join(" / ");
      target.searchParams.set("text", `${target.searchParams.get("text") || ""}\nOrigem: ${origin}`);
      link.href = target.toString();
    });
  });
}
