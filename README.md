# Análise Forense de Vídeos

Sistema de análise forense focado na detecção de descontinuidades, sincronia de áudio e espectrograma para validação de mídias.

## Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas em sua máquina antes de prosseguir com a instalação:
* **Python 3.10+**
* **Node.js** (para a interface web)
* **Banco de Dados** (MySQL)
* **Redis** (para fila de tarefas e cache)
* **FFmpeg** (requerido para o processamento de áudio/vídeo via Librosa)

## Instalação

1. Clone o repositório para a sua máquina local:
   ```bash
   git clone [https://github.com/SharyssaArs/AnaliseForenseVideos.git](https://github.com/SharyssaArs/AnaliseForenseVideos.git)
   cd AnaliseForenseVideos