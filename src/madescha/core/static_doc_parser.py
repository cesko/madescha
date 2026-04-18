import re
from difflib import SequenceMatcher

from madescha.core.datatypes import PersonOrOrganisation
def get_sender(letter: str, sender_guess: PersonOrOrganisation) -> PersonOrOrganisation:
    """
    Extracts the sender information from a letter using regex and heuristics.

    Attempts to find name, address, website and email in the letter text.
    Falls back to sender_guess values when information cannot be extracted.

    Args:
        letter: The full text content of the letter to analyze.
        sender_guess: An initial guess for the sender's details, used as
                      fallback values when information is missing in the letter.

    Returns:
        A PersonOrOrganisation instance populated with the extracted sender
        information, falling back to sender_guess values where unavailable.
    """
    name = _extract_name(letter) or sender_guess.name
    address = _extract_address(letter) or sender_guess.address
    website = _extract_website(letter) or sender_guess.website
    email = _extract_best_email(letter, sender_guess.email, sender_guess.name) or sender_guess.email

    return PersonOrOrganisation(
        name=name,
        address=address,
        website=website,
        email=email,
    )


def _similarity(a: str, b: str) -> float:
    """
    Computes a similarity score between two strings using SequenceMatcher.

    Args:
        a: First string.
        b: Second string.

    Returns:
        A float between 0.0 (no similarity) and 1.0 (identical).
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _score_email(email: str, guess_email: str, guess_name: str) -> float:
    """
    Scores an email address based on its similarity to the guessed email and name.

    Compares the local part and domain of the email against both the guessed
    email address and the guessed name to produce a combined similarity score.

    Args:
        email: The candidate email address to score.
        guess_email: The guessed email address for comparison.
        guess_name: The guessed name for comparison.

    Returns:
        A float score where higher values indicate a better match.
    """
    local, domain = email.split("@") if "@" in email else (email, "")
    full_email_score = _similarity(email, guess_email)
    local_name_score = _similarity(local, guess_name)
    domain_name_score = _similarity(domain.split(".")[0], guess_name)

    return max(full_email_score, local_name_score, domain_name_score)


def _extract_all_emails(text: str) -> list[str]:
    """
    Extracts all email addresses found in the text.

    Args:
        text: The text to search for email addresses.

    Returns:
        A list of all email addresses found in the text.
    """
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def _extract_best_email(text: str, guess_email: str, guess_name: str) -> str | None:
    """
    Extracts the most likely sender email from all emails found in the text.

    Scores each found email against the guessed email and name, returning
    the best match. Falls back to the first found email if no guess is available.

    Args:
        text: The text to search for email addresses.
        guess_email: The guessed email address to compare against.
        guess_name: The guessed name to compare against.

    Returns:
        The best matching email address, or None if no emails are found.
    """
    emails = _extract_all_emails(text)

    if not emails:
        return None

    # if no useful guess is available, fall back to first email
    if guess_email == "unknown" and guess_name == "unknown":
        return emails[0]

    return max(emails, key=lambda e: _score_email(e, guess_email, guess_name))


def _extract_website(text: str) -> str | None:
    """
    Extracts the first website/domain found in the text.

    Args:
        text: The text to search for a website.

    Returns:
        The first website domain found, or None if not found.
    """
    pattern = r"""
        (?:https?://)?           # optional scheme
        (?:www\.)?               # optional www
        ([a-zA-Z0-9\-]+          # domain name
        (?:\.[a-zA-Z0-9\-]+)*   # subdomains
        \.[a-zA-Z]{2,})          # TLD
        (?:/[^\s]*)?             # optional path
    """
    match = re.search(pattern, text, re.VERBOSE)
    return match.group(0).strip() if match else None


def _extract_address(text: str) -> str | None:
    """
    Extracts a German postal address (street + house number, postal code, city).

    Args:
        text: The text to search for an address.

    Returns:
        The first address found as a formatted string, or None if not found.
    """
    pattern = r"""
        ([A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ]?[a-zäöüß]+)*  # street name
        (?:straße|strasse|weg|allee|platz|gasse|ring|damm|ufer|chaussee|pfad)?  # optional street suffix
        \s+\d+[a-zA-Z]?)                                       # house number
        [,\s]+
        (\d{5})                                                # German postal code
        \s+
        ([A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ]?[a-zäöüß]+)*)  # city
    """
    match = re.search(pattern, text, re.VERBOSE)
    if match:
        street, postal_code, city = match.group(1), match.group(2), match.group(3)
        return f"{street.strip()}, {postal_code} {city.strip()}"
    return None


def _extract_name(text: str) -> str | None:
    """
    Attempts to extract the sender name from the beginning of the letter.

    Assumes the sender name appears in the first few lines before the address,
    and is typically a capitalized word or known organization suffix.

    Args:
        text: The text to search for a sender name.

    Returns:
        The extracted name, or None if not found.
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    org_pattern = r"""
        ^[A-ZÄÖÜ][a-zA-ZäöüÄÖÜß\s\-\.&]+  # starts with capital
        (?:GmbH|AG|KG|OHG|UG|e\.V\.|Inc\.|Ltd\.|Co\.|GbR)?  # optional legal suffix
        $
    """

    for line in lines[:5]:  # sender name is usually in the first few lines
        if re.match(org_pattern, line, re.VERBOSE):
            # skip lines that look like addresses or dates
            if not re.search(r"\d{5}|\d{1,2}\.\d{1,2}\.\d{4}|straße|strasse|weg\b", line, re.IGNORECASE):
                return line

    return None


if __name__ == "__main__":
    sample_letter = """
    TechCorp GmbH
    Musterstraße 42
    10115 Berlin
    info@techcorp.de
    www.techcorp.de

    An:
    Max Mustermann
    Beispielweg 1
    20095 Hamburg
    max.mustermann@gmail.com

    Berlin, 15. Januar 2024

    Sehr geehrter Herr Mustermann,

    wir freuen uns, Ihnen mitteilen zu können, dass Ihre Bestellung eingegangen ist.
    Bei Fragen wenden Sie sich an support@techcorp.de

    Mit freundlichen Grüßen,
    TechCorp GmbH
    """

    initial_guess = PersonOrOrganisation(
        name="TechCorp",
        address="unknown",
        website="unknown",
        email="info@techcorp.de"
    )

    sender = get_sender(sample_letter, initial_guess)
    print(f"Name:    {sender.name}")
    print(f"Address: {sender.address}")
    print(f"Website: {sender.website}")
    print(f"Email:   {sender.email}")

    print("\n--- All emails found ---")
    for email in _extract_all_emails(sample_letter):
        score = _score_email(email, initial_guess.email, initial_guess.name)
        print(f"  {email:<35} score: {score:.3f}")