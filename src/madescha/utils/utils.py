import re
from urllib.parse import urlparse
import tldextract

from madescha.core.datatypes import PersonOrOrganisation

# Legal suffixes to remove for companies
LEGAL_SUFFIXES = [
    r'\bGmbH\s*&\s*Co\.\s*KG\b',
    r'\bGmbH\s*&\s*Co\b',
    r'\bGmbH\b',
    r'\bAG\b',
    r'\bKG\b',
    r'\bOHG\b',
    r'\bGbR\b',
    r'\bUG\s*\(haftungsbeschränkt\)\b',
    r'\bUG\b',
    r'\bmbH\b',
    r'\bInc\.\b',
    r'\bLtd\.\b',
    r'\bLLC\b',
    r'\bS\.A\.\b',
    r'\bSE\b',
    r'\be\.V\.\b',
    r'\be\.G\.\b',
]


def _extract_domain(website: str) -> str | None:
    """Extract the domain from a website URL or email address, stripping www. prefix and TLD.

    Args:
        website: The website URL, domain string, or email address.

    Returns:
        The cleaned domain name without TLD or None if extraction fails.
    """
    if not website or website == "unknown":
        return None

    # Handle email addresses by extracting the domain part
    if '@' in website:
        website = website.split('@')[-1]

    extracted = tldextract.extract(website)

    domain = extracted.domain

    return domain if domain else None


def _is_person(name: str) -> bool:
    """Heuristically determine if the name belongs to a person.
    
    Args:
        name: The name string to evaluate.
        
    Returns:
        True if the name likely belongs to a person, False otherwise.
    """
    # If it contains a legal suffix, it's an organisation
    for suffix in LEGAL_SUFFIXES:
        if re.search(suffix, name, re.IGNORECASE):
            return False
    
    # A person's name typically has exactly two words (first and last name)
    # and no special characters like &, -, numbers
    parts = name.strip().split()
    if len(parts) == 2 and all(p.isalpha() for p in parts):
        return True
    
    # Could also be "Vorname Zweiter Nachname" etc.
    # Heuristic: if it's 2-3 words and all alphabetical, likely a person
    if 2 <= len(parts) <= 3 and all(re.match(r'^[A-Za-zÄÖÜäöüß\-]+$', p) for p in parts):
        return True
    
    return False


def _person_short_name(name: str) -> str:
    """Generate a short name for a person like 'hmustermann'.
    
    Args:
        name: Full name of the person.
        
    Returns:
        Short name combining first letter of first name and full last name.
    """
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0].lower()
    
    first_name = parts[0]
    last_name = parts[-1]
    
    short = (first_name[0] + last_name).lower()
    # Remove any non-alphanumeric characters
    short = re.sub(r'[^a-z0-9]', '', short)
    return short


def _organisation_short_name(name: str) -> str:
    """Generate a short name for an organisation by stripping legal suffixes.
    
    Args:
        name: Full name of the organisation.
        
    Returns:
        Short name without legal suffixes, lowercased and stripped.
    """
    short = name.strip()
    
    for suffix in LEGAL_SUFFIXES:
        short = re.sub(suffix, '', short, flags=re.IGNORECASE)
    
    # Remove trailing punctuation and whitespace
    short = re.sub(r'[\s,.\-&]+$', '', short).strip()
    short = short.lower()
    # Replace spaces and special chars with empty string or underscore
    short = re.sub(r'\s+', '', short)
    short = re.sub(r'[^a-z0-9äöüß]', '', short)
    
    return short


def organisation_short_name(organisation: PersonOrOrganisation) -> str:
    """Generate a short identifier for a person or organisation.

    - If the entity has a valid website, the domain is used as the short name.
    - If it's a person, returns a combination of first letter of first name
      and last name (e.g. 'hmustermann' for 'Hermann Mustermann').
    - If it's an organisation, removes legal suffixes (GmbH, AG, etc.)
      and returns a cleaned version.

    Args:
        person_or_organisation: An instance of PersonOrOrganisation.

    Returns:
        A short string identifier for the given entity.
    """
    # Prefer domain from website if available
    domain = _extract_domain(organisation.website)
    if domain:
        return domain

    name = organisation.name

    return _organisation_short_name(name)
