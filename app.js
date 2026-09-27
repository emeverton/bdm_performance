"use strict";
// Review only: no backend requests, no personal data in analytics and no lead event.
window.dataLayer = window.dataLayer || [];
const track = (event, data = {}) => window.dataLayer.push({ event, environment: "review", ...data });
track("view_lp");
document.querySelectorAll("[data-intent]").forEach((element) => {
  element.addEventListener("click", () => {
    const intent = element.dataset.intent === "b2b" ? "b2b" : "b2c";
    track("cta_click", { intent });
    const select = document.querySelector('select[name="intent"]');
    if (select) select.value = intent;
  });
});
const form = document.querySelector("form[data-preview]");
if (form) {
  form.addEventListener("focusin", () => track("form_start"), { once: true });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const intent = form.elements.namedItem("intent").value === "b2b" ? "b2b" : "b2c";
    track("preview_form_submit", { intent });
    const status = document.getElementById("form-status");
    if (status) status.textContent = "Simulação concluída. Nenhum dado foi enviado e nenhum atendimento foi iniciado.";
    form.reset();
  });
}
