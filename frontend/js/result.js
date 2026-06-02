const METADATA_FLAGS_TRANSLATION = {
    camera_model_absent: "Modelo de câmera ausente"
};

const MANIPULATION_TYPE_TRANSLATION = {
    face_swap: "Troca de rosto"
};

const AUDIO_SYNC_TRANSLATION = {
    inconsistent: "Áudio dessincronizado",
    inconsistente: "Áudio dessincronizado"
};

function sanitizeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export function initResultPage() {
    fetchAndRenderResult();
}

export async function fetchAndRenderResult() {
    const taskId = localStorage.getItem("task_id");

    if (!taskId) {
        showResultError("Nenhuma análise encontrada.");
        return;
    }

    try {
        const result = await api.getResult(taskId);

        renderScoreCard(result);
        renderMetadataFlags(result.metadata_flags || result.metadata_flag || []);
        renderForensicDetails(result);

    } catch (error) {
        console.error("Erro ao carregar resultado:", error);
        showResultError("Erro ao carregar o resultado da análise.");
    }
}

export function renderScoreCard(result) {
    const scoreCard = document.getElementById("score-card");

    if (!scoreCard) return;

    const isDeepfake = result.is_deepfake === true;
    const text = isDeepfake ? "Deepfake detectado" : "Video autentico";

    scoreCard.classList.remove("perigo", "sucesso");
    scoreCard.classList.add(isDeepfake ? "perigo" : "sucesso");

    scoreCard.innerHTML = `
        <h2>${sanitizeHTML(text)}</h2>
    `;
}

export function renderMetadataFlags(flags) {
    const container = document.getElementById("metadata-flags");

    if (!container) return;

    container.innerHTML = "";

    const flagsList = Array.isArray(flags) ? flags : [flags];

    flagsList.forEach((flag) => {
        const translatedFlag = METADATA_FLAGS_TRANSLATION[flag] || flag;

        const badge = document.createElement("span");
        badge.classList.add("badge");
        badge.innerHTML = sanitizeHTML(translatedFlag);

        container.appendChild(badge);
    });
}

export function renderForensicDetails(result) {
    const container = document.getElementById("forensic-details");

    if (!container) return;

    const manipulationKey =
        result.manipulation_type ||
        result["manipulação_type"];

    const audioSyncKey = result.audio_sync;

    const manipulationText =
        MANIPULATION_TYPE_TRANSLATION[manipulationKey] ||
        manipulationKey ||
        "Não informado";

    const audioSyncText =
        AUDIO_SYNC_TRANSLATION[audioSyncKey] ||
        audioSyncKey ||
        "Não informado";

    container.innerHTML = `
        <p>
            <strong>${sanitizeHTML("Tipo de manipulação")}:</strong>
            ${sanitizeHTML(manipulationText)}
        </p>

        <p>
            <strong>${sanitizeHTML("Sincronia do áudio")}:</strong>
            ${sanitizeHTML(audioSyncText)}
        </p>
    `;
}

function showResultError(message) {
    const container = document.getElementById("result-container");

    if (!container) return;

    container.innerHTML = `
        <div class="card perigo">
            <h2>${sanitizeHTML("Erro")}</h2>
            <p>${sanitizeHTML(message)}</p>
        </div>
    `;
}
