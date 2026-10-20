"use strict";

// Client checks improve feedback; Django also validates every upload on the server.
const bookForm = document.querySelector("[data-book-form]");
if (bookForm) {
  const coverInput = bookForm.querySelector('input[type="file"]');
  const preview = document.querySelector("#cover-preview");
  const previewBox = document.querySelector(".cover-preview");
  const error = document.querySelector("#upload-error");
  let previewUrl = null;
  function validateCover() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    previewBox.hidden = true;
    preview.removeAttribute("src");
    error.hidden = true;
    coverInput.setCustomValidity("");
    const file = coverInput.files[0];
    if (!file) return true;
    let message = "";
    if (file.size > 5 * 1024 * 1024) message = "Выберите обложку размером до 5 МБ.";
    else if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) message = "Поддерживаются JPEG, PNG и WebP.";
    if (message) {
      error.textContent = message;
      error.hidden = false;
      coverInput.setCustomValidity(message);
      return false;
    }
    previewUrl = URL.createObjectURL(file);
    preview.src = previewUrl;
    previewBox.hidden = false;
    return true;
  }
  coverInput.addEventListener("change", validateCover);
  bookForm.addEventListener("submit", (event) => {
    if (!validateCover()) {
      event.preventDefault();
      coverInput.reportValidity();
    }
  });
}
