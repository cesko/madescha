from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from enum import Enum

class PersonOrOrganisation(BaseModel):
    name : str = Field("unkown", description="Name of Person or Organisation")
    address: str = Field("unkown", description="Postal Address: Streetname and number, postal code, city")
    website : str = Field("unkown", description="Website")

class Date(BaseModel):
    year : int = Field(0, description="Year")
    month : int = Field(0, description="Month")
    day : int = Field(0, description="Day of the month")

class Document(BaseModel):
    title : str = Field("unkown", description="Title of the document")
    reference : str = Field("unknown", description="Contract number, membership number, customer number or similar.")
    date : Date = Field( Date(), description="date of this document")
    sender : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Sending person or organisation. This is the creator of the document")
    receiver : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Receiving person. Usually addressed in the letter.")
    keywords : list[str] = Field( [], description="List of keywords (1-3), e.g. 'invoice'")

@dataclass
class OcrResult:
    text: str = ""
    success : bool = False
    message: str = ""

@dataclass
class LlmResult:
    document_info: Document
    success : bool
    message : str

@dataclass
class DocumentInfo:
    date : Date = field(default_factory=Date)
    author : str = "unknown"
    title : str = "unknown"


@dataclass
class AutoProcessingStatus:
    running: bool
    success: bool
    status_message : str
    fields : DocumentInfo = None
    ocr_text : str = ""


@dataclass
class MadeschaSettngs:
    pass