from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json

@dataclass
class FaceGeometry:
    shape: str
    length_width_ratio: float
    asymmetry: str
    jaw_tension: str
    styling_recommendations: Dict[str, str] = field(default_factory=dict)

@dataclass
class PersonalColor:
    cielab: Dict[str, float]
    seasonal_type: str
    undertone: str
    recommended_palette: List[str]
    eye_hair_match: str

@dataclass
class SkinScores:
    total_health: int
    radiance: int
    climate_adaptability: int
    vitality: int
    resilience: int

@dataclass
class IntegratedCuration:
    skincare_prescription: str
    makeup_prescription: str
    hair_prescription: str
    climate_adjustment: str

@dataclass
class ProfessionalBiometrics:
    skin_age: int
    ita: float
    skin_type: str
    skin_hex: str
    elasticity_score: float
    melanin_index: float
    erythema_index: float
    pore_density: str
    wrinkle_score: float
    age_range: str = "" 
    confidence_score: int = 100

@dataclass
class ExpertConsultation:
    summary: str
    skincare: str
    makeup: str
    hair: str

@dataclass
class GuardianRiskFilter:
    alert_level: str # Warning, Secure, High Risk
    makeup_oxidation_risk: str
    scalp_thermal_risk: str
    conflict_report: str
    blacklist_ingredients: List[str] = field(default_factory=list)

@dataclass
class ProfessionalDossier:
    medical_report: str
    makeup_strategy: str
    hair_architecture: str
    visual_prompt: str
    shampoo_prescription: str
    nutritional_advice: str

@dataclass
class FinalAction:
    risk_summary: str
    professional_tip: str
    offset_routine: List[str] = field(default_factory=list)

@dataclass
class TotalBeautyGuardianReport:
    version: str = "3.1.7-PRO"
    biometrics: Optional[ProfessionalBiometrics] = None
    face: Optional[FaceGeometry] = None
    color: Optional[PersonalColor] = None
    curation: Optional[IntegratedCuration] = None
    risks: Optional[GuardianRiskFilter] = None
    consult: Optional[ExpertConsultation] = None
    dossier: Optional[ProfessionalDossier] = None
    final_action: Optional[FinalAction] = None
    scores: Optional[SkinScores] = None
    reliability_message: Optional[str] = None
    image_type: str = "face"
    comparison: Optional[Dict[str, Any]] = None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
