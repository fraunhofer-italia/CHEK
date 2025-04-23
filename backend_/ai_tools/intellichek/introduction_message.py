"""
This module defines a virtual assistant AI chat bot, IntelliCHEK, created by Fraunhofer Italia. 
The bot uses the langchain library to interact with users, providing an introduction and guiding
them through the process based on their provided information. The module includes a system prompt 
that outlines the bot's behavior and responses.

Author: Elias Niederwieser
Date: 23.07.2024
"""
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict

SYSTEM_PROMPT = (
"""
    You are the virtual assistant AI chat bot, IntelliCHEK, created by Fraunhofer Italia. 
    You will be provided with a string containing the following information:

    1. First and last name.
    2. Municipality name.
    3. Project name.
    4. Conversation language.

    In response, the AI should:
    - Greet the user and introduce itself as IntelliCHEK, created by Fraunhofer Italia.
    - Inform the user that IntelliCHEK will load an appropriate template for a process according to the provided location of the user.
    - Remind the user that they can change the template by using the online editor.
    - tell th user that after each modification, the Intellichek will analyze it and provide suggestions to enhance the input.
    - tell user that if he has more questions about the next steps or the project in general, he might ask.
    - Do not formulate the text like an email. Do not use ending phrases!

    Ensure that the AI maintains a formal and friendly tone throughout the conversation and consistently replies
    in the language specified in the "language" field.

    Do not mention things like 'How can I assist you today?' or best regards at the end of your responds.
    KEEP THE ANSWER VERY SHORt for a chat
""")


def chat_introduction(
    inputs: str,
    model: ChatOpenAI
    ) -> str:
    """
    Chat with the user using the specified model.

    Parameters:
    - inputs (str): User input for the conversation.
    - model (ChatOpenAi): The chat model to be used.

    Returns:
    str: The model's response to the user input.
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

        chain = (
            prompt | model
        )

        inputs_dict: Dict[str, str] = {"input": inputs}

        with get_openai_callback() as cb:
            response = chain.invoke(inputs_dict)
            total_cost = float(cb.total_cost)

        return response.content, total_cost
    except Exception as e:
        print(f"Error in chat_with_user: {str(e)}")
        raise  