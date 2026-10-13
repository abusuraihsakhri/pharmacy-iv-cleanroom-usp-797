"""Security and regression tests for the illustrative audit application."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.llm_factory import LLMFactory
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from usp_797_cleanroom.models import FrontierPayload

client = TestClient(app)


def test_audit_records_are_not_public_by_default(monkeypatch):
    monkeypatch.delenv("AUDIT_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "anything"}).status_code == 403


def test_audit_record_requires_correct_token(monkeypatch):
    monkeypatch.setenv("AUDIT_READ_TOKEN", "sample-test-token")
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "wrong"}).status_code == 403
    response = client.get("/api/audit/logs", headers={"X-Audit-Token": "sample-test-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_sensitive_attributes_are_rejected_without_echo():
    data = {
        "task_id": "TASK-123",
        "target_identifier": "TARGET-A",
        "primary_metric": 4,
        "attributes": {"contact": "patient@example.org"},
    }
    response = client.post("/api/audit", json=data)
    assert response.status_code == 422
    assert "patient@example.org" not in response.text


def test_sensitive_attributes_are_rejected_by_supervisor():
    payload = SystemTaskPayload(
        task_id="TASK-123",
        target_identifier="TARGET-A",
        primary_metric=4,
        attributes={"phone": "(555) 123-4567"},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


def test_audit_log_snapshot_cannot_mutate_internal_ledger():
    trail = AuditTrail(secret_key="example-test-secret")
    trail.log("system", "service", "ACTION", {"status": "ok"})
    trail.get_trail()[0]["payload_hash"] = "forged"
    assert trail.verify_integrity()


def test_unimplemented_provider_never_pretends_to_connect():
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")
    assert "No clinical or regulatory verification" in LLMFactory.create("mock").invoke("Explain threshold")


def test_nonfinite_and_non_numeric_subsystem_input_rejected():
    for number in (float("nan"), float("inf"), "twelve", True):
        with pytest.raises(ValueError):
            FrontierPayload("TASK", "TARGET", number, 1, "NOMINAL")


def test_blank_task_id_and_control_characters_rejected():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="  ", target_identifier="KEY", primary_metric=1)
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="TASK\nINJECTED", target_identifier="KEY", primary_metric=1)


def test_root_serves_real_console():
    response = client.get("/")
    assert response.status_code == 200
    assert "Not a USP" in response.text
    assert "Math.random()" not in response.text


def test_browser_demonstration_has_no_signed_hash():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "audit_hash:null" in html
    assert "fetch(" in html
    assert "URL.createObjectURL" in html


def test_metrics_report_actual_latest_urgency():
    response = client.post("/api/audit", json={
        "task_id": "DEMO-METRICS", "target_identifier": "ZONE-A",
        "primary_metric": 1, "secondary_metric": 1,
        "status_descriptor": "NOMINAL", "is_critical_flag": True,
    })
    assert response.status_code == 200
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["system_status"] == "CRITICAL_STAT_PANIC"
