import ollama

from madescha.madescha_types import PersonOrOrganisation, Date, Document

class OllamaDocumentParser:

    def __init__(self, model:str):
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

    example_content = ""
    
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

    

    

