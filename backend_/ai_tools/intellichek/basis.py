"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed
to guide users through building permit processes.
In case of inquiries outside its focus, Intellichek informs users of its specialization,
apologizes, and reaffirms its commitment to assist within the scope of the web tool.
The module includes a function to facilitate basic AI chat interactions with users, 
specifying responses in the user's chosen language.

Author: Elias Niederwieser
Date: 23.07.2024
"""
from operator import itemgetter
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser


SYSTEM_PROMPT = (
"""
You are an AI assistant Chatbot named Intellichek, specializing in guiding users 
through building permit processes. Your expertise lies in this field, ensuring a 
smooth and informed experience for users seeking assistance. In the event of inquiries
unrelated to building permits or maturity models, kindly inform the user of the focus 
of your expertise, offer apologies, and reassure them that you are committed to assisting
within the scope of this web tool.

At the end, please add that if the user needs more guidance or 
help with the CHEK application, they can simply ask.

This is the users text: {question}

Answer in this language: {language}

""")


def basic_ai_chat(
    inputs: str, 
    language: str, 
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
                ("human", "{question}"),
            ])


        chain = (
            {
                "question": itemgetter("question"),
                "language": itemgetter("language"),
            }
            | prompt
            | model
            | StrOutputParser()
        
        )

        with get_openai_callback() as cb:
            response = chain.invoke({"question": inputs, "language": language})
            total_cost = float(cb.total_cost)
        
        return response, total_cost

    except Exception as e:
        print(f"Error in chat_with_user: {str(e)}")
        raise  