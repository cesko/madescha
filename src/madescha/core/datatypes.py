from __future__ import annotations
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from enum import Enum

from madescha.utils.utils import organisation_short_name

# class PersonOrOrganisation(BaseModel):
#     name : str = Field("unkown", description="Name of Person or Organisation")
#     address: str = Field("unkown", description="Postal Address: Streetname and number, postal code, city")
#     website : str = Field("unkown", description="Website")

# class Date(BaseModel):
#     year : int = Field(0, description="Year")
#     month : int = Field(0, description="Month")
#     day : int = Field(0, description="Day of the month")

# class Document(BaseModel):
#     title : str = Field("unkown", description="Title of the document")
#     reference : str = Field("unknown", description="Contract number, membership number, customer number or similar.")
#     date : Date = Field( Date(), description="date of this document")
#     sender : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Sending person or organisation. This is the creator of the document")
#     receiver : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Receiving person. Usually addressed in the letter.")
#     keywords : list[str] = Field( [], description="List of keywords (1-3), e.g. 'invoice'")


class PersonOrOrganisation(BaseModel):
    name : str = Field("unknown", description="Name der Person oder Organisation")
    address: str = Field("unknown", description="Anschrift: Straße und Hausnummer, Postleitzahl, Stadt")
    website : str = Field("unknown", description="Website domain")
    email : str = Field("unknown", description="E-Mailadresse")

class Date(BaseModel):
    year : int = Field(0, description="Year")
    month : int = Field(0, description="Month")
    day : int = Field(0, description="Day of the month")

    def __str__(self) -> str:
        """
        Convert the date to a string in year-month-day format.

        Returns:
            A string representation of the date in 'YYYY-MM-DD' format.
        """
        return f"{self.year:04d}{self.month:02d}{self.day:02d}"

class Document(BaseModel):
    title : str = Field("unknown", description="Titel des Dokumentes. Bei Briefen der Betreff.")
    reference : str = Field("unknown", description="Vertragsnummer, Zeichen, Kundennummer oder ähnliches.")
    date : Date = Field( Date(), description="date of this document")
    sender : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Absender (Person oder Organisation). Dies ist der Ersteller / Autor des Briefes.")
    receiver : PersonOrOrganisation = Field( PersonOrOrganisation(), description="Empfänger. Das bin normalerweise ich oder meine Familie.")
    keywords : list[str] = Field( [], description="Schlüsselwörter, z.B. Rechnung, Strom, Steuern")


# class ShortName(BaseModel):
#     short_name: str = Field("unknown", description="Kurzversion eines Namens, insebsondere Firmennamen ohne GmbH etc. Ideal ist die Domain bzw. website ohne top-level-domain")

@dataclass
class OcrResult:
    text: str = ""
    success : bool = False
    message: str = ""

@dataclass
class LlmResult:
    document: Document = field(default_factory=Document)
    success : bool = False
    message : str = ""

@dataclass
class DocumentInfo:
    date : Date = field(default_factory=Date)
    author : str = "unknown"
    author_short : str = "unknown"
    title : str = "unknown"
    keywords: list[str] = field(default_factory=list)  # Fix: use field(default_factory=list)

    @staticmethod
    def fromDocument(doc:Document) -> DocumentInfo:
        return DocumentInfo(
            date = doc.date,
            author = doc.sender.name,
            author_short = organisation_short_name(doc.sender.name, doc.sender.website),
            title = doc.title,
            keywords = doc.keywords)


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