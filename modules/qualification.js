const PHONE = "5518997553071";
const CONSENT_KEY = "bdm_measurement_consent";

function sanitize(value, limit = 120) {
  return String(value || "").slice(0, limit).replace(/[<>]/g, "").trim();
}

function pushEvent(payload) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(payload);
  let measurementConsent = "denied";
  try { measurementConsent = localStorage.getItem(CONSENT_KEY) || "denied"; } catch { /* Optional storage. */ }
  if (measurementConsent !== "granted") return;
  if (typeof window.gtag === "function") window.gtag("event", payload.event, payload);
  if (typeof window.fbq === "function") {
    const metaEvent = payload.event === "generate_lead" ? "Lead" : payload.event;
    window.fbq("track", metaEvent, payload);
  }
}

function readAttribution() {
  try { return JSON.parse(sessionStorage.getItem("bdm_attribution") || "{}"); }
  catch { return {}; }
}

function initConsent() {
  const banner = document.querySelector("#consent-banner");
  if (!banner) return;
  let current = null;
  try { current = localStorage.getItem(CONSENT_KEY); } catch { current = "denied"; }
  if (!current) banner.hidden = false;
  banner.querySelectorAll("[data-consent]").forEach((button) => {
    button.addEventListener("click", () => {
      const value = button.dataset.consent === "granted" ? "granted" : "denied";
      try { localStorage.setItem(CONSENT_KEY, value); } catch { /* Optional storage. */ }
      banner.hidden = true;
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: "consent_update", analytics_storage: value, ad_storage: value });
    });
  });
}

function markInvalid(field, invalid) {
  field.setAttribute("aria-invalid", invalid ? "true" : "false");
}

export function initQualification() {
  initConsent();
  const form = document.querySelector("#partner-form");
  const error = document.querySelector("#form-error");
  if (!form || !error) return;

  form.querySelectorAll("input, select").forEach((field) => {
    field.addEventListener("input", () => markInvalid(field, false));
    field.addEventListener("change", () => markInvalid(field, false));
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const required = [...form.querySelectorAll("[required]")];
    const invalid = required.filter((field) => !field.checkValidity());
    required.forEach((field) => markInvalid(field, invalid.includes(field)));
    if (invalid.length) {
      error.textContent = "Preencha os campos obrigatórios e aceite o consentimento para continuar.";
      invalid[0].focus();
      return;
    }

    const data = new FormData(form);
    const lead = {
      name: sanitize(data.get("name"), 100),
      phone: sanitize(data.get("phone"), 20),
      region: sanitize(data.get("region"), 100),
      automotiveRole: sanitize(data.get("automotive_role"), 100),
      capital: sanitize(data.get("capital"), 100),
    };
    const attribution = readAttribution();
    pushEvent({
      event: "generate_lead",
      lead_type: "authorized_representative",
      automotive_role: lead.automotiveRole,
      capital_status: lead.capital,
      region: lead.region,
      ...attribution,
    });

    const origin = [attribution.utm_source, attribution.utm_medium, attribution.utm_campaign].filter(Boolean).join(" / ");
    const message = [
      "Olá, BDM. Preenchi a análise para representante autorizado.",
      "",
      `Nome: ${lead.name}`,
      `WhatsApp: ${lead.phone}`,
      `Cidade/região: ${lead.region}`,
      `Atuação automotiva: ${lead.automotiveRole}`,
      `Capital disponível: ${lead.capital}`,
      origin ? `Origem: ${origin}` : "",
      "",
      "Quero saber se minha região está disponível.",
    ].filter(Boolean).join("\n");
    error.textContent = "";
    window.location.assign(`https://wa.me/${PHONE}?text=${encodeURIComponent(message)}`);
  });
}
