# Capstone-ai-agent

This repository contains a FastAPI-based project that uses LangChain, Google generative APIs, Ollama and connects to a MySQL database. The project is dockerized and can be run locally using Docker Compose.

## Contents

 - `docker-compose.yml` — defines `app` (the FastAPI service) and `db` (MySQL 8.0).
 - `Dockerfile` — builds a Python 3.13-based image and runs `uvicorn main:app` on port 8000.
 - `requirements.txt` — Python dependencies.
 - `main.py` — FastAPI application entrypoint.

## Quick start (Docker)

Prerequisites:

 - Docker Desktop installed and running (recommended WSL2 backend on Windows).
 - Docker Compose (comes with Docker Desktop).
 - Optional: a Google API key if you use Google Generative APIs in the application.

1. Open PowerShell and change to the project root (where `docker-compose.yml` exists).

2. (Optional) Set `GOOGLE_API_KEY` in the current PowerShell session:

```powershell
$env:GOOGLE_API_KEY = 'your_google_api_key_here'
```

Or create a `.env` file in the project root with:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

3. Build and start the services (foreground):

```powershell
docker-compose up --build
```

To run in the background (detached):

```powershell
docker-compose up --build -d
```

4. Visit the running API at:

http://localhost:8000

MySQL will be available at `localhost:3306` with credentials from `docker-compose.yml`:

 - user: `user`
 - password: `password`
 - database: `capstone_db`

To stop and remove containers:

```powershell
docker-compose down
```

To remove containers and volumes (drops MySQL data):

```powershell
docker-compose down -v

## Run (detailed)

This project can be run several ways depending on whether you want the DB started and whether you want to run only the `app` service.

- Start everything (app + db) — default Compose behavior:

```powershell
docker-compose up --build
```

- Start in detached/background mode:

```powershell
docker-compose up --build -d
```

- Start only the `app` service (Compose will not start `db`):

```powershell
docker-compose up --build app
```

- Start only the `app` service and explicitly skip dependencies (useful when you don't want `db` started at all):

```powershell
docker-compose up --build --no-deps app
```

- Build the `app` image then run it manually (no Compose networking; useful for quick debugging):

```powershell
docker build -t capstone-app .
docker run --rm -p 8000:8000 -e PORT=8000 -e GOOGLE_API_KEY='your_key_here' capstone-app
```

Notes:
- If you run `app` without `db`, the service will start but the application may fail at runtime if it attempts to connect to MySQL on startup. Consider using `--no-deps` only for testing or when the app has lazy DB initialization.
- To prevent MySQL from binding to your host's port 3306 (and avoid conflicts), remove the `ports:` mapping for `db` in `docker-compose.yml` and use `expose: - "3306"` instead — other containers on the same Compose network can still reach it by service name `db`.

## Fixes to be aware of

- The Dockerfile previously used the JSON exec form for CMD with a literal `${PORT}`. That form does not expand shell variables and caused uvicorn to see the string `${PORT}` (invalid). The Dockerfile has been updated to run uvicorn using the shell form so `${PORT}` expands at runtime and defaults to `8000` if unset.

```

## Environment variables

The Docker Compose file exposes these environment variables for the `app` service:

 - `MYSQL_HOST` (set to `db`)
 - `MYSQL_USER` (default: `user`)
 - `MYSQL_PASSWORD` (default: `password`)
 - `MYSQL_DATABASE` (default: `capstone_db`)
 - `GOOGLE_API_KEY` (pulled from host env or `.env` file)

If your application requires additional secrets (for Ollama, Google, etc.), provide them via a `.env` file or your environment.

## Development notes

 - The `Dockerfile` installs `default-libmysqlclient-dev` and build tools so Python packages requiring native extensions can build.
 - Starting the app uses `uvicorn main:app --host 0.0.0.0 --port 8000` so FastAPI is reachable from the host.

## Troubleshooting

 - Docker not running: start Docker Desktop and ensure the daemon is running.
 - Port conflicts: if `8000` or `3306` are in use, update `docker-compose.yml` ports before starting.
 - Long builds / pip failures: large dependencies may take time; ensure your machine has a stable internet connection.
 - Database initialization errors: check logs with `docker-compose logs db`.
 - App logs: `docker-compose logs -f app`

Specific common errors and actions

- Error: Invalid value for '--port': '${PORT}' is not a valid integer.
	- Cause: Dockerfile used JSON exec form; `${PORT}` wasn't expanded. Fix: rebuild after the Dockerfile change (the repo already contains the fix).

- Error: Ports are not available: exposing port TCP 0.0.0.0:3306 ...
	- Cause: another service/process is bound to port 3306 on the host.
	- Quick fixes:
		- Stop the local MySQL service or other app using 3306.
		- Change the host mapping in `docker-compose.yml` from `3306:3306` to another host port (e.g., `3307:3306`).
		- Remove the `ports:` mapping for the `db` service and use `expose: - "3306"` so MySQL is reachable only to other containers.


## Next improvements (optional)

 - Add a healthcheck for the `app` service to wait for the DB to be ready.
 - Add `.env.example` (included in this repo) and update docs with exact required variables.
 - Add automated tests to validate container startup.

## Files added

 - `.env.example` — example env variables to copy to `.env`.

---

If you want, I can also add a healthcheck/wait-for-db script and update `docker-compose.yml` to include it. Tell me which additions you'd like.