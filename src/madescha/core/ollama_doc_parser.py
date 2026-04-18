import ollama

from madescha.core.datatypes import PersonOrOrganisation, Date, Document

class OllamaDocumentParser:

    def __init__(self, model:str = "phi4-mini"):
        self._model = model

    def _generate_system_prompt(self, response_scheme:str) -> dict:
        return {
            "role": "system",
            "content": (
                f"You extract information as requested from documents."
                f"Very Important: Always respond with valid JSON only! Only respeond with JSON matching this exact schema: {response_scheme}." 
                f"No explanation or extra text."
            )
        }
    
    def _chat(self, message, repsonse_class:type):
        response = ollama.chat(
            model = self._model,
            messages=[
                self._generate_system_prompt(repsonse_class.model_json_schema()),
                {
                    "role": "user",
                    "content": message,
                }
            ],
            format=repsonse_class.model_json_schema(),
            think=False,
            options={
                #"temperature": 0,  # More deterministic output
            },
        )
    
        try:
            result = repsonse_class.model_validate_json(response.message.content)
            return result
        except Exception as e:
            print(f"UNABLE TO PARSE: {response.message.content}")
            print(f"Error: {e}")
            return repsonse_class()
    
    def get_sender(self, content:str) -> PersonOrOrganisation:
        organisation = self._chat(f"Get the sender of this document:\n\n {content}", PersonOrOrganisation)
        return organisation


    def get_receiver(self, content:str) -> PersonOrOrganisation:
        organisation = self._chat(f"Get the receiver of this document:\n\n {content}", PersonOrOrganisation)
        return organisation


    def get_document_info(self, content:str) -> Document:
        document = self._chat(f"Extract title, date, sender, receiver and keywords from this document\n\n {content}", Document)
        return document
    

if __name__ == "__main__":

    example_content = """
Stadtwerke Musterstadt GmbH
Energiestraße 42
12345 Musterstadt
Telefon: 0123 456-0
E-Mail: service@stadtwerke-musterstadt.de
www.stadtwerke-musterstadt.de

Musterstadt, 15. Januar 2025
Herrn
Max Mustermann
Hauptstraße 7
12345 Musterstadt

Betreff: Ihre Jahresstromrechnung 2024 – Kundennummer 987654321

Sehr geehrter Herr Mustermann,
vielen Dank, dass Sie Ihren Strom bei den Stadtwerken Musterstadt beziehen. Anbei erhalten Sie Ihre Jahresabrechnung für den Zeitraum vom 01. Januar 2024 bis zum 31. Dezember 2024.
Für den genannten Abrechnungszeitraum ergibt sich für Sie eine Nachzahlung in Höhe von 118,92 Euro. Wir bitten Sie, diesen Betrag bis zum 15. Februar 2025 auf unser unten genanntes Konto zu überweisen.
Bitte beachten Sie außerdem, dass wir Ihren monatlichen Abschlag ab dem 01. Februar 2025 auf 97,00 Euro anpassen werden. Diese Anpassung basiert auf Ihrem tatsächlichen Verbrauch im vergangenen Jahr.
Bei Fragen zu Ihrer Rechnung stehen wir Ihnen gerne zur Verfügung:

📞 Telefon: 0123 456-100 (Mo–Fr, 8–18 Uhr)
📧 E-Mail: abrechnung@stadtwerke-musterstadt.de
🌐 Online: www.stadtwerke-musterstadt.de/meinbereich

Mit freundlichen Grüßen
Stadtwerke Musterstadt GmbH
Abteilung Kundenservice


Stromrechnung / Abrechnung
Stadtwerke Musterstadt GmbH | Energiestraße 42 | 12345 Musterstadt
HRB 12345 | Amtsgericht Musterstadt | USt-IdNr.: DE123456789
Geschäftsführer: Dr. Anna Beispiel

Kundendaten
Copy table







Kunde:
Max Mustermann


Lieferadresse:
Hauptstraße 7, 12345 Musterstadt


Kundennummer:
987654321


Vertragsnummer:
V-2019-00456


Zählernummer:
Z-88776655


Tarif:
Stadtwerke Klassik Strom


Abrechnungszeitraum:
01.01.2024 – 31.12.2024


Rechnungsdatum:
15.01.2025


Rechnungsnummer:
RE-2025-0034512



Verbrauchsermittlung
Copy table



Zählerstand
Datum



Anfangsstand
12.450 kWh
01.01.2024


Endstand
15.220 kWh
31.12.2024


Verbrauch
2.770 kWh




Kostenaufstellung (netto)
Copy table


Position
Menge
Preis
Betrag



Arbeitspreis
2.770 kWh
0,2890 €/kWh
800,53 €


Grundpreis
12 Monate
9,50 €/Monat
114,00 €


Netzentgelt (Arbeit)
2.770 kWh
0,0720 €/kWh
199,44 €


Netzentgelt (Leistung)
12 Monate
4,20 €/Monat
50,40 €


Konzessionsabgabe
2.770 kWh
0,0110 €/kWh
30,47 €


EEG-Umlage
2.770 kWh
0,0000 €/kWh
0,00 €


Offshore-Netzumlage
2.770 kWh
0,0065 €/kWh
18,01 €


Mess- und Betriebskosten
12 Monate
2,80 €/Monat
33,60 €


Summe netto


1.246,45 €


Umsatzsteuer 19 %


236,82 €


Gesamtbetrag brutto


1.483,27 €



Verrechnung mit Abschlagszahlungen
Copy table


Monat
Betrag



Januar 2024
115,00 €


Februar 2024
115,00 €


März 2024
115,00 €


April 2024
115,00 €


Mai 2024
115,00 €


Juni 2024
115,00 €


Juli 2024
115,00 €


August 2024
115,00 €


September 2024
115,00 €


Oktober 2024
115,00 €


November 2024
115,00 €


Dezember 2024
115,00 €


Summe geleistete Abschläge
1.380,00 €



Ergebnis der Abrechnung
Copy table







Gesamtbetrag brutto
1.483,27 €


Abzüglich geleisteter Abschläge
– 1.380,00 €


Verbleibender Nachzahlungsbetrag
118,92 €



Zahlungsinformationen
Bitte überweisen Sie den Nachzahlungsbetrag von 118,92 € bis zum 15. Februar 2025 unter Angabe der Rechnungsnummer RE-2025-0034512 auf folgendes Konto:
Copy table







Empfänger:
Stadtwerke Musterstadt GmbH


IBAN:
DE12 3456 7890 1234 5678 90


BIC:
MUSTA DE M XXX


Verwendungszweck:
RE-2025-0034512 / 987654321



Neuer Abschlag ab Februar 2025
Basierend auf Ihrem Jahresverbrauch 2024 wird Ihr monatlicher Abschlag ab dem 01. Februar 2025 auf 97,00 Euro festgesetzt.

Diese Rechnung wurde maschinell erstellt und ist ohne Unterschrift gültig.
Stadtwerke Musterstadt GmbH | Energiestraße 42 | 12345 Musterstadt
"""
    #print(Organisation.model_json_schema())

    #parser = OllamaDocumentParser("qwen3.5:4b")
    parser = OllamaDocumentParser("phi4-mini")

    # sender = parser.get_sender(example_content)
    # print("Sender:")
    # print(f"name:    {sender.name}")
    # print(f"address: {sender.address}")

    # receiver = parser.get_receiver(example_content)

    # print("Receiver:")
    # print(f"name:    {receiver.name}")
    # print(f"address: {receiver.address}")

    doc = parser.get_document_info(example_content)
    print(doc)

    

    

