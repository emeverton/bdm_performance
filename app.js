const ATTRIBUTION_KEY = "bdm_partner_attribution";
const ATTRIBUTION_FIELDS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "gbraid", "wbraid", "fbclid"];
const WHATSAPP_NUMBER = "5518997553071";

const sanitize = (value, max = 120) => String(value || "").replace(/[<>]/g, "").trim().slice(0, max);
const pushEvent = (event, values = {}) => {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...values });
};

function attribution() {
  const params = new URLSearchParams(window.location.search);
  let prior = {};
  try { prior = JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || "{}"); } catch (_) { /* session storage unavailable */ }
  const values = Object.fromEntries(ATTRIBUTION_FIELDS.map((key) => [key, sanitize(params.get(key) || prior[key]) ]));
  try { sessionStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(values)); } catch (_) { /* optional persistence */ }
  return values;
}

const storedAttribution = attribution();
document.querySelectorAll("[data-cta]").forEach((cta) => cta.addEventListener("click", () => {
  pushEvent("bdm_partner_cta_click", { cta_id: cta.dataset.cta, ...storedAttribution });
}));

document.querySelectorAll("details").forEach((item) => item.addEventListener("toggle", () => {
  if (item.open) pushEvent("bdm_faq_open", { question: sanitize(item.querySelector("summary").textContent, 120) });
}));

const finalSection = document.querySelector(".final");
if (finalSection && "IntersectionObserver" in window) {
  const observer = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    pushEvent("bdm_final_cta_view");
    observer.disconnect();
  }, { threshold: 0.4 });
  observer.observe(finalSection);
}

const form = document.querySelector("#partner-form");
const formError = document.querySelector("#form-error");
form?.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!form.checkValidity()) {
    formError.textContent = "Preencha os campos obrigatórios para continuar.";
    form.querySelector(":invalid")?.focus();
    return;
  }
  const values = new FormData(form);
  const lead = {
    name: sanitize(values.get("name"), 100),
    phone: sanitize(values.get("phone"), 20),
    region: sanitize(values.get("region"), 100),
    automotiveRole: sanitize(values.get("automotive_role"), 100),
    capitalStatus: sanitize(values.get("capital_status"), 100)
  };
  pushEvent("generate_lead", {
    lead_type: "authorized_representative",
    automotive_role: lead.automotiveRole,
    capital_status: lead.capitalStatus,
    region: lead.region,
    ...storedAttribution
  });
  const message = [
    "Olá, BDM. Quero ser um autorizado.", "",
    `Nome: ${lead.name}`,
    `WhatsApp: ${lead.phone}`,
    `Cidade e estado: ${lead.region}`,
    `Atuação no automotivo: ${lead.automotiveRole}`,
    `Capital: ${lead.capitalStatus}`
  ].join("\n");
  window.location.assign(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`);
});

document.querySelector("#year").textContent = new Date().getFullYear();
