function sanitizeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const taskId = localStorage.getItem("task_id");

if (!taskId) {
  window.location.href = "./upload.html";
}

let result;

try {
  result = JSON.parse(localStorage.getItem("analysis_result"));
} catch {
  result = null;
}

result = result || {
  score: 82,
  is_deepfake: true,
  manipulation_type: "Manipulação facial",
  audio_sync: "Inconsistência entre áudio e vídeo",
  metadata_flags: ["camera_model_absent", "timestamp_modified", "encoding_suspicious"],
  forensic_details: "Foram identificadas inconsistências visuais, sinais de edição e alterações nos metadados do arquivo.",
  layer_scores: {
    visual: 82,
    audio: 64,
    metadata: 75,
    compression: 58
  }
};

renderResult(result);

function renderResult(result) {
  renderScoreCard(result);
  renderText("manipulation-type", result.manipulation_type || "Não informado");
  renderText("audio-sync", result.audio_sync || "Não informado");
  renderText("forensic-details", result.forensic_details || "Nenhum detalhe disponível");
  renderMetadataFlags(result.metadata_flags || []);
  renderBreakdown(result.layer_scores || {});
}

function renderScoreCard(result) {
  const scoreCard = document.getElementById("score-card");
  const score = Number(result.score ?? 0);
  const isDeepfake = result.is_deepfake === true;

  scoreCard.classList.add(isDeepfake ? "perigo" : "sucesso");

  scoreCard.innerHTML = `
    <h2>${isDeepfake ? "Deepfake detectado" : "Vídeo autêntico"}</h2>
    <p class="score-percentage">${sanitizeHTML(score)}%</p>
    <p>${isDeepfake ? "Há indícios de manipulação." : "Não há indícios relevantes de manipulação."}</p>
  `;
}

function renderText(elementId, value) {
  const element = document.getElementById(elementId);
  element.innerHTML = `<p>${sanitizeHTML(value)}</p>`;
}

function renderMetadataFlags(flags) {
  const container = document.getElementById("metadata-flags");
  container.innerHTML = "";

  flags.forEach((flag) => {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = flag;
    container.appendChild(badge);
  });
}

function renderBreakdown(scores) {
  setBar("visual-score", scores.visual);
  setBar("audio-score", scores.audio);
  setBar("metadata-score", scores.metadata);
  setBar("compression-score", scores.compression);
}

function setBar(elementId, value) {
  const bar = document.getElementById(elementId);
  const score = Math.max(0, Math.min(100, Number(value ?? 0)));

  bar.style.width = `${score}%`;
  bar.textContent = `${score}%`;
}