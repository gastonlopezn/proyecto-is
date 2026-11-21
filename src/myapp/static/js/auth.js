document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const toggleBtn = document.querySelector("[data-toggle-password]");
  const form = document.querySelector("[data-auth-form]");
  const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

  if (emailInput && passwordInput) {
    if (emailInput.value.trim()) {
      passwordInput.focus();
    } else {
      emailInput.focus();
    }
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
        iconShow.hidden = isHidden;
        iconHide.hidden = !isHidden;
      }
    });
  }

  if (form && submitBtn) {
    form.addEventListener("submit", () => {
      submitBtn.disabled = true;
      submitBtn.textContent = "Signing in...";
    });
  }
});
