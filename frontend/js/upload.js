import { analyzeVideo, getStatus } from './api.js';

const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500 MB em bytes
const ALLOWED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];

let pollingInterval = null;

export function initUploadPage() {
    setupDragAndDrop();

    const form = document.getElementById('upload-form');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }
}

function setupDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('video-file');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
        }
    });
}

function validateFile(file) {
    if (!file) {
        return { isValid: false, message: "Por favor, selecione um arquivo." };
    }

    const fileName = file.name;
    const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
        return { isValid: false, message: "Formato não suportado." };
    }

    if (file.size > MAX_FILE_SIZE) {
        return { isValid: false, message: "Arquivo muito grande. O limite é de 500 MB." };
    }

    return { isValid: true, message: "" };
}

async function handleSubmit(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const fileInput = document.getElementById('video-file');
    const file = fileInput.files[0];

    hideError();
    submitBtn.disabled = true;

    const validation = validateFile(file);
    if (!validation.isValid) {
        showError(validation.message);
        submitBtn.disabled = false;
        return;
    }

    try {
        const response = await analyzeVideo(file);

        if (response && response.task_id) {
            startPolling(response.task_id);
        } else {
            throw new Error("O servidor não retornou um ID de tarefa válido.");
        }
    } catch (error) {
        showError("Erro de rede ao enviar o arquivo. Tente novamente.");
        submitBtn.disabled = false;
    }
}

function startPolling(taskId) {
    if (pollingInterval) clearInterval(pollingInterval);

    pollingInterval = setInterval(async () => {
        try {
            const statusResponse = await getStatus(taskId);

            updateProgressBar(statusResponse.progress || 0);

            if (statusResponse.status === 'completed') {
                clearInterval(pollingInterval);
                localStorage.setItem('task_id', taskId);
                window.location.href = 'result.html';

            } else if (statusResponse.status === 'failed') {
                clearInterval(pollingInterval);
                showError(statusResponse.error_message || "Ocorreu um erro durante a análise.");
                document.getElementById('submit-btn').disabled = false;
            }

        } catch (error) {
            console.error("Erro ao verificar o status:", error);
        }
    }, 5000);
}

function updateProgressBar(progressPercent) {
    const progressBar = document.getElementById('upload-progress');
    if (progressBar) {
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute('aria-valuenow', progressPercent);

        const statusMessage = document.getElementById('status-message');
        if (statusMessage) {
            statusMessage.textContent = `${progressPercent}%`;
        }
    }
}

function showError(message) {
    const errorDisplay = document.getElementById('error-area');
    if (errorDisplay) {
        errorDisplay.textContent = message;
        errorDisplay.style.display = 'block';
    }
}

function hideError() {
    const errorDisplay = document.getElementById('error-area');
    if (errorDisplay) {
        errorDisplay.textContent = '';
        errorDisplay.style.display = 'none';
    }
}

// Inicializa a página automaticamente
initUploadPage();