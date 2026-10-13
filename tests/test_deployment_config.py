"""Basic deploy-configuration checks."""
from pathlib import Path

def test_dockerfile_runs_unprivileged_and_does_not_copy_secrets():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    ignore = Path(".dockerignore").read_text(encoding="utf-8")
    assert "USER appuser" in dockerfile
    assert ".env" in ignore
    assert ".git" in ignore

def test_compose_requires_external_key_and_local_bind():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "127.0.0.1:8000:8000" in compose
    assert "${AUDIT_SECRET_KEY:?" in compose
    assert "prod-audit-key" not in compose
