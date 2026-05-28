"""Excel report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from src.config import REPORTS_DIR
from src.utils.datetime_utils import utc_now_compact


def _format_sheet(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    sheet = writer.sheets[sheet_name]
    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for idx, column in enumerate(df.columns, start=1):
        col_letter = get_column_letter(idx)
        max_len = max(len(str(column)), *(len(str(v)) for v in df[column].astype(str).head(300)))
        sheet.column_dimensions[col_letter].width = min(max_len + 2, 45)


def generate_excel_report(
    telemetry_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
    summary_dict: dict[str, Any],
    external_data_dict: dict[str, Any] | None = None,
) -> str:
    """Generate multi-sheet Excel report and return file path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = utc_now_compact()
    run_id = str(summary_dict.get("run_id", ""))
    run_id_short = run_id.replace("-", "")[:8] if run_id else "no-runid"
    file_path = REPORTS_DIR / f"artemis_sentinel_report_{timestamp}_{run_id_short}.xlsx"

    power_data = (external_data_dict or {}).get("power_data", {})
    donki_data = (external_data_dict or {}).get("donki_data", {})
    apollo_reference = (external_data_dict or {}).get("apollo_reference", {})

    summary_row = dict(summary_dict)
    summary_row.setdefault("email_enabled", summary_dict.get("email_enabled", False))
    summary_row.setdefault("email_status", summary_dict.get("email_status", "skipped"))
    summary_df = pd.DataFrame([summary_row])

    external_summary_row = {
        "record_type": "external_summary",
        "run_id": summary_dict.get("run_id"),
        "generated_at": summary_dict.get("generated_at"),
        "mission_name": summary_dict.get("mission_name"),
        "power_source": power_data.get("source"),
        "power_latitude": power_data.get("latitude"),
        "power_longitude": power_data.get("longitude"),
        "power_records_count": power_data.get("records_count", len(power_data.get("records", []))),
        "power_missing_records": power_data.get("missing_records"),
        "power_missing_ratio": power_data.get("missing_ratio"),
        "power_fallback_used": power_data.get("fallback_used"),
        "power_fallback_reason": power_data.get("fallback_reason"),
        "donki_source": donki_data.get("source"),
        "donki_event_count": donki_data.get("event_count"),
        "donki_max_class_type": donki_data.get("max_class_type"),
        "donki_max_class_rank": donki_data.get("max_class_rank"),
        "donki_fallback_used": donki_data.get("fallback_used"),
        "donki_fallback_reason": donki_data.get("fallback_reason"),
        "apollo_folder_found": apollo_reference.get("apollo_folder_found"),
        "apollo_folder_path": apollo_reference.get("apollo_folder_path"),
        "apollo_files_count": apollo_reference.get("files_count"),
        "apollo_license_found": apollo_reference.get("license_found"),
        "apollo_readme_found": apollo_reference.get("readme_found"),
        "apollo_analysis_mode": apollo_reference.get("analysis_mode"),
    }
    event_rows = []
    for event in donki_data.get("events", []):
        event_rows.append(
            {
                "record_type": "donki_event",
                "run_id": summary_dict.get("run_id"),
                "event_id": event.get("event_id"),
                "begin_time": event.get("begin_time"),
                "peak_time": event.get("peak_time"),
                "class_type": event.get("class_type"),
                "source_location": event.get("source_location"),
                "active_region": event.get("active_region"),
            }
        )
    external_data_df = pd.DataFrame([external_summary_row, *event_rows])
    alerts_out = alerts_df if not alerts_df.empty else pd.DataFrame(columns=["severity", "metric", "message"])

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="mission_summary", index=False)
        telemetry_df.to_excel(writer, sheet_name="telemetry", index=False)
        alerts_out.to_excel(writer, sheet_name="alerts", index=False)
        external_data_df.to_excel(writer, sheet_name="external_data", index=False)
        _format_sheet(writer, "mission_summary", summary_df)
        _format_sheet(writer, "telemetry", telemetry_df)
        _format_sheet(writer, "alerts", alerts_out if not alerts_out.empty else pd.DataFrame({"info": ["no alerts"]}))
        _format_sheet(writer, "external_data", external_data_df)

    return str(Path(file_path))
