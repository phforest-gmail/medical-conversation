from dataclasses import dataclass, field
import json

from wowool.sdk import Pipeline, Domain
from pathlib import Path
from wowool.annotation import Sentence, Entity

this_folder = Path(__file__).parent


@dataclass
class AnswerInfo:
    sentence: Sentence
    entities: list[Entity] = field(default_factory=list)
    is_negative: bool = False


@dataclass
class QuestionInfo:
    sentence: Sentence
    entities: list[Entity] = field(default_factory=list)


@dataclass
class QuestionAnswerInfo:
    speaker: str
    questions: list[QuestionInfo] = field(default_factory=list)
    answers: list[AnswerInfo] = field(default_factory=list)


@dataclass
class ConversationInfo:
    speaker: Entity
    sentences: list[Sentence] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)


@dataclass
class SpeakersInfo:
    speakers: list[str] = field(default_factory=list)

    def set_speaker(self, speaker: str):
        self.speakers.append(speaker)

    @property
    def current_speaker(self):
        return self.speakers[-1] if self.speakers else None

    @property
    def previous_speaker(self):
        return self.speakers[-2] if len(self.speakers) > 1 else None


def get_symptoms(sentence: Sentence):
    return list(filter(lambda e: e.uri in MedicalConversations.SYMPTOM_FILTERS, sentence.entities))


class MedicalConversations:

    FILTERS = {"QuestionHealthIssue", "AbsentHealthIssue", "HealthIssue"}
    ANALYSIS_FILTERS = {
        "QuestionHealthIssue",
        "AbsentHealthIssue",
        "HealthIssue",
        "Treatment",
        "Medication",
        "NegativeAnswer",
        "Question",
    }
    SYMPTOM_FILTERS = {"QuestionHealthIssue", "AbsentHealthIssue", "HealthIssue"}

    def __init__(self, pipeline: str):
        self._pipeline = Pipeline(pipeline)
        self.speakers = Domain(source=Path(this_folder, "conversation.wow").read_text())

    def generate_conversation(self, jdoc: dict):
        conversation = jdoc.get("conversation", [])
        conversation_text = "\n".join([f"{sent['speaker']} {sent['text']}" for sent in conversation])
        return conversation_text

    def __call__(self, input: dict):
        # Process the input string and extract conversations
        # This is a placeholder for the actual implementation
        conversation = self.process_sentence(input)
        return conversation

    def collect_information(self, input: dict, filters: set):
        conversation_text = self.generate_conversation(input)
        doc = self.speakers(self._pipeline(conversation_text))
        results = []

        previous_speaker = None
        speakers = SpeakersInfo()
        for sentence in doc.sentences:

            speaker = sentence.Speaker
            if speaker:
                speakers.set_speaker(speaker.canonical)
            print(f"Processing sentence: {sentence.text} (Speaker: {speakers.current_speaker})")
            entities = [entity for entity in sentence.entities if entity.uri in filters]
            for entity in entities:
                results.append(
                    {
                        "speaker": (speakers.current_speaker if speakers.current_speaker else "Unknown"),
                        "entity": entity.text,
                        "uri": entity.uri,
                    }
                )
        return results

    def process_sentence(self, input: dict):
        return self.collect_information(input, self.FILTERS)

    def analyze_conversation(self, conversation: dict):
        conversation_text = self.generate_conversation(conversation)
        doc = self.speakers(self._pipeline(conversation_text))

        print(f"Processing document: \n{doc}")
        results = []
        question_answer = []
        current_question = None
        current_speaker = None
        dialog = []
        speakers = SpeakersInfo()
        for sentence in doc.sentences:

            print(f"Processing sentence: {sentence}")
            speaker = sentence.Speaker
            speakers.set_speaker(speaker.canonical if speaker else "Unknown")

            print(f"Sentence: {sentence.text} ")
            entities = [entity for entity in sentence.entities if entity.uri in self.ANALYSIS_FILTERS]
            for entity in entities:
                if entity.uri == "Question" and speakers.current_speaker:
                    if current_question is None:
                        current_question = QuestionAnswerInfo(speaker=speakers.current_speaker)
                    current_question.questions.append(QuestionInfo(sentence=sentence, entities=get_symptoms(sentence)))
                    print(f"    !!! Question: {sentence.text} (Speaker: {speakers.current_speaker})")

            if current_question and speaker and speaker.canonical != current_question.speaker:
                answer = AnswerInfo(sentence=sentence, entities=get_symptoms(sentence))
                current_question.answers.append(answer)
                negative_answers = [entity for entity in sentence.entities if entity.uri == "NegativeAnswer"]
                if negative_answers:
                    answer.is_negative = True
                    print(f"    !!! Negative Answer: {sentence.text} (Speaker: {speakers.current_speaker})")
                else:
                    print(f"    !!! Positive Answer: {sentence.text} (Speaker: {speakers.current_speaker})")
                question_answer.append(current_question)
                current_question = None

        postive_answer_symptoms = []
        negative_answers_symptoms = []

        for qa in question_answer:
            print("----------------------------------------")
            print(f"Question by {qa.speaker}:")
            question_symptoms = []
            for q in qa.questions:
                print(f"    Question: {q.sentence.text}")
                if "allergies" in q.sentence.text.lower():
                    print("    !!! This question is about allergies.")
                question_symptoms.extend(q.entities)
                for e in q.entities:
                    print(f"        Entity: {e.text} (URI: {e.uri})")
            for a in qa.answers:
                if a.is_negative:
                    print(f"    Negative Answer: {a.sentence.text}")
                    negative_answers_symptoms.extend(a.entities)
                    negative_answers_symptoms.extend(question_symptoms)
                else:
                    print(f"    Positive Answer: {a.sentence.text}")
                    postive_answer_symptoms.extend(a.entities)
                    postive_answer_symptoms.extend(question_symptoms)

        print("Summary of Symptoms:")
        print("  Positive Symptoms:")
        for symptom in postive_answer_symptoms:
            print(f"    {symptom.text} (URI: {symptom.uri})")
        print("  Negative Symptoms:")
        for symptom in negative_answers_symptoms:
            print(f"    {symptom.text} (URI: {symptom.uri})")
        return results
