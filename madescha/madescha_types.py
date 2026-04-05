from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum

class PersonOrOrganisation(BaseModel):
    name : str = Field("unkown", description="Name of Person or Organisation")
    website : str = Field("unkown", description="Website")
    address: str = Field("unkown", description="Postal Address")

class Date(BaseModel):
    year : int = Field(0, description="Year")
    month : int = Field(0, description="Month")
    day : int = Field(0, description="Day of the month")

class Document(BaseModel):
    title : str = Field("unkown", description="Title of the document")
    date : Date = Field( Date(), description="date of this document")
    sender : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Sending person or organisation. Creator of the document")
    receiver : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Receiving person or organisation.")
    keywords : list[str] = Field( [], description="List of keywords (1-3), e.g. 'invoice'")

@dataclass
class OcrResult:
    text: str
    success : bool

@dataclass
class LlmResult:
    document_info: Document
    success : bool
    message : str

@dataclass
class DocumentFields:
    date : Date
    author : str
    title : str


@dataclass
class AutoProcessingStatus:
    success: bool
    status_message : str
    ocr_text : str = ""
    fields : DocumentFields


@dataclass
class MadeschaSettngs:
    pass