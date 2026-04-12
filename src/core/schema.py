import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional

@dataclass
class BiometricData:
    ita_angle: float
    skin_type: str
    melanin_index: float
    erythema_index: float
    lab_values: Dict[str, float]

@dataclass
class EnvironmentData:
    location: str
    weather: Dict[str, float]  # temp, humidity, uv, aqi
    pore_clogging_rate: float # 0.0 to 1.0
    water_evaporation_rate: float # estimated TEWL

@dataclass
class InteractionReport:
    contraindications: List[str] = field(default_factory=list)
    synergies: List[str] = field(default_factory=list)
    risk_level: str = "Low"

@dataclass
class SideEffectPrediction:
    overall_risk_score: float # 0 to 10
    prediction_map: Dict[str, str] # ingredient -> risk (e.g., "High", "Medium", "Safe")
    high_risk_ingredients: List[str] = field(default_factory=list)

@dataclass
class VeriSkinAnalysisReport:
    version: str = "1.0.0"
    engine_name: str = "VeriSkin-Core-Engine"
    biometrics: BiometricData = None
    environment: EnvironmentData = None
    interaction: InteractionReport = None
    prediction: SideEffectPrediction = None

    def to_json(self):
        return json.dumps(asdict(self), indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Sample initialization for testing
    report = VeriSkinAnalysisReport()
    print(report.to_json())
