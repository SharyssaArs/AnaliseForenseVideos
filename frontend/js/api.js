const BASE_URL = 'http://localhost:8000';

function handleHttpError(response) {
    const messages = {
        400: 'Requisição inválida. Verifique os dados enviados.',
        413: 'Arquivo muito grande. O limite é de 500 MB.',
        422: 'Dados inválidos. Verifique o formato do arquivo.',
        429: 'Muitas requisições. Aguarde um momento e tente novamente.',
        500: 'Erro interno do servidor. Tente novamente mais tarde.',
    };
    const message = messages[response.status] ?? `Erro inesperado: código ${response.status}.`;
    return { error: true, message };
}

async function analyzeVideo(file) {
    const formData = new FormData();
    formData.append('file', file);

    let response;
    try {
        response = await fetch(`${BASE_URL}/api/v1/analyze`, {
            method: 'POST',
            body: formData,
        });
    } catch {
        return { error: true, message: 'Sem conexão com o servidor.' };
    }

    if (!response.ok) {
        return handleHttpError(response);
    }

    const data = await response.json();
    if (data.task_id) {
        localStorage.setItem('task_id', data.task_id);
    }
    return data;
}

async function getStatus(taskId) {
    let response;
    try {
        response = await fetch(`${BASE_URL}/api/v1/status/${encodeURIComponent(taskId)}`);
    } catch {
        return { error: true, message: 'Sem conexão com o servidor.' };
    }

    if (!response.ok) {
        return handleHttpError(response);
    }

    return response.json();
}

async function getResult(taskId) {
    let response;
    try {
        response = await fetch(`${BASE_URL}/api/v1/result/${encodeURIComponent(taskId)}`);
    } catch {
        return { error: true, message: 'Sem conexão com o servidor.' };
    }

    if (!response.ok) {
        return handleHttpError(response);
    }

    return response.json();
}

export { analyzeVideo, getStatus, getResult };
export default { analyzeVideo, getStatus, getResult };
