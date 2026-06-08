from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    #VARIAVEIS AMBIENTE - DATABASE
    DATABASE_URL: str
    REDIS_URL: str
    #VARIAVEIS AMBIENTE - SEGURANÇA
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    #VARIAVEIS AMBIENTE - API
    REALITY_DEFENDER_API_KEY: str
    DEEPFAKE_THRESHOLD: float  = 0.50
    #VARIAVEIS AMBIENTE - UPLOAD
    MAX_FILE_SIZE_MB: int = 500
    UPLOAD_DIR: str
    #VARIAVEIS AMBIETE - APLICAÇÃO
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1/" # Caso precisar adicionar outra API - Prefixo das ROTAS API
    LOG_LEVEL: str = "INFO"
    # Se aparecer mais, durante o projeto declarar em seu "Tópico", se não se encaixar coloque "VARIAVEIS AMBIENTE - (nome)" e declare embaixo, posteriormente atualize em backend/.env.example também!

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
    
    #Validações -- 
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, value):
        if not value.startwith(("mysql://", "mysql+pymysql://root:root_password@localhost:3307/forensic_db")):
            raise ValueError("Erro, DATABASE_URL inválida")
        return value

    @field_validator("REDIS_URL")
    def validate_redis_url(cls, value):
        if not value.startwith(("redis://")):
            raise ValueError("Erro, REDIS_URL inválida")
        return value
    
    @field_validator("REALITY_DEFENDER_API")
    def validate_api_key(cls, value):
        if len(value.strip()) < 10: #Checa o Tamanho e Quantidade de Caractéres da KEY // Depois vai ter que mudar.
            raise ValueError("Erro, REALITY_DEFENDER_API inválida")
        return value

#Singleton 
settings = Settings()