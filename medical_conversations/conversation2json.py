import argparse as parseargs
from wowool.document import Document
from wowool.sdk import Pipeline, Domain
from wowool.document import Document
import json



class ParseConversation:

    
    def __init__(self):
        self._pipeline = Pipeline("english")
        self.speakers = Domain(source="""
rule: { "Speaker" "[A-Z]" ":" } = Speaker; 
rule: { "(D|P)" ":" } = Speaker; 
""")

    def __call__(self, input: str | Document):
        doc = self.speakers(self._pipeline(input))
        conversation  = []

        previous_speaker = None

        for sentence in doc.sentences:
            speaker = sentence.Speaker
            if speaker:
                previous_speaker = speaker
            conversation.append({
                    "start": sentence.begin_offset,
                    "end": sentence.end_offset,
                    "speaker": previous_speaker.literal if previous_speaker else "Unknown",
                    "text": sentence.text[len(previous_speaker.literal)+1:] if previous_speaker else sentence.text,
                })
        return {"conversation": conversation}



def parse_args():
    parser = parseargs.ArgumentParser(description="Medical Conversations")
    parser.add_argument(
        "-f", "--file", type=str, required=True, help="Path to the file to process"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    medical_conversations = ParseConversation()
    for doc in Document.glob(args.file):
        result = medical_conversations(doc.data)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()