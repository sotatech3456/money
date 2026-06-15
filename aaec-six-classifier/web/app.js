const form = document.querySelector("#classify-form");
const input = document.querySelector("#text-input");
const sampleButton = document.querySelector("#sample-button");
const results = document.querySelector("#results");
const legendList = document.querySelector("#legend-list");
const sentenceCount = document.querySelector("#sentence-count");
const statusRow = document.querySelector("#status-row");
const statusText = document.querySelector("#status-text");

const sampleText =
  "Although online education cannot replace every classroom experience, it can make learning more accessible. For example, students in rural areas can attend advanced courses without moving to a city. In recent years, schools have also improved digital tools for discussion and feedback. This means that online learning is not just convenient, but also socially important. Therefore, governments should support high-quality online education.";

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function percent(value) {
  return `${Math.round(value * 100)}%`;
}

function setStatus(message, isError = false) {
  statusRow.hidden = !message;
  statusText.textContent = message || "";
  statusRow.style.borderColor = isError ? "#dd7b7b" : "#f2c46d";
  statusRow.style.background = isError ? "#fff0f0" : "#fff8e8";
  statusRow.style.color = isError ? "#8b2020" : "#765113";
}

function renderLegend(labels) {
  legendList.className = "legend-list";
  legendList.innerHTML = labels
    .map(
      (label) => `
        <div class="legend-item ${label.key}">
          <div class="legend-title">
            <span>${escapeHtml(label.japanese)}</span>
            <span>${escapeHtml(label.display)}</span>
          </div>
          <p>${escapeHtml(label.description)}</p>
        </div>
      `,
    )
    .join("");
}

function renderResults(data) {
  sentenceCount.textContent = `${data.summary.sentence_count} sentences`;
  renderLegend(data.labels);

  results.innerHTML = data.sentences
    .map(
      (item) => `
        <article class="sentence-card ${item.label.key}">
          <p>${escapeHtml(item.text)}</p>
          <div class="meta">
            <span class="pill ${item.label.key}">${escapeHtml(item.label.japanese)} / ${escapeHtml(item.label.display)}</span>
            <span>confidence ${percent(item.confidence)}</span>
            <span>margin ${percent(item.margin)}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

async function classify(text) {
  const response = await fetch("/api/classify", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || data.error || "Classification failed");
  }
  return data;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Classifying...");
  try {
    const data = await classify(input.value);
    renderResults(data);
    setStatus(data.language.warning);
  } catch (error) {
    setStatus(error.message, true);
  }
});

sampleButton.addEventListener("click", () => {
  input.value = sampleText;
  form.requestSubmit();
});

form.requestSubmit();

