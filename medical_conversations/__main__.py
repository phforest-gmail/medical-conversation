import argparse as parseargs
from medical_conversations.medical_conversations import MedicalConversations


def parse_args():
    parser = parseargs.ArgumentParser(description="Medical Conversations")
    parser.add_argument(
        "-f","--file", type=str, required=True, help="Path to the file to process"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Processing file: {args.file}")
    medical_conversations = MedicalConversations()
    result = medical_conversations(
        "Hello, I have been feeling unwell for the past few days."
    )
    print(result)


if __name__ == "__main__":
    main()