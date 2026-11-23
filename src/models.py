from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class StartupRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"
    source_name: str
    source_url: str
    entityName: str
    employeeCount: Optional[int] = None
    collectedAt: str

class ProductRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"
    source_name: str
    source_url: str
    startupName: Optional[str] = None
    entityName: str
    pricingModel: Optional[str] = None
    collectedAt: str

class ResearchPaperRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"
    title: str
    authors: List[str] = Field(default_factory=list)
    paper_url: str
    github_url: Optional[str] = None
    github_stars: Optional[int] = None
    published_date: Optional[str] = None

class SignalRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str
    title: str
    company: Optional[str] = None
    url: str
    date: Optional[str] = None
    is_remote: Optional[bool] = None
    role_family: Optional[str] = None
    content: Optional[str] = None
