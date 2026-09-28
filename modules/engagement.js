function pushEvent(payload) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(payload);
  if (typeof window.gtag === "function") window.gtag("event", payload.event, payload);
  if (typeof window.fbq === "function") window.fbq("trackCustom", payload.event, payload);
}

export function initEngagement() {
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

  document.querySelectorAll(".story-play[data-video-id]").forEach((link) => {
    link.addEventListener("click", () => pushEvent({
      event: "bdm_testimonial_play",
      video_id: link.dataset.videoId || "",
      label: link.getAttribute("aria-label") || "",
    }), { once: true });
  });

  const finalSection = document.querySelector(".final-cta");
  if (!finalSection || !("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    pushEvent({ event: "bdm_final_cta_view" });
    observer.disconnect();
  }, { threshold: .45 });
  observer.observe(finalSection);
}
