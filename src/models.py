from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class MarginConfig(BaseModel):
    inner: float
    outer: float
    top: float
    bottom: float

class PrinterProfile(BaseModel):
    description: str
    paper_size: str
    width_mm: float
    height_mm: float
    margins: MarginConfig
    edge_index_mode: Literal["safe", "bleed"] = "safe"
    duplex_offset_x: float = 0.0

class PrinterProfiles(BaseModel):
    profiles: Dict[str, PrinterProfile]

class AnnualEvent(BaseModel):
    name: str
    month: Optional[int] = None
    day: Optional[int] = None
    rule: Optional[str] = None # e.g. "3rd Mon Jan", "easter"

class DatedEvent(BaseModel):
    name: str
    date: str # ISO 8601 YYYY-MM-DD
    icon: Optional[str] = None # Optional icon override

class SpecialDays(BaseModel):
    annual: List[AnnualEvent] = []
    birthdays: List[DatedEvent] = []
    anniversaries: List[DatedEvent] = []
    education: List[DatedEvent] = []
    other: List[DatedEvent] = []

class UserData(BaseModel):
    start_year: int = 2026
    num_years: int = 8
    special_days: SpecialDays
