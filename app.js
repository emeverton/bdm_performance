const PHONE = "5518997553071";
const CONSENT_KEY = "bdm_measurement_consent";
const ATTRIBUTION_KEY = "bdm_attribution";

function sanitize(value, limit = 120) {
  return String(value || "").slice(0, limit).replace(/[<>]/g, "").trim();
}

function pushEvent(payload) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(payload);

  let consent = "denied";
  try { consent = localStorage.getItem(CONSENT_KEY) || "denied"; } catch {}

  if (consent !== "granted") return;
  if (typeof window.gtag === "function") window.gtag("event", payload.event, payload);
  if (typeof window.fbq === "function") {
    if (payload.event === "generate_lead") window.fbq("track", "Lead", payload);
    else window.fbq("trackCustom", payload.event, payload);
  }
}

function initNavigation() {
  const button = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".main-nav");
  if (!button || !nav) return;

  const close = () => {
    button.setAttribute("aria-expanded", "false");
    nav.dataset.open = "false";
  };

  button.addEventListener("click", () => {
    const next = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(next));
    nav.dataset.open = String(next);
  });

  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) close();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      close();
      button.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (!button.contains(event.target) && !nav.contains(event.target)) close();
  });
}

function initAttribution() {
  const params = new URLSearchParams(window.location.search);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "gbraid", "wbraid", "fbclid"];

  let stored = {};
  try { stored = JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || "{}"); } catch {}

  const attribution = {};
  for (const key of keys) {
    attribution[key] = sanitize(params.get(key) || stored[key] || "", 120);
  }

  attribution.landing_path = sanitize(stored.landing_path || window.location.pathname, 160);
  try {
    attribution.referrer_host = sanitize(stored.referrer_host || (document.referrer ? new URL(document.referrer).hostname : "direct"), 100);
  } catch {
    attribution.referrer_host = "direct";
  }

  try { sessionStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(attribution)); } catch {}

  document.querySelectorAll('a[href="#qualificacao"]').forEach((link) => {
    link.addEventListener("click", () => {
      const section = link.closest("section")?.id || (link.closest("header") ? "header" : "footer");
      const ctaId = link.dataset.ctaId || section + "_cta";
      pushEvent({
        event: "bdm_partner_cta_click",
        event_id: typeof crypto.randomUUID === "function" ? crypto.randomUUID() : Date.now() + "_" + ctaId,
        conversion_destination: "whatsapp",
        cta_id: ctaId,
        section,
        label: link.textContent.trim(),
        ...attribution,
      });
    });
  });
}

function readAttribution() {
  try { return JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || "{}"); }
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
      try { localStorage.setItem(CONSENT_KEY, value); } catch {}
      banner.hidden = true;
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: "consent_update", analytics_storage: value, ad_storage: value });
    });
  });
}

function initFaq() {
  document.querySelectorAll(".faq-list details").forEach((item, index) => {
    item.addEventListener("toggle", () => {
      if (!item.open) return;
      pushEvent({
        event: "bdm_faq_open",
        faq_index: index + 1,
        faq_question: item.querySelector("summary")?.textContent.trim() || "",
      });
    });
  });
}

function initFinalView() {
  const section = document.querySelector(".qualification-section");
  if (!section || !("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    pushEvent({ event: "bdm_final_cta_view" });
    observer.disconnect();
  }, { threshold: 0.35 });

  observer.observe(section);
}

function initQualification() {
  const form = document.querySelector("#partner-form");
  const error = document.querySelector("#form-error");
  if (!form || !error) return;

  form.querySelectorAll("input, select").forEach((field) => {
    const clear = () => field.setAttribute("aria-invalid", "false");
    field.addEventListener("input", clear);
    field.addEventListener("change", clear);
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const required = [...form.querySelectorAll("[required]")];
    const invalid = required.filter((field) => !field.checkValidity());

    required.forEach((field) => {
      field.setAttribute("aria-invalid", invalid.includes(field) ? "true" : "false");
    });

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
      "Nome: " + lead.name,
      "WhatsApp: " + lead.phone,
      "Cidade/região: " + lead.region,
      "Atuação automotiva: " + lead.automotiveRole,
      "Capital disponível: " + lead.capital,
      origin ? "Origem: " + origin : "",
      "",
      "Quero saber se minha região está disponível.",
    ].filter(Boolean).join("\n");

    error.textContent = "";
    window.location.assign("https://wa.me/" + PHONE + "?text=" + encodeURIComponent(message));
  });
}

document.documentElement.classList.add("js-ready");
initNavigation();
initAttribution();
initConsent();
initFaq();
initFinalView();
initQualification();

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());
