"""Run Lexi's FastAPI app in an isolated E2E test mode."""

from __future__ import annotations

import argparse
import atexit
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import uvicorn


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _postgres_database_url(admin_url: str, database_name: str) -> str:
    parsed = urlparse(admin_url)
    return urlunparse(parsed._replace(path=f"/{database_name}"))


def _connect_postgres(admin_url: str):
    import psycopg2

    connection = psycopg2.connect(admin_url)
    connection.autocommit = True
    return connection


def _ensure_docker_postgres(repo_root: Path) -> None:
    if os.environ.get("LEXI_E2E_SKIP_DOCKER_POSTGRES") == "1":
        return

    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "postgres"],
            cwd=repo_root,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "Could not start Docker Postgres for the E2E gate. Ensure Docker is "
            "installed and the Docker daemon is running, or set "
            "LEXI_E2E_SKIP_DOCKER_POSTGRES=1 when pointing "
            "LEXI_E2E_POSTGRES_ADMIN_URL at an already-running test Postgres."
        ) from exc


def _wait_for_postgres(admin_url: str) -> None:
    timeout_seconds = int(os.environ.get("LEXI_E2E_POSTGRES_TIMEOUT_SECONDS", "90"))
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            connection = _connect_postgres(admin_url)
            connection.close()
            return
        except Exception as exc:  # pragma: no cover - exercised by E2E harness timing
            last_error = exc
            time.sleep(1)

    raise RuntimeError(f"Postgres did not become ready within {timeout_seconds}s: {last_error}")


def _drop_postgres_database(admin_url: str, database_name: str) -> None:
    from psycopg2 import sql

    if not database_name.startswith("lexi_e2e_"):
        raise RuntimeError(
            "Refusing to drop a Postgres database whose name does not start with "
            f"'lexi_e2e_': {database_name}"
        )

    connection = _connect_postgres(admin_url)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                  AND pid <> pg_backend_pid()
                """,
                (database_name,),
            )
            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(database_name))
            )
    finally:
        connection.close()


def _create_postgres_database(admin_url: str, database_name: str) -> None:
    from psycopg2 import sql

    _drop_postgres_database(admin_url, database_name)

    connection = _connect_postgres(admin_url)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    finally:
        connection.close()


def _prepare_postgres_database(repo_root: Path, port: int) -> tuple[str, Callable[[], None]]:
    admin_url = os.environ.get(
        "LEXI_E2E_POSTGRES_ADMIN_URL",
        "postgresql://lexi:lexi@127.0.0.1:5432/postgres",
    )
    database_name = os.environ.get("LEXI_E2E_POSTGRES_DATABASE", f"lexi_e2e_{port}")

    _ensure_docker_postgres(repo_root)
    _wait_for_postgres(admin_url)
    _create_postgres_database(admin_url, database_name)

    return _postgres_database_url(admin_url, database_name), lambda: _drop_postgres_database(
        admin_url, database_name
    )


def _run_alembic_migrations(repo_root: Path) -> None:
    from alembic import command
    from alembic.config import Config

    alembic_config = Config(str(repo_root / "backend" / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(repo_root / "backend" / "alembic"))
    command.upgrade(alembic_config, "head")


def _prepare_environment(
    repo_root: Path,
    tmp_root: Path,
    database_mode: str,
    port: int,
) -> Callable[[], None]:
    upload_dir = tmp_root / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    frontend_port = os.environ.get("LEXI_E2E_FRONTEND_PORT", "3100")

    os.environ.setdefault("UPLOAD_TEMP_DIR", str(upload_dir))
    os.environ.setdefault(
        "CORS_ORIGINS",
        f'["http://127.0.0.1:{frontend_port}","http://localhost:{frontend_port}"]',
    )
    os.environ["LLM_PROVIDER"] = "fake"
    os.environ["LLM_MODEL_NAME"] = "fake-grounded-summary-v1"
    os.environ["RAG_VECTOR_BACKEND"] = "in_memory"
    os.environ["RAG_EMBEDDING_BACKEND"] = "deterministic"
    os.environ.setdefault("LOG_LEVEL", "WARNING")

    if database_mode == "sqlite":
        os.environ.setdefault("DATABASE_URL", f"sqlite:///{tmp_root / 'api.sqlite'}")
        return lambda: None

    if database_mode == "postgres":
        database_url, cleanup_database = _prepare_postgres_database(repo_root, port)
        os.environ["DATABASE_URL"] = database_url
        return cleanup_database

    raise ValueError(f"Unsupported E2E database mode: {database_mode}")


def _test_tmp_root() -> Path:
    configured_root = os.environ.get("LEXI_E2E_TMP_ROOT")
    if configured_root:
        tmp_root = Path(configured_root)
        shutil.rmtree(tmp_root, ignore_errors=True)
        tmp_root.mkdir(parents=True, exist_ok=True)
        return tmp_root

    return Path(tempfile.mkdtemp(prefix="lexi_playwright_api_"))


def _configure_app(repo_root: Path, database_mode: str):
    if database_mode == "postgres":
        _run_alembic_migrations(repo_root)

    from backend.celery_app import celery_app
    from backend.database import Base, engine
    from backend.main import app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True

    if database_mode == "sqlite":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    return app, engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8010, type=int)
    parser.add_argument(
        "--database",
        choices=("sqlite", "postgres"),
        default=os.environ.get("LEXI_E2E_DATABASE", "sqlite"),
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    sys.path.insert(0, str(repo_root))

    tmp_root = _test_tmp_root()
    cleanup_database = _prepare_environment(repo_root, tmp_root, args.database, args.port)
    try:
        app, engine = _configure_app(repo_root, args.database)
    except Exception:
        cleanup_database()
        shutil.rmtree(tmp_root, ignore_errors=True)
        raise
    cleaned = False

    def cleanup() -> None:
        nonlocal cleaned
        if cleaned:
            return
        cleaned = True
        engine.dispose()
        try:
            cleanup_database()
        finally:
            shutil.rmtree(tmp_root, ignore_errors=True)

    def stop(_signum, _frame) -> None:
        cleanup()
        raise SystemExit(0)

    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
