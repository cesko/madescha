
from __future__ import annotations
import os
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from pypdf import PdfReader, PdfWriter

from madescha.core.datatypes import DocumentInfo

@dataclass
class PdfMetadata:
    """Metadata to be embedded into a PDF document."""

    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = field(default_factory=datetime.now)

    @staticmethod
    def fromDocumentInfo(doc_info:DocumentInfo) -> PdfMetadata:
        return PdfMetadata(
            title=doc_info.title,
            author=doc_info.author,
            subject=doc_info.title,
            keywords=doc_info.keywords,
            creation_date=datetime(doc_info.date.year, doc_info.date.month, doc_info.date.day)
        )
        

def apply_pdf_metadata(source_path: str, metadata: PdfMetadata) -> None:
    """
    Apply metadata tags to an existing PDF file in place.

    Args:
        source_path: Path to the PDF file to modify.
        metadata: Metadata object containing the tags to apply.
    """
    reader = PdfReader(source_path)
    writer = PdfWriter()

    # Copy all pages from the source
    for page in reader.pages:
        writer.add_page(page)

    # Copy existing metadata and overlay with new values
    existing_meta = reader.metadata or {}
    meta_dict: dict[str, str] = {**existing_meta}

    if metadata.title is not None:
        meta_dict["/Title"] = metadata.title
    if metadata.author is not None:
        meta_dict["/Author"] = metadata.author
    if metadata.subject is not None:
        meta_dict["/Subject"] = metadata.subject
    if metadata.keywords:
        meta_dict["/Keywords"] = ", ".join(metadata.keywords)
    if metadata.creator is not None:
        meta_dict["/Creator"] = metadata.creator
    if metadata.producer is not None:
        meta_dict["/Producer"] = metadata.producer
    if metadata.creation_date is not None:
        meta_dict["/CreationDate"] = metadata.creation_date.strftime("D:%Y%m%d%H%M%S")

    writer.add_metadata(meta_dict)

    # Write back to the same file
    with open(source_path, "wb") as output_file:
        writer.write(output_file)


def apply_file_tags_macos(file_path: str, tags: list[str]) -> None:
    """
    Apply Finder tags to a file on macOS using the 'tag' CLI tool.

    Requires the 'tag' tool: brew install tag

    Args:
        file_path: Path to the target file.
        tags: List of tag strings to apply.
    """
    if not tags:
        return
    subprocess.run(
        ["tag", "--add", ",".join(tags), file_path],
        check=True,
        capture_output=True,
    )


def apply_file_tags_windows(file_path: str, metadata: PdfMetadata) -> None:
    """
    Apply file tags on Windows using extended NTFS properties via win32com.

    Applies title, author, subject, keywords and creation date
    to the file's property store.

    Requires: pip install pywin32

    Args:
        file_path: Path to the target file.
        metadata: Metadata object containing the tags to apply.
    """
    try:
        from win32com.shell import shell, shellcon  # type: ignore
        import pywintypes  # type: ignore
    except ImportError as e:
        raise ImportError("pywin32 is required on Windows: pip install pywin32") from e

    abs_path = os.path.abspath(file_path)
    store = shell.SHGetPropertyStoreFromParsingName(
        abs_path, None, shellcon.GPS_READWRITE, shell.IID_IPropertyStore
    )

    property_map: dict[str, any] = {}

    if metadata.title is not None:
        property_map["System.Title"] = metadata.title
    if metadata.author is not None:
        property_map["System.Author"] = [metadata.author]
    if metadata.subject is not None:
        property_map["System.Subject"] = metadata.subject
    if metadata.keywords:
        property_map["System.Keywords"] = metadata.keywords
    if metadata.creation_date is not None:
        property_map["System.Document.DateCreated"] = pywintypes.Time(
            metadata.creation_date
        )

    for prop_name, value in property_map.items():
        pk = shell.PSGetPropertyKeyFromName(prop_name)
        pv = shell.InitPropVariantFromString(str(value)) if isinstance(value, str) else value
        store.SetValue(pk, pv)

    store.Commit()


def apply_file_tags_linux(file_path: str, metadata: PdfMetadata) -> None:
    """
    Apply file tags on Linux using the XDG standard extended attribute
    'user.xdg.tags', which is recognized across desktop environments
    (KDE, GNOME, XFCE, Cinnamon, etc.).

    Also applies Baloo-specific tags on KDE for Dolphin sidebar integration.

    Requires: pip install xattr

    Args:
        file_path: Path to the target file.
        metadata: Metadata object containing the tags to apply.
    """
    import xattr  # pip install xattr

    attrs = xattr.xattr(file_path)

    # --- XDG standard: cross-desktop tag support ---
    # Format: comma-separated list of tags
    # Recognized by Dolphin, Nautilus, Thunar, Nemo and others
    tags = [metadata.author]
    tags.extend(metadata.keywords)
    attrs["user.xdg.tags"] = ",".join(tags).encode("utf-8")

    # --- Additional XDG extended attributes for other metadata ---
    # attr_map: dict[str, Optional[str]] = {
    #     "user.xdg.comment": metadata.subject,
    #     "user.dublincore.title": metadata.title,
    #     "user.dublincore.creator": metadata.author,
    #     "user.dublincore.subject": metadata.subject,
    #     "user.dublincore.description": metadata.subject,
    # }
    # for key, value in attr_map.items():
    #     if value is not None:
    #         attrs[key] = value.encode("utf-8")


def apply_file_tags(file_path: str, metadata: PdfMetadata) -> None:
    """
    Apply OS-level file tags based on the current platform.

    - macOS:   Finder tags via the 'tag' CLI tool
    - Windows: NTFS extended properties via pywin32
    - Linux:   Extended attributes (xattr) via the xattr library

    Args:
        file_path: Path to the target file.
        metadata: Metadata object containing the tags to apply.
    """
    system = platform.system()

    if system == "Darwin":
        apply_file_tags_macos(file_path, metadata.keywords)
    elif system == "Windows":
        apply_file_tags_windows(file_path, metadata)
    elif system == "Linux":
        apply_file_tags_linux(file_path, metadata)
    else:
        print(f"File tagging is not supported on platform: {system}")
