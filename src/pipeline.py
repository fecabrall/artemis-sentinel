"""Main end-to-end AI-RPA pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.collectors.nasa_donki import fetch_space_weather_events
from src.collectors.nasa_power import fetch_nasa_power_data
from src.config import (
    DB_PATH,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    EMAIL_ENABLED,
    MISSION_NAME,
    MISSION_RANDOM_SEED,
    nasa_api_key_status,
)
from src.database import (
    init_db,
    new_run_id,
    save_alerts,
    save_email_notification,
    save_external_data,
    save_mission_summary,
    save_telemetry,
)
from src.intelligence.ml_anomaly_detector import analyze_telemetry_anomalies
from src.intelligence.risk_engine import calculate_risk_score
from src.intelligence.validators import validate_telemetry_dataframe
from src.logger import setup_logger
from src.notifications.email_report import send_mission_email
from src.reports.excel_report import generate_excel_report
from src.telemetry.simulator import generate_mission_telemetry
from src.utils.apollo_reference import inspect_apollo_reference
from src.utils.datetime_utils import utc_now_iso

logger = setup_logger(__name__)


def run_artemis_pipeline(samples: int = 120, anomaly_mode: bool = False) -> dict[str, Any]:
    """Run complete ARTEMIS Sentinel pipeline."""
    try:
        key_status = nasa_api_key_status()
        logger.info(
            "Starting ARTEMIS pipeline | mission=%s | anomaly_mode=%s | api_key_mode=%s",
            MISSION_NAME,
            anomaly_mode,
            key_status["mode"],
        )
        init_db()
        run_id = new_run_id()
        logger.info("Run ID created: %s", run_id)

        power_data = fetch_nasa_power_data()
        logger.info(
            "NASA POWER source=%s records_count=%s missing_ratio=%s fallback_reason=%s",
            power_data.get("source"),
            power_data.get("records_count"),
            power_data.get("missing_ratio"),
            power_data.get("fallback_reason"),
        )

        donki_data = fetch_space_weather_events()
        logger.info(
            "NASA DONKI source=%s event_count=%s max_class_type=%s fallback_reason=%s",
            donki_data.get("source"),
            donki_data.get("event_count"),
            donki_data.get("max_class_type"),
            donki_data.get("fallback_reason"),
        )

        seed = MISSION_RANDOM_SEED
        telemetry_df = generate_mission_telemetry(
            samples=samples,
            anomaly_mode=anomaly_mode,
            seed=seed,
        )
        apollo_reference = inspect_apollo_reference(Path.cwd())
        alerts_df = validate_telemetry_dataframe(telemetry_df)

        ml_result = analyze_telemetry_anomalies(
            telemetry_df,
            contamination=0.18 if anomaly_mode else None,
        )

        risk_result = calculate_risk_score(
            telemetry_df=telemetry_df,
            alerts_df=alerts_df,
            space_weather_data=donki_data,
            power_data=power_data,
        )

        summary_dict = {
            "run_id": run_id,
            "mission_name": MISSION_NAME,
            "generated_at": utc_now_iso(),
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "mission_status": risk_result["mission_status"],
            "critical_alerts": risk_result["critical_alerts"],
            "warning_alerts": risk_result["warning_alerts"],
            "info_alerts": risk_result["info_alerts"],
            "telemetry_samples": len(telemetry_df),
            "external_power_source": power_data.get("source"),
            "external_donki_source": donki_data.get("source"),
            "telemetry_source": "TELEMETRY_SIMULATED",
            "main_risk_factors": risk_result["main_risk_factors"],
            "anomaly_mode": anomaly_mode,
            "apollo_analysis_mode": apollo_reference.get("analysis_mode"),
            "data_mode": "SIMULATED_TELEMETRY_WITH_EXTERNAL_SOURCES",
            "email_enabled": EMAIL_ENABLED,
            **ml_result,
        }

        save_telemetry(telemetry_df, run_id)
        save_alerts(alerts_df, run_id)
        save_external_data(run_id, power_data, donki_data, apollo_reference)
        save_mission_summary(summary_dict, run_id)

        report_path = generate_excel_report(
            telemetry_df=telemetry_df,
            alerts_df=alerts_df,
            summary_dict=summary_dict,
            external_data_dict={
                "power_data": power_data,
                "donki_data": donki_data,
                "apollo_reference": apollo_reference,
            },
        )

        email_result = {"status": "skipped", "detail": "not triggered"}
        if EMAIL_ENABLED and (
            summary_dict["mission_status"] in {"NO-GO"} or summary_dict["risk_level"] == "CRITICAL"
        ):
            email_result = send_mission_email(summary_dict, report_path)
            save_email_notification(run_id, email_result["status"], email_result.get("detail", ""))
        summary_dict["email_status"] = email_result["status"]

        logger.info(
            "Pipeline completed | risk_score=%.2f risk_level=%s mission_status=%s report_path=%s database_path=%s",
            summary_dict["risk_score"],
            summary_dict["risk_level"],
            summary_dict["mission_status"],
            report_path,
            DB_PATH,
        )
        return {
            "summary": summary_dict,
            "telemetry": telemetry_df,
            "alerts": alerts_df,
            "power_data": power_data,
            "donki_data": donki_data,
            "apollo_reference": apollo_reference,
            "ml_result": ml_result,
            "report_path": report_path,
            "email_result": email_result,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline execution failed: %s", exc)
        raise
