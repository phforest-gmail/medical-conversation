from wowool.sdk import Pipeline, Domain
from wowool.document import Document
from pathlib import Path

this_folder = Path(__file__).parent


class MedicalConversations:

    FILTERS = {"QuestionHealthIssue", "AbsentHealthIssue", "HealthIssue","NegativeAnswer","BodyPart"}

    def __init__(self, pipeline: str):
        self._pipeline = Pipeline(pipeline)
        self.speakers = Domain(source=Path(this_folder, "conversation.wow").read_text())


    def generate_conversation(self, jdoc: dict):
        conversation = jdoc.get("conversation", [])
        conversation_text = "\n".join([f"{sent['speaker']}: {sent['text']}" for sent in conversation])
        return conversation_text
    
    def __call__(self, input: dict):
        # Process the input string and extract conversations
        # This is a placeholder for the actual implementation
        conversation = self.process_sentence(input)
        return conversation
    
    def process_sentence(self, input: dict):
        conversation_text = self.generate_conversation(input)
        doc = self.speakers(self._pipeline(conversation_text))
        print(f"Processing document: {doc.id}")
        results  = []

        previous_speaker = None
        for sentence in doc.sentences:

            speaker = sentence.Speaker
            if speaker:
                previous_speaker = speaker
            print(f"Processing sentence: {sentence.text} (Speaker: {speaker})")
            entities = [entity for entity in sentence.entities if entity.uri in self.FILTERS]
            for entity in entities:
                print(f" - {entity.uri}:{entity.text}")
                results.append({
                    "speaker": previous_speaker.literal if previous_speaker else "Unknown",
                    "entity": entity.text,
                    "uri": entity.uri
                })
        return results
