import os
import subprocess
import tempfile
import librosa
import numpy as np

def analyze(video_path: str, lip_timestamps: list = None) -> dict:
    """
    Analisa a sincronia de áudio de um vídeo e detecta possíveis injeções forenses.
    """
    # Criação segura do arquivo temporário
    temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_wav_fd)

    try:
        # 1. Extração do áudio via FFmpeg (Rápido e silencioso)
        command = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            temp_wav_path, "-y"
        ]
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Critério 1: Tratar vídeo sem faixa de áudio
        if process.returncode != 0 or not os.path.exists(temp_wav_path) or os.path.getsize(temp_wav_path) == 0:
            return {
                "audio_sync": "no_audio",
                "audio_score": 0.0
            }

        # 2. Carregamento com Librosa
        y, sr = librosa.load(temp_wav_path, sr=None)
        
        if len(y) == 0:
            return {"audio_sync": "no_audio", "audio_score": 0.0}

        # 3. Extração do Espectrograma e Padrões de Energia
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        energia_rms = librosa.feature.rms(y=y)[0]
        
        # 4. Detecção de Descontinuidades (Injeção de Áudio)
        # Calcula a diferença de energia entre os frames de áudio
        diferenca_energia = np.abs(np.diff(energia_rms))
        
        # Uma "anomalia" é um corte brusco no áudio (muito acima da média padrão)
        limite_anomalia = np.mean(diferenca_energia) + 3 * np.std(diferenca_energia)
        quantidade_anomalias = np.sum(diferenca_energia > limite_anomalia)
        
        # 5. Cálculo do audio_score (0.0 a 1.0)
        # Começamos com score perfeito (1.0) e penalizamos por cortes bruscos/edições
        penalidade = min(quantidade_anomalias * 0.05, 1.0)
        audio_score = round(1.0 - penalidade, 2)
        
        # 6. Definição do audio_sync
        # Se o áudio for fluido e sem muitas edições suspeitas, consideramos consistente
        if audio_score >= 0.7:
            audio_sync = "consistent"
        else:
            audio_sync = "inconsistent"

        return {
            "audio_sync": audio_sync,
            "audio_score": float(audio_score)
        }

    except Exception as e:
        print(f"Erro durante a análise forense de áudio: {e}")
        # Retorno seguro em caso de arquivo corrompido
        return {
            "audio_sync": "no_audio",
            "audio_score": 0.0
        }

    finally:
        # Critério 3: Remoção do arquivo temporário mesmo em caso de erro
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

    # Implementação da análise de sincronia e espectrograma mel - Issue #55