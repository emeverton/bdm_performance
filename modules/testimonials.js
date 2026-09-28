export function initTestimonials() {
  document.querySelectorAll(".story-play[data-video-id]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const id = link.dataset.videoId;
      if (!/^[a-zA-Z0-9_-]{11}$/.test(id || "")) return;
      event.preventDefault();
      const frame = document.createElement("iframe");
      frame.src = `https://www.youtube.com/embed/${id}?autoplay=1&rel=0`;
      frame.title = link.getAttribute("aria-label") || "Depoimento em vídeo";
      frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      frame.referrerPolicy = "strict-origin-when-cross-origin";
      frame.allowFullscreen = true;
      link.replaceWith(frame);
    });
  });
}
