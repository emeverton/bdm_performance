"use strict";

document.documentElement.classList.add("js-ready");

const hero = document.querySelector(".hero");
const heroVideo = document.querySelector(".hero-video");
if (hero && heroVideo) {
  const canPlayHero = window.matchMedia("(min-width: 761px) and (prefers-reduced-motion: no-preference)");
  const syncHeroVideo = () => {
    if (canPlayHero.matches) {
      if (!heroVideo.getAttribute("src")) {
        heroVideo.src = heroVideo.canPlayType('video/webm; codecs="vp9"') ? heroVideo.dataset.srcWebm : heroVideo.dataset.src;
      }
      heroVideo.play().catch(() => {});
    } else {
      heroVideo.pause();
      heroVideo.removeAttribute("src");
      heroVideo.load();
      hero.classList.remove("is-video-ready");
    }
  };
  heroVideo.addEventListener("playing", () => hero.classList.add("is-video-ready"));
  canPlayHero.addEventListener("change", syncHeroVideo);
  syncHeroVideo();
}

const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector(".main-nav");

if (menuButton && navigation) {
  const closeMenu = () => {
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Abrir menu");
    navigation.dataset.open = "false";
  };

  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    navigation.dataset.open = String(open);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menuButton.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (!navigation.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
  });
}

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());

// Carrega o player somente quando a pessoa decide assistir ao depoimento.
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

// Evento pronto para GTM e contexto de campanha enviado na própria conversa.
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
