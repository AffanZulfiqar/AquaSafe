from pydantic import BaseModel, Field


class WaterAssessment(BaseModel):
    """Pydantic model representing visual-only water safety assessment scores.
    
    IMPORTANT: These scores represent visual environmental risk confidence only.
    They do NOT represent laboratory potable/drinkable safety probabilities.
    """

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
