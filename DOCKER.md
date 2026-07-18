# Docker Deployment

Run the Retro Quiz app locally on your machine with Docker.

## Prerequisites
- Docker & docker-compose installed
- Ports **3000** (frontend), **8001** (backend), **27017** (mongo) free

## Setup
1. From the project root run:
   ```bash
   docker-compose up --build
   ```
2. Open http://localhost:3000

The `docker-compose.yml` starts three services:
- **mongo** — MongoDB 7 with a persistent volume `mongo_data`
- **backend** — FastAPI on port 8001
- **frontend** — React (production build served by nginx) on port 3000

## Environment
The compose file passes required env vars to the backend automatically:
- `MONGO_URL=mongodb://mongo:27017`
- `DB_NAME=retro_quiz`
- `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `EMERGENT_LLM_KEY`, `FRONTEND_URL`

Edit `docker-compose.yml` to change secrets or point the frontend at a custom domain.

## Stop / cleanup
```bash
docker-compose down          # stop containers, keep data
docker-compose down -v       # stop and delete mongo data
```
