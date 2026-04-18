from pathlib import Path

class MadeschaConfig():
    automatically_parse_opened_documents = True
    export_root_directory:str = str(Path.home())
