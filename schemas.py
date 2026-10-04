from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"


class WaterAssessment(BaseModel):
    """Pydantic model representing visual-only ecosystem risk assessment.

    IMPORTANT: These scores represent visual environmental risk confidence only.
    They do NOT represent laboratory potable/drinkable safety probabilities.
    """

    risk_level: RiskLevel = Field(
        ...,
        description=(
            "Overall visual ecosystem risk level. LOW = no obvious indicators, "
            "MODERATE = some concern, ELEVATED = clear indicators, HIGH = severe indicators."
        ),
    )

    visually_safe: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Percentage confidence (0 to 100) that the water shows no obvious visible "
            "environmental contamination indicators. NOTE: A high score does NOT mean "
            "the water is potable, drinkable, or free from invisible pathogens/chemicals."
        ),
    )

    visually_risky: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Percentage confidence (0 to 100) that the image displays visible indicators "
            "associated with environmental contamination, pollution, or poor water quality."
        ),
    )

    image_quality: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Percentage confidence (0 to 100) that the image quality (resolution, lighting, "
            "clarity, focus, and perspective) is sufficient for meaningful visual assessment."
        ),
    )

    ai_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Overall AI confidence (0 to 100) in this assessment, factoring in image quality "
            "and clarity of visible indicators."
        ),
    )

    visible_evidence: List[str] = Field(
        default_factory=list,
        description=(
            "List of specific visual indicators detected in the image. "
            "Example: ['unusual discoloration', 'surface foam', 'floating debris']"
        ),
    )

    ai_detected_indicators: List[str] = Field(
        default_factory=list,
        description=(
            "List of citizen-style observation labels that the AI can confidently detect "
            "from the image. Use lowercase labels matching: unusual color, foam, floating waste, "
            "algae, oil/surface film, cloudiness/sediment, dead fish, sewage-like appearance."
        ),
    )

    description: str = Field(
        ...,
        description=(
            "Concise observational summary explaining visible findings. State what is and is not "
            "visible. Emphasize that this is a VISUAL ECOSYSTEM RISK assessment only, not a "
            "determination of drinking water safety. Do not make medical claims."
        ),
    )

    reasoning: str = Field(
        ...,
        description=(
            "Step-by-step explanation of how the AI reached this assessment. "
            "Describe the visual evidence, what was checked, and how confidence was calculated."
        ),
    )

    uncertainty_note: str = Field(
        ...,
        description=(
            "Clear statement of what this assessment CANNOT determine, including invisible "
            "contaminants (bacteria, viruses, heavy metals, pesticides, pH, salinity). "
            "State that human/laboratory verification is required for definitive conclusions."
        ),
    )

    recommended_action: str = Field(
        ...,
        description=(
            "Recommended next step for a human reviewer or citizen. Should reference "
            "human verification, field testing, or expert assessment as appropriate to risk level."
        ),
    )

    ecosystem_insight: str = Field(
        ...,
        description=(
            "Brief One Health ecosystem insight: potential environmental significance "
            "using cautious language. Do not claim proof of toxicity."
        ),
    )

    aquatic_life_note: str = Field(
        ...,
        description=(
            "Brief note on potential implications for aquatic life and biodiversity "
            "if these visual conditions persist. Use cautious, non-alarmist language."
        ),
    )

    human_wellbeing_note: str = Field(
        ...,
        description=(
            "Brief note on potential human exposure considerations. "
            "Do NOT make unsupported medical or toxicological claims. "
            "Focus on awareness and the need for verification."
        ),
    )
