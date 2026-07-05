# Fracdrop

App web multiusuario (**fracdrop.app**) que clasifica adjuntos de correos de Gmail
y los sube a carpetas de **Dropbox** según reglas definidas por el usuario.

> La app **solo lee** de las etiquetas de Gmail que el usuario marca como vigiladas.
> Nunca mueve, borra ni crea etiquetas ni correos. Toda la lógica vive en el backend;
> N8N solo dispara. Ver `specs.md` (fuente de verdad) y `claude.md`.

## Stack

| Capa            | Tecnología                                   |
|-----------------|----------------------------------------------|
| Frontend        | React 19 + Vite + TypeScript + TailwindCSS   |
| Backend         | FastAPI + Python 3.11                         |
| BD relacional   | MariaDB 10.6                                  |
| BD NoSQL        | MongoDB 7.0 *(4.4 en esta máquina — CPU sin AVX)* |
| Cache           | Redis 7.0                                     |
| Automatización  | N8N                                          |
| Contenedores    | Docker + Docker Compose                      |

## Estado

**Fase 1 — Esqueleto.** Estructura de carpetas, Docker Compose, `.env.example`,
Dockerfiles y stubs. Sin lógica de negocio todavía. Backend expone `/` y `/health`;
el frontend muestra una página placeholder.

## Arrancar

```bash
cp .env.example .env      # rellenar secretos (ver notas abajo)
docker-compose build
docker-compose up -d
```

Servicios:

| Servicio | URL                          |
|----------|------------------------------|
| Backend  | http://localhost:8000 (docs en `/docs`) |
| Frontend | http://localhost:5173        |
| N8N      | http://localhost:5678        |
| MariaDB  | localhost:3306               |
| MongoDB  | localhost:27017              |
| Redis    | localhost:6379               |

### Notas sobre `.env`

- **ENCRYPTION_KEY**: debe ser una clave Fernet válida. Genérala con:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- **SECRET_KEY**: `openssl rand -hex 32`
- Cambia todas las contraseñas `CHANGE_ME_*` antes de usar.

## Comandos útiles

```bash
docker-compose logs -f backend   # logs del backend
docker-compose ps                # estado de contenedores
docker-compose down              # parar
docker-compose down -v           # parar y BORRAR volúmenes (reset total)
```

## Estructura

```
backend/    FastAPI (app/ con api, models, schemas, services, utils)
frontend/   React + Vite (src/ con pages, components, hooks, services, types)
n8n-workflows/  Workflow disparador (process-labeled-emails.json)
```

Roadmap de fases en `claude.md`.
