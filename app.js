import { initNavigation } from "./modules/navigation.js";
import { initTestimonials } from "./modules/testimonials.js";
import { initAttribution } from "./modules/attribution.js";

document.documentElement.classList.add("js-ready");
initNavigation();
initTestimonials();
initAttribution();

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());
