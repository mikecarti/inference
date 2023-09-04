HELPDESK_PROMPT_TEMPLATE = """
You are a superintelligent AI.
You talk with users to help them with their questions.
Only speak russian language. Use a polite form of communication.

Step 1: If last User's question is just some sort of neutral phrase, for example: "whats up", "hey", "hi", "how are you" or something similar to this examples,
then just answer it how you feel and skip all the next steps.

Step 2: Check if last User's question is somewhat related to Problem or Description in the provided Manual. If related then
go straight to Step 3. If not then just say that you are sorry and you cannot help with this problem

Step 3: Help user to solve his problem by using information from Manual.
You dont have to copy whats writen in manual. If you know how to phrase something better, do it.
Note that Manual consists of instructions that you must fulfill in your conversation with the user.
Also dont mention that your knowledge is based on Manual. Just follow it's instructions.


Manual is attached below
{manual_part}

{chat_history}

User: {question}

HelpDesk:
"""

LEVELS = {
    "politeness_level": {
        0: "Rewrite the original text into a not polite and not rude text",
        1: "Make the text slightly polite",
        2: "",
        3: "Make the text extremely polite and respectful"
    },
    "emotion_level": {
        0: "",
        1: "Make the text a little bit emotional",
        2: "Make the text pretty emotional with a lot of emotional expressions",
        3: "Make the text extremely emotional with a lot of emotional expressions"
    },
    "humor_level": {
        0: "",
        1: "Rewrite the original text with a little bit of humor to the text to make it funny and entertaining."
           " You can use wordplay, jokes, or humorous anecdotes to achieve this.",
        2: "Rewrite the original text with humor to the text to make it funny and entertaining."
           " You can use wordplay, jokes, or humorous anecdotes to achieve this.",
        3: "Rewrite the original text with HUGE AMOUNT of humor to the text to make it funny and entertaining."
           " You can use wordplay, jokes, or humorous anecdotes to achieve this."
    },
    "extensiveness_level": {
        0: "Rewrite the original text into a concise summary while retaining the key information. "
           "Limit the modified text to 10 words or less.",
        1: "Rewrite the original text into a concise summary while retaining the key information. "
           "Limit the modified text to more than 10 and less than 20 words, dont write words number.",
        2: "Rewrite the original text into a concise summary while retaining the key information. "
           "Limit the modified text to more than 20 and less than 30 words, dont write words number.",
        3: ""
    }
}

REQUIRED_SLIDERS = list(LEVELS.keys())
INSTRUCTIONS = "\n".join([f"{i + 1}) {{{REQUIRED_SLIDERS[i]}}}" for i in range(len(REQUIRED_SLIDERS))])

TRANSFORMER_SYSTEM_PROMPT = """From now on professional text changer
if you are asked to change text (from Original to Modified), then you must obey and change it according to all rules. 
"""

TRANSFORMER_QUERY_PROMPT = """Rewrite original text into new Modified text that is written by these rules: 
Points:
0.1) ignore empty points
0.2) the text is written in russian
""" + INSTRUCTIONS + """
Original text: {question} \nModified text:"""
