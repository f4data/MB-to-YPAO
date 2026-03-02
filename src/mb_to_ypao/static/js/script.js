/* ═══════════════════════════════════════════════════════════════════
   MB-to-YPAO — Client-side logic
   ═══════════════════════════════════════════════════════════════════ */

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Get the AVR IP value from the input field. */
function getIp() {
    return document.getElementById("avr-ip").value.trim();
}

/**
 * Show a status box with a result.
 * @param {HTMLElement} box  - The .status-box element.
 * @param {boolean}     ok   - Whether the operation succeeded.
 * @param {string}      msg  - Message to display.
 */
function showStatus(box, ok, msg) {
    box.textContent = msg;
    box.className = "status-box " + (ok ? "ok" : "error");
}

/** Clear a status box. */
function clearStatus(box) {
    box.textContent = "";
    box.className = "status-box";
}

/**
 * Set a button into loading state and return a restore function.
 * @param {HTMLButtonElement} btn
 * @returns {() => void}
 */
function setLoading(btn) {
    const orig = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Working…';
    return () => {
        btn.innerHTML = orig;
        btn.disabled = false;
    };
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

async function checkStatus() {
    const ip = getIp();
    if (!ip) { alert("Please enter the AVR IP address first."); return; }

    const btn = document.getElementById("btn-check-status");
    const box = document.getElementById("status-connection");
    const restore = setLoading(btn);
    clearStatus(box);

    try {
        const res = await fetch("/api/check-status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip }),
        });
        const data = await res.json();
        showStatus(box, data.ok, data.message);
    } catch (err) {
        showStatus(box, false, "Network error: " + err.message);
    } finally {
        restore();
    }
}

async function preparePeqThrough() {
    const ip = getIp();
    if (!ip) { alert("Please enter the AVR IP address first."); return; }

    const btn = document.getElementById("btn-prepare-through");
    const box = document.getElementById("status-preparation");
    const restore = setLoading(btn);
    clearStatus(box);

    try {
        const res = await fetch("/api/prepare-peq-through", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip }),
        });
        const data = await res.json();
        showStatus(box, data.ok, data.message);
    } catch (err) {
        showStatus(box, false, "Network error: " + err.message);
    } finally {
        restore();
    }
}

async function prepareFromPeqFlat() {
    const ip = getIp();
    if (!ip) { alert("Please enter the AVR IP address first."); return; }

    const btn = document.getElementById("btn-prepare-flat");
    const box = document.getElementById("status-preparation");
    const restore = setLoading(btn);
    clearStatus(box);

    try {
        const res = await fetch("/api/prepare-from-peq-flat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip }),
        });
        const data = await res.json();
        showStatus(box, data.ok, data.message);
    } catch (err) {
        showStatus(box, false, "Network error: " + err.message);
    } finally {
        restore();
    }
}

async function applyFilters() {
    const ip = getIp();
    if (!ip) { alert("Please enter the AVR IP address first."); return; }

    const fileInput = document.getElementById("filter-file");
    if (!fileInput.files.length) { alert("Please select a filter file first."); return; }

    const btn = document.getElementById("btn-apply-filters");
    const box = document.getElementById("status-filters");
    const restore = setLoading(btn);
    clearStatus(box);

    const form = new FormData();
    form.append("ip", ip);
    form.append("file", fileInput.files[0]);

    try {
        const res = await fetch("/api/apply-filters", { method: "POST", body: form });
        const data = await res.json();
        showStatus(box, data.ok, data.message);

        // Populate verbose sections
        const inputPre = document.getElementById("verbose-input");
        const outputPre = document.getElementById("verbose-output");
        inputPre.textContent = data.input || "";
        outputPre.textContent = data.output || "";
    } catch (err) {
        showStatus(box, false, "Network error: " + err.message);
    } finally {
        restore();
    }
}

// ---------------------------------------------------------------------------
// Verbose toggle
// ---------------------------------------------------------------------------

function toggleVerbose() {
    const checked = document.getElementById("verbose-checkbox").checked;
    const content = document.getElementById("verbose-content");
    content.classList.toggle("visible", checked);
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("verbose-checkbox").addEventListener("change", toggleVerbose);
});
