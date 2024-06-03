import configparser

from loaders.json import CustomJSONLoader
from qa.basic_qa import AskConversation
from summarizers.short import advancedSummarizer, shortSummarizer

# Import Env Variables
config = configparser.ConfigParser()
config.read("config.cfg")
OPENAI_API_KEY = config["OPENAI"]["OPENAI_API_KEY"]

# Load the document
loader = CustomJSONLoader("demo-segments.json")
docs = loader.load()

# Perform the short summarization
summarizer = shortSummarizer(docs, OPENAI_API_KEY)
print("\n\n-----------------------------------------------------")
print(summarizer.run())
print("-----------------------------------------------------\n\n")

# Perform the advanced summarization
textified_conversation = loader.consolidated_text_retranscription()
docs = loader.text2chunks(textified_conversation)
summarizer = advancedSummarizer(docs, OPENAI_API_KEY)
print("\n\n-----------------------------------------------------")
print(summarizer.run())
print("-----------------------------------------------------\n\n")

# Perform the QA task
ac = AskConversation("demo-segments.json", api_key=OPENAI_API_KEY)
ac.load()
replies = ac.ask(
    [
        """What are the next steps after the meeting? List future actions to be undertaken based on
        the team discussion""",
        """"Was there any clear mention of a budget? If so answer with the following format:
            budget = <budget here with dots between every thousand expressed in euros per month> €/mois
            If there was no budget don't make up an answer, say it clearly.
        """,
        "Who is Lancelot? Most specifically what's his job",
        "What CRM does the prospect already use? If there are specific brand names mentioned list them here with bullet points",
        "What are the main objections raised by the participants of this videocall retranscription",
    ]
)
for reply in replies:
    print("----------------------------")
    print(reply)
