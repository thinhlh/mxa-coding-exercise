import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://mxa:mxa@localhost:5432/mxa")
os.environ.setdefault("KEYCLOAK_ISSUER", "http://localhost:8080/realms/mxa")
os.environ.setdefault("KEYCLOAK_AUDIENCE", "mxa-api")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
