"""
Security and Input Validation Tests for Pharmacy Iv Cleanroom Usp 797.
Tests for HMAC signature verification, input sanitization, and error handling.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestPHIGuardSecurity:
    """Tests for PHI outbound guard security features."""

    def test_phi_detection_mrn(self):
        """MRN patterns should be detected and blocked."""
        with pytest.raises(SecurityException) as exc_info:
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")
        # Ensure pattern details are not leaked in error message
        assert "pattern" not in str(exc_info.value).lower()

    def test_phi_detection_ssn(self):
        """SSN patterns should be detected and blocked."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phi_detection_phone(self):
        """Phone number patterns should be detected and blocked."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact: (555) 123-4567")

    def test_phi_detection_email(self):
        """Email patterns should be detected and blocked."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@hospital.org")

    def test_phi_redaction(self):
        """PHI redaction should replace sensitive data."""
        text = "Patient John Doe MRN-994827 has appointment"
        redacted = PHIGuard.redact_phi(text)
        assert "John Doe" not in redacted
        assert "MRN-994827" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted

    def test_clean_text_passes(self):
        """Clean clinical text should pass without exception."""
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Pressure differential 25.5 Pa within bounds")


class TestAuditTrailIntegrity:
    """Tests for HMAC-SHA256 audit trail integrity verification."""

    def test_audit_chain_integrity(self):
        """Audit trail should maintain chain integrity."""
        trail = AuditTrail(secret_key="test-secret-key-2026")
        trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
        trail.log("actor3", "tier1", "EVENT_3", {"data": "value3"})
        assert trail.verify_integrity() is True

    def test_audit_signature_verification(self):
        """HMAC signatures should be verified correctly."""
        trail = AuditTrail(secret_key="test-secret-key-2026")
        entry = trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
        # Signature should be a valid hex string
        assert len(entry["current_hash"]) == 64  # SHA256 hex length
        assert all(c in "0123456789abcdef" for c in entry["current_hash"])

    def test_audit_tamper_detection(self):
        """Tampered entries should fail integrity check."""
        trail = AuditTrail(secret_key="test-secret-key-2026")
        trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
        # Tamper with an entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False


class TestInputValidation:
    """Tests for input validation in SystemTaskPayload."""

    def test_control_characters_rejected(self):
        """Control characters in string fields should be rejected."""
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="TASK\x00INVALID", target_identifier="KEY-01", primary_metric=10.0)

    def test_nan_metric_rejected(self):
        """NaN metric values should be rejected."""
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=float("nan"))

    def test_inf_metric_rejected(self):
        """Infinite metric values should be rejected."""
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=float("inf"))

    def test_excessive_length_rejected(self):
        """Excessively long string fields should be rejected."""
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="T" * 200, target_identifier="KEY-01", primary_metric=10.0)

    def test_valid_payload_accepted(self):
        """Valid payload should be accepted."""
        payload = SystemTaskPayload(
            task_id="TASK-001",
            target_identifier="KEY-001",
            primary_metric=25.5,
            secondary_metric=10.0,
            status_descriptor="NOMINAL"
        )
        assert payload.task_id == "TASK-001"
        assert payload.primary_metric == 25.5

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace should be stripped from string fields."""
        payload = SystemTaskPayload(
            task_id="  TASK-001  ",
            target_identifier="  KEY-001  ",
            primary_metric=10.0,
            status_descriptor="  NOMINAL  "
        )
        assert payload.task_id == "TASK-001"
        assert payload.target_identifier == "KEY-001"
        assert payload.status_descriptor == "NOMINAL"


class TestBatchErrorHandling:
    """Tests for batch processing error handling."""

    def test_batch_skips_invalid_rows(self):
        """Batch processing should skip invalid rows and continue."""
        import tempfile
        import os

        # Create a malformed CSV
        csv_content = """task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor
TASK-01,KEY-01,28.4,14.2,True,DISCORDANT
TASK-02,KEY-02,INVALID,4.1,False,NOMINAL
TASK-03,KEY-03,35.0,19.5,True,ANOMALY"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            output_path = temp_path + '.out.csv'
            from cli import main
            result = main(["batch", "-i", temp_path, "-o", output_path])
            assert result == 0

            # Verify output was created with valid rows
            import csv
            with open(output_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                # Should have 2 valid rows (TASK-01 and TASK-03)
                assert len(rows) == 2
                assert rows[0]["task_id"] == "TASK-01"
                assert rows[1]["task_id"] == "TASK-03"
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestFrontierPayloadValidation:
    """Tests for FrontierPayload input validation."""

    def test_nan_metric_rejected(self):
        """NaN metric values should be rejected."""
        from usp_797_cleanroom.models import FrontierPayload
        with pytest.raises(ValueError):
            FrontierPayload("T1", "KEY-01", float("nan"), 5.0, "NOMINAL")

    def test_inf_metric_rejected(self):
        """Infinite metric values should be rejected."""
        from usp_797_cleanroom.models import FrontierPayload
        with pytest.raises(ValueError):
            FrontierPayload("T1", "KEY-01", 10.0, float("inf"), "NOMINAL")

    def test_valid_payload_accepted(self):
        """Valid payload should be accepted."""
        from usp_797_cleanroom.models import FrontierPayload
        payload = FrontierPayload("T1", "KEY-01", 25.5, 10.0, "NOMINAL")
        assert payload.task_id == "T1"
        assert payload.primary_metric == 25.5
