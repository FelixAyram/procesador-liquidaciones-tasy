/** Acceso privado — cambiá ACCESS_PIN_HASH generando SHA-256 de tu clave. */
export const ACCESS_PIN_HASH =
  "4cd35edd35af2afe7ec521949099e8de45783a63a0572c7c84c9db67f4adf654";

const STORAGE_KEY = "tasy_unlock_v1";

async function sha256(text) {
  const buffer = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(text)
  );
  return [...new Uint8Array(buffer)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function isUnlocked() {
  return sessionStorage.getItem(STORAGE_KEY) === "1";
}

export async function tryUnlock(pin) {
  const hash = await sha256(pin.trim());
  if (hash === ACCESS_PIN_HASH) {
    sessionStorage.setItem(STORAGE_KEY, "1");
    return true;
  }
  return false;
}

export function ensureAccess() {
  const overlay = document.getElementById("access-gate");

  if (isUnlocked()) {
    overlay.hidden = true;
    document.body.classList.remove("locked");
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const form = document.getElementById("access-form");
    const input = document.getElementById("access-pin");
    const error = document.getElementById("access-error");

    overlay.hidden = false;
    document.body.classList.add("locked");
    input.focus();

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.textContent = "";

      const ok = await tryUnlock(input.value);
      if (!ok) {
        error.textContent = "Clave incorrecta";
        input.select();
        return;
      }

      overlay.hidden = true;
      document.body.classList.remove("locked");
      resolve();
    });
  });
}
