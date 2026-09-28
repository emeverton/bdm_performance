import { initNavigation } from "./modules/navigation.js";
import { initTestimonials } from "./modules/testimonials.js";
import { initAttribution } from "./modules/attribution.js";
import { initEngagement } from "./modules/engagement.js";

document.documentElement.classList.add("js-ready");
initNavigation();
initTestimonials();
initAttribution();
initEngagement();

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());
