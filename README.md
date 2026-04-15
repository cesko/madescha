Madescha
========

*Mach deine scheiß Ablage!*

Helps you organise important documents, letters, certificates, with out vendor login.

## The Core Idea

1. Have a scanned document
2. Open it in Madescha
3. Madescha runs OCR and local AI to help you categorize the document
4. Export file - Madescha helps you stick to a naming convention

## How To

## Technology

- Developed in Python
- Qt6 GUI framework
- Depends of Ollama for local AI support

## TODOs
 - [x] Implement all Madescha Widgets
 - [x] Show all Madescha Widgets in Main Window
 - [x] Add Slots / Signals for Medascha Widgets in Main Window
 - [x] Hold and Process Document in Main
 - [ ] Full processing pipeline in Main
 - [ ] Connect Open Documents -> Display Document in Document Viewer
 - [ ] Run automated Process OCR/AI with status feedback
 - [ ] Apply and edit document info
 - [ ] Implement Save Document Widget and the ability to save documents
 - [ ] Set tags for document
 - [ ] Settings file storage and load
 - [ ] Change settings in App


## Dev Notes

- Install with `pip install -e .`
- Run with `medascha`
