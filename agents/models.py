"""
Pydantic v2 schemas and data definitions for Pharmacy Iv Cleanroom Usp 797.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier", min_length=1, max_length=128)
    target_identifier: str = Field(..., description="Non-identifying entity key", min_length=1, max_length=128)
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor", max_length=64)
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def sanitize_string_fields(cls, v: str) -> str:
        """Prevent control character injection in string fields."""
        if any(ord(c) < 32 or ord(c) == 127 for c in v):
            raise ValueError("Control characters not allowed in string fields")
        value = v.strip()
        if not value:
            raise ValueError("Identifier or descriptor must not be blank")
        return value

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_finite_metrics(cls, v: float) -> float:
        """Ensure numeric metrics are finite (not NaN or Inf)."""
        import math
        if not math.isfinite(v):
            raise ValueError("Metric values must be finite numbers")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "CAP / CLSI / ISO Standards"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "pharmacy-iv-cleanroom-usp-797"
    domain: str = "Clinical & Biomedical AI"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "CAP / CLSI / ISO Standards"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
