document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-auth-form]");
  const passwordInput = document.getElementById("password");
  const toggleBtn = document.querySelector("[data-toggle-password]");
  const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

  if (form) {
    const focusOrder = [
      document.getElementById("name"),
      document.getElementById("email"),
      passwordInput,
    ].filter(Boolean);

    const firstEmpty = focusOrder.find((input) => !input.value.trim());
    (firstEmpty || focusOrder[focusOrder.length - 1])?.focus();
  }

  if (toggleBtn && passwordInput) {
    const iconShow = toggleBtn.querySelector("[data-icon-show]");
    const iconHide = toggleBtn.querySelector("[data-icon-hide]");

    toggleBtn.addEventListener("click", () => {
      const isHidden = passwordInput.type === "password";
      passwordInput.type = isHidden ? "text" : "password";
      toggleBtn.setAttribute("aria-pressed", String(isHidden));
      toggleBtn.setAttribute(
        "aria-label",
        isHidden ? "Hide password" : "Show password",
      );

      if (iconShow && iconHide) {
        iconShow.toggleAttribute("hidden", isHidden);
        iconHide.toggleAttribute("hidden", !isHidden);
      }
    });
  }

  if (form && submitBtn) {
    form.addEventListener("submit", () => {
      submitBtn.disabled = true;
      const loadingText = submitBtn.getAttribute("data-loading-text");
      if (loadingText) {
        submitBtn.textContent = loadingText;
      }
    });
  }
});
