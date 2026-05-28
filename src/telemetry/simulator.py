"""Synthetic telemetry generation for mission simulation."""

from __future__ import annotations

from datetime import timedelta
import random
from typing import Any

import pandas as pd

from src.config import MISSION_RANDOM_SEED
from src.utils.datetime_utils import utc_now

PHASES = [
    "PRE_LAUNCH",
    "LAUNCH",
    "TRANS_LUNAR_INJECTION",
    "CRUISE",
    "LUNAR_ORBIT",
    "DESCENT",
    "LANDING",
]


def _phase_for_index(index: int, total: int) -> str:
    segment = max(1, total // len(PHASES))
    phase_idx = min(index // segment, len(PHASES) - 1)
    return PHASES[phase_idx]


def generate_mission_telemetry(
    samples: int = 120,
    anomaly_mode: bool = False,
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate synthetic lunar mission telemetry."""
    effective_seed = seed if seed is not None else MISSION_RANDOM_SEED
    if effective_seed is not None:
        random.seed(effective_seed)

    if effective_seed is not None:
        # Base fixa para reprodutibilidade quando seed está definido.
        from datetime import datetime, timezone

        start_time = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc) - timedelta(minutes=samples)
    else:
        start_time = utc_now() - timedelta(minutes=samples)
    rows: list[dict[str, Any]] = []

    battery = 100.0
    oxygen = 100.0
    fuel = 100.0
    altitude = 0.0
    velocity = 0.0

    anomaly_points = set()
    if anomaly_mode and samples >= 10:
        anomaly_points = {
            samples // 3,
            samples // 2,
            int(samples * 0.7),
            samples - 8,
        }

    for i in range(samples):
        phase = _phase_for_index(i, samples)
        timestamp = start_time + timedelta(minutes=i)

        battery = max(5.0, battery - random.uniform(0.08, 0.24))
        oxygen = max(8.0, oxygen - random.uniform(0.05, 0.18))
        fuel = max(2.0, fuel - random.uniform(0.15, 0.5))

        cabin_pressure = random.uniform(97.0, 103.0)
        cabin_temp = random.uniform(20.0, 26.0)
        radiation = random.uniform(0.15, 0.7)
        signal = random.uniform(65.0, 100.0)
        engine_temp = random.uniform(420.0, 820.0)

        # Latência de comunicação (mais alta conforme distância/regime de missão).
        latency_ranges = {
            "PRE_LAUNCH": (300.0, 1400.0),
            "LAUNCH": (800.0, 2600.0),
            "TRANS_LUNAR_INJECTION": (1800.0, 4200.0),
            "CRUISE": (1500.0, 3600.0),
            "LUNAR_ORBIT": (1700.0, 4000.0),
            "DESCENT": (1300.0, 3300.0),
            "LANDING": (400.0, 1800.0),
        }
        latency_min, latency_max = latency_ranges.get(phase, (300.0, 2000.0))
        latency = random.uniform(latency_min, latency_max)

        if phase == "PRE_LAUNCH":
            velocity = max(0.0, random.uniform(0, 12))
            altitude = max(0.0, random.uniform(0, 0.4))
        elif phase == "LAUNCH":
            velocity += random.uniform(55, 120)
            altitude += random.uniform(2, 7)
        elif phase == "TRANS_LUNAR_INJECTION":
            velocity += random.uniform(80, 160)
            altitude += random.uniform(8, 20)
        elif phase == "CRUISE":
            velocity += random.uniform(-30, 50)
            altitude += random.uniform(15, 25)
        elif phase == "LUNAR_ORBIT":
            velocity += random.uniform(-80, 20)
            altitude += random.uniform(-3, 6)
        elif phase == "DESCENT":
            velocity += random.uniform(-110, -40)
            altitude += random.uniform(-8, -2)
        else:  # LANDING
            velocity += random.uniform(-60, -20)
            altitude += random.uniform(-3, 0.5)

        velocity = max(0.0, velocity)
        altitude = max(0.0, altitude)

        if i in anomaly_points:
            battery = max(2.0, battery - random.uniform(10, 20))
            radiation += random.uniform(0.9, 1.4)
            signal = max(5.0, signal - random.uniform(25, 45))
            engine_temp += random.uniform(220, 350)
            cabin_pressure -= random.uniform(12, 20)

        rows.append(
            {
                "timestamp": timestamp.isoformat(),
                "mission_elapsed_min": i,
                "phase": phase,
                "battery_percent": round(battery, 2),
                "oxygen_percent": round(oxygen, 2),
                "fuel_percent": round(fuel, 2),
                "cabin_pressure_kpa": round(cabin_pressure, 2),
                "cabin_temperature_c": round(cabin_temp, 2),
                "radiation_msv": round(radiation, 3),
                "communication_latency_ms": round(latency, 2),
                "signal_strength_percent": round(signal, 2),
                "engine_temperature_c": round(engine_temp, 2),
                "velocity_m_s": round(velocity, 2),
                "altitude_km": round(altitude, 2),
            }
        )

    return pd.DataFrame(rows)
