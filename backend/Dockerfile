FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /app

# Copia dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Cria usuário não-root
RUN useradd -m appuser

# Define usuário da aplicação
USER appuser

# Expõe porta da API
EXPOSE 8000

# Inicia FastAPI
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Construir a imagem Docker
# docker build -t forensic-api .

# Executar o container mapeando a porta 8000
#docker run -d -p 8000:8000 --name forensic-container fore