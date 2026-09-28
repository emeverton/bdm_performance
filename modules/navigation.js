export function initNavigation() {
  const button = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".main-nav");
  if (!button || !navigation) return;

  const close = () => {
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-label", "Abrir menu");
    navigation.dataset.open = "false";
  };

  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    button.setAttribute("aria-expanded", String(open));
    navigation.dataset.open = String(open);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) close();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && button.getAttribute("aria-expanded") === "true") {
      close();
      button.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (!navigation.contains(event.target) && !button.contains(event.target)) close();
  });
}
