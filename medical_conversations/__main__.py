import argparse as parseargs
from medical_conversations.medical_conversations import MedicalConversations
from wowool.document import Document
import json
from pathlib import Path


def parse_args():
    parser = parseargs.ArgumentParser(description="Medical Conversations")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to the file to the json input",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Processing file: {args.file}")
    medical_conversations = MedicalConversations("english,healthcare,question")
    print(f"Processing document: {args.file}")
    jdoc = json.loads(Path(args.file).read_text())
    result = medical_conversations.analyze_conversation(jdoc)
    # print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
