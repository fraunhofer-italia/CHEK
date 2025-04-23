"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed to 
interpret BPMN (Business Process Model and Notation) files for building permits in the 
European Union.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing
smooth and informed assistance.
The module includes a function to facilitate AI chat interactions with users, specifying
responses in the user's chosen language, and extracts tasks, events, and gateways from 
provided BPMN XML snippets.

The primary function, `extraction_process`, performs asynchronous evaluations of user 
inputs, extracting and describing tasks, events, and gateways based on the given BPMN 
XML snippet and providing justifications for each extraction.

Author: Elias Niederwieser
Date: 23.07.2024
"""

from operator import itemgetter
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

async def extraction_process(
    string: str, 
    language: str, 
    model: ChatOpenAI
    ) -> str:
    """
    Perform a chat with a ChatOpenAI model based on provided inputs and update the conversation log.

    Args:
        action (str): The input action for the chat.
        language (str): The language for the response.
        model (ChatOpenAI): The ChatOpenAI model for generating responses.

    Returns:
        tuple: A tuple containing the generated response and the total cost of the API call.
    """
    
    template = """
    You are a BPMN interpreter for building permits in the European Union.

    The user will provide you with a portion of the XML from a BPMN file describing a building permit process:
    
    {string}

    Based on this, extract all tasks, events, and gateways. 
    For each, provide the corresponding DESCRIPTION that you find in the XML File. 
    
    Format your response as follows: 
   
        - NAME the task 
        - Use the DESCRIPTION to briefly explain how it is done.
        
    Maintain the order in which they appear in the process map.

    Answer in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{string}"),
        ])

    chain = (
        {
            "string": itemgetter("string"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    with get_openai_callback() as cb:
        response = await chain.ainvoke({"string": string, "language": language})
        total_cost = float(cb.total_cost)
   
    return response, total_cost

