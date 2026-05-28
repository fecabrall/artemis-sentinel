"""Streamlit dashboard for ARTEMIS Sentinel."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import EMAIL_ENABLED, nasa_api_key_status
from src.notifications.email_report import send_mission_email
from src.pipeline import run_artemis_pipeline
from src.reports.excel_report import generate_excel_report

st.set_page_config(page_title="ARTEMIS Sentinel", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0b1020; color: #e5e7eb; }
    .metric-box { padding: 0.8rem; border-radius: 0.8rem; background: #111827; border: 1px solid #1f2937; }
    .metric-box .value { font-size: 1.05rem; white-space: nowrap; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ARTEMIS Sentinel")
st.subheader("AI-RPA Mission Validation System")
st.caption(
    "Telemetria simulada e trajetória conceitual. NASA POWER e NASA DONKI são fontes externas reais. "
    "Não há cálculo orbital físico."
)

key_status = nasa_api_key_status()
st.sidebar.markdown(f"**NASA API:** `{key_status['mode']}`")


def _short_data_mode(summary: dict, power_data: dict, donki_data: dict) -> str:
    """Rótulo curto para card (evita quebra de linha)."""
    parts = ["SIM"]
    power_src = str(power_data.get("source", ""))
    donki_src = str(donki_data.get("source", ""))
    if "LIVE" in power_src or "LIVE" in donki_src:
        parts.append("NASA LIVE")
    elif power_src or donki_src:
        parts.append("NASA FB")
    return " + ".join(parts)


def _email_status_message(result: dict[str, str]) -> None:
    status = result.get("status", "unknown")
    if status == "skipped":
        st.info("E-mail: desabilitado (EMAIL_ENABLED=false).")
    elif status == "missing_config":
        st.warning("E-mail: configuração SMTP incompleta no `.env`.")
    elif status == "sent":
        st.success("E-mail enviado com sucesso.")
    elif status == "failed":
        st.error("E-mail: falha no envio (detalhe mascarado nos logs).")
    else:
        st.info(f"E-mail: {status}")


with st.sidebar:
    st.header("Configuração da missão")
    samples = st.slider("Número de amostras", min_value=40, max_value=400, value=120, step=10)
    anomaly_mode = st.checkbox("Ativar anomaly_mode", value=False)
    run_clicked = st.button("Executar Validação da Missão", width="stretch")
    report_clicked = st.button("Gerar Relatório Excel", width="stretch")
    if EMAIL_ENABLED:
        email_clicked = st.button("Enviar resumo por e-mail", width="stretch")
    else:
        email_clicked = False
        st.caption("E-mail desabilitado (EMAIL_ENABLED=false)")

if run_clicked:
    with st.spinner("Executando pipeline ARTEMIS..."):
        st.session_state["pipeline_result"] = run_artemis_pipeline(samples=samples, anomaly_mode=anomaly_mode)

result = st.session_state.get("pipeline_result")
if not result:
    st.info("Clique em **Executar Validação da Missão** para iniciar o fluxo.")
    st.stop()

summary = result["summary"]
telemetry_df: pd.DataFrame = result["telemetry"]
alerts_df: pd.DataFrame = result["alerts"]
ml_result = result.get("ml_result", {})
power_data = result.get("power_data", {})
donki_data = result.get("donki_data", {})
apollo_info = result.get("apollo_reference", {})

if report_clicked:
    report_path = generate_excel_report(
        telemetry_df=telemetry_df,
        alerts_df=alerts_df,
        summary_dict=summary,
        external_data_dict={
            "power_data": power_data,
            "donki_data": donki_data,
            "apollo_reference": apollo_info,
        },
    )
    st.session_state["manual_report_path"] = report_path
    st.session_state["excel_bytes"] = Path(report_path).read_bytes()
    st.session_state["excel_filename"] = Path(report_path).name
    st.success(f"Relatório Excel gerado com sucesso.")
    st.code(report_path, language=None)

if email_clicked:
    email_out = send_mission_email(
        summary,
        st.session_state.get("manual_report_path", result.get("report_path")),
    )
    _email_status_message(email_out)

status_colors = {
    "GO": "#22c55e",
    "GO WITH CAUTION": "#eab308",
    "WARNING": "#f97316",
    "NO-GO": "#ef4444",
}
mission_color = status_colors.get(str(summary["mission_status"]), "#a3a3a3")

if summary.get("mission_status") == "NO-GO":
    st.error(
        "Missão classificada como **NO-GO**. A trajetória continua sendo exibida apenas para "
        "análise simulada do perfil operacional."
    )

data_mode_full = summary.get("data_mode", "SIMULATED_TELEMETRY_WITH_EXTERNAL_SOURCES")
data_mode_short = _short_data_mode(summary, power_data, donki_data)

cols = st.columns(8)
cards = [
    ("Mission Status", summary["mission_status"]),
    ("Risk Level", summary["risk_level"]),
    ("Risk Score", summary["risk_score"]),
    ("Critical Alerts", summary["critical_alerts"]),
    ("Warning Alerts", summary["warning_alerts"]),
    ("Telemetry Samples", summary["telemetry_samples"]),
    ("Data Mode", data_mode_short),
    ("ML Anomaly Ratio", ml_result.get("ml_anomaly_ratio", summary.get("ml_anomaly_ratio", 0))),
]
for col, (label, value) in zip(cols, cards):
    color = mission_color if label == "Mission Status" else "#e5e7eb"
    title_attr = f' title="{data_mode_full}"' if label == "Data Mode" else ""
    col.markdown(
        f"<div class='metric-box'{title_attr}><strong>{label}</strong><br>"
        f"<span class='value' style='color:{color}'>{value}</span></div>",
        unsafe_allow_html=True,
    )

with st.expander("Detalhes técnicos do modo de dados", expanded=False):
    st.write({"data_mode": data_mode_full, "telemetry_source": summary.get("telemetry_source")})
    st.write({"power_source": power_data.get("source"), "donki_source": donki_data.get("source")})

st.markdown("### Visualização simulada da trajetória Terra → Lua")
st.warning(
    "Visualização conceitual para apoio operacional. Não representa cálculo orbital real."
)

max_min = int(telemetry_df["mission_elapsed_min"].max()) if not telemetry_df.empty else 1
selected_min = st.slider("Minuto da missão (trajetória)", 0, max_min, max_min)
row = telemetry_df[telemetry_df["mission_elapsed_min"] == selected_min].iloc[0] if not telemetry_df.empty else None

t_vals = telemetry_df["mission_elapsed_min"] / max(max_min, 1)
x_path = t_vals * 10
y_path = 2.5 * (t_vals - 0.5) ** 2
craft_x = float(selected_min / max(max_min, 1)) * 10
craft_y = float(2.5 * ((selected_min / max(max_min, 1)) - 0.5) ** 2)

fig_traj = go.Figure()
fig_traj.add_trace(go.Scatter(x=x_path, y=y_path, mode="lines", name="Trajetória", line=dict(color="#64748b", width=2)))
fig_traj.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text", text=["Terra"], name="Terra", marker=dict(size=18, color="#3b82f6")))
fig_traj.add_trace(go.Scatter(x=[10], y=[0], mode="markers+text", text=["Lua"], name="Lua", marker=dict(size=18, color="#94a3b8")))
fig_traj.add_trace(
    go.Scatter(
        x=[craft_x],
        y=[craft_y],
        mode="markers+text",
        text=["Nave"],
        name="Nave",
        marker=dict(size=16, color=mission_color),
    )
)
if row is not None:
    hover = (
        f"min={row['mission_elapsed_min']} | phase={row['phase']} | "
        f"battery={row['battery_percent']}% | oxygen={row['oxygen_percent']}% | "
        f"fuel={row['fuel_percent']}% | radiation={row['radiation_msv']} mSv | "
        f"latency={row['communication_latency_ms']} ms | signal={row['signal_strength_percent']}% | "
        f"risk={summary['risk_level']} | status={summary['mission_status']}"
    )
    fig_traj.add_annotation(x=craft_x, y=craft_y + 0.3, text=hover, showarrow=False, font=dict(size=10))
st.plotly_chart(fig_traj, width="stretch")

crit_cols = st.columns(4)
crit_cols[0].metric("Bateria atual", f"{row['battery_percent']}%" if row is not None else "—")
crit_cols[1].metric("Oxigênio atual", f"{row['oxygen_percent']}%" if row is not None else "—")
crit_cols[2].metric("Combustível atual", f"{row['fuel_percent']}%" if row is not None else "—")
crit_cols[3].metric("Fase atual", row["phase"] if row is not None else "—")

crit_cols2 = st.columns(4)
crit_cols2[0].metric("Radiação máxima", f"{telemetry_df['radiation_msv'].max():.3f} mSv")
crit_cols2[1].metric("Maior latência", f"{telemetry_df['communication_latency_ms'].max():.0f} ms")
crit_cols2[2].metric("Menor sinal", f"{telemetry_df['signal_strength_percent'].min():.1f}%")
crit_cols2[3].metric("Status atual", summary["mission_status"])

st.markdown("### Telemetria da missão")
st.plotly_chart(
    px.line(telemetry_df, x="mission_elapsed_min", y=["battery_percent", "oxygen_percent", "fuel_percent"], title="Bateria, Oxigênio e Combustível"),
    width="stretch",
)
st.plotly_chart(
    px.line(telemetry_df, x="mission_elapsed_min", y=["cabin_pressure_kpa", "cabin_temperature_c"], title="Pressão e Temperatura"),
    width="stretch",
)
st.plotly_chart(px.line(telemetry_df, x="mission_elapsed_min", y="radiation_msv", title="Radiação"), width="stretch")
st.plotly_chart(
    px.line(telemetry_df, x="mission_elapsed_min", y=["communication_latency_ms", "signal_strength_percent"], title="Latência e Sinal"),
    width="stretch",
)
st.plotly_chart(
    px.line(telemetry_df, x="mission_elapsed_min", y=["altitude_km", "velocity_m_s"], title="Altitude e Velocidade"),
    width="stretch",
)

st.markdown("### Alertas")
if alerts_df.empty:
    st.success("Sem alertas nesta execução.")
else:
    sev_count = alerts_df["severity"].value_counts().reset_index()
    sev_count.columns = ["severity", "count"]
    st.plotly_chart(px.bar(sev_count, x="severity", y="count", color="severity", title="Alertas por severidade"), width="stretch")
    st.dataframe(alerts_df, width="stretch")

st.markdown("### Fontes externas e inteligência local")
ext_col1, ext_col2, ext_col3 = st.columns(3)

with ext_col1:
    st.markdown("**NASA POWER**")
    st.write(
        {
            "source": power_data.get("source"),
            "latitude": power_data.get("latitude"),
            "longitude": power_data.get("longitude"),
            "records_count": power_data.get("records_count"),
            "missing_records": power_data.get("missing_records"),
            "missing_ratio": power_data.get("missing_ratio"),
            "fallback_used": power_data.get("fallback_used"),
            "fallback_reason": power_data.get("fallback_reason"),
        }
    )
with ext_col2:
    st.markdown("**NASA DONKI**")
    st.write(
        {
            "source": donki_data.get("source"),
            "event_count": donki_data.get("event_count"),
            "max_class_type": donki_data.get("max_class_type"),
            "max_class_rank": donki_data.get("max_class_rank"),
            "fallback_used": donki_data.get("fallback_used"),
            "fallback_reason": donki_data.get("fallback_reason"),
        }
    )
with ext_col3:
    st.markdown("**ML local (IsolationForest)**")
    st.write(ml_result)
    st.caption("Detecção de anomalias operacionais em telemetria simulada — não é predição orbital.")

with st.expander("Referência Apollo 11 (read-only)", expanded=False):
    if not apollo_info.get("apollo_folder_found"):
        st.info("Pasta Apollo 11 não encontrada. Não afeta o pipeline principal.")
    else:
        st.write(
            {
                "folder_found": apollo_info.get("apollo_folder_found"),
                "path": apollo_info.get("apollo_folder_path"),
                "files_count": apollo_info.get("files_count"),
                "license_found": apollo_info.get("license_found"),
                "readme_found": apollo_info.get("readme_found"),
                "analysis_mode": apollo_info.get("analysis_mode"),
            }
        )
        st.caption("Inventário histórico read-only — não executa código Apollo.")

report_path = st.session_state.get("manual_report_path", result.get("report_path"))
if report_path:
    st.markdown("### Relatório Excel")
    st.success(f"Arquivo: `{report_path}`")
    excel_bytes = st.session_state.get("excel_bytes")
    excel_name = st.session_state.get("excel_filename", Path(report_path).name)
    if excel_bytes is None and Path(report_path).exists():
        excel_bytes = Path(report_path).read_bytes()
        excel_name = Path(report_path).name
    if excel_bytes:
        st.download_button(
            label="Baixar relatório Excel",
            data=excel_bytes,
            file_name=excel_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
