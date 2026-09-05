"""
Data Models & Telemetry Definitions for USP-797 Sentinel: Sterile Compounding Cleanroom Environment & Beyond-Use-Date.
Domain: Hospital Pharmacy
Standard: USP <797> Pharmaceutical Compounding
"""
import datetime
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class ExecutionStatus(str, Enum):
    NOMINAL = "NOMINAL_OPTIMAL"
    ELEVATED_RISK = "ELEVATED_RISK_WARNING"
    CRITICAL_INTERVENTION = "CRITICAL_INTERVENTION_REQUIRED"


@dataclass
class FrontierPayload:
    task_id: str
    target_identifier: str
    primary_metric: float
    secondary_metric: float
    status_descriptor: str
    is_critical_flag: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.task_id, str) or len(self.task_id) > 128:
            raise ValueError("task_id must be a string with max length 128")
        if not isinstance(self.target_identifier, str) or len(self.target_identifier) > 128:
            raise ValueError("target_identifier must be a string with max length 128")
        if not isinstance(self.status_descriptor, str) or len(self.status_descriptor) > 64:
            raise ValueError("status_descriptor must be a string with max length 64")
        if not math.isfinite(self.primary_metric):
            raise ValueError("primary_metric must be a finite number")
        if not math.isfinite(self.secondary_metric):
            raise ValueError("secondary_metric must be a finite number")


@dataclass
class AgentTelemetryAlert:
    alert_id: str
    origin_agent: str
    status: ExecutionStatus
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "USP <797> Pharmaceutical Compounding"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "origin_agent": self.origin_agent,
            "status": self.status.value,
            "summary": self.summary,
            "technical_details": self.technical_details,
            "actionable_remediation": self.actionable_remediation,
            "standard_reference": self.standard_reference,
            "timestamp": self.timestamp,
        }
