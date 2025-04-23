"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed to generate roadmaps
for building permit processes based on key maturity areas (KMAs) and predefined benchmarks.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing smooth and 
informed assistance.
The module includes a function to facilitate AI chat interactions with users, specifying responses in 
the user's chosen language, and generates detailed roadmaps based on provided inputs.

The primary function, `get_roadmap_from_ai`, performs asynchronous evaluations of user inputs, creating 
a roadmap in JSON format that includes KMAs, dependencies, actions, and tools, with careful 
consideration of start dates and dependencies.

Author: Elias Niederwieser
Date: 23.07.2024
"""
from operator import itemgetter
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser

async def get_roadmap_from_ai(
    inputs: str, 
    language: str,
    model: ChatOpenAI) -> str:
    """
    Perform a chat with a ChatOpenAI model based on provided inputs and update the conversation log.

    Args:
        inputs (str): The input question or statement for the chat.
        model (ChatOpenAI): The ChatOpenAI model for generating responses.

    Returns:
        tuple: A tuple containing the generated response and the total cost of the API call.
    """

    template = """
    You will receive a JSON file representing a roadmap for reaching a given maturity level 
    in the process of building permits. 
    The JSON file includes various KMAs (Key Maturity Areas) with their respective 
    level differences, which denote the number of levels difference between the current 
    (as-is) and target (to-be) states. this is the JSON file: 
    {text}

    Please create a new roadmap by transforming the given JSON file with the following changes:

    Replace the level_difference label with start_date and end_date.
    Calculate the start_date and end_date based on the level_difference:
    
    1 level difference = 3 months, 2 level difference = 6 months etc. 
    
    Ensure that the start_date for a KMA can only begin after the end_date of any other KMA 
    in which the Dependencies are Actions. 

    Dependencies are a list that also can be a list of Actions in different KMA's. Keep that in mind.

    The roadmap should be a json in this format 
    If the level difference is 0 or negative the start_date and end_date should be the same and 
    the labels dependencies, actions ad chek_tools should be emppty.
    FORMAT:
        "kma": "string",
        "start_date": "string",
        "end_date": "string",
        "dependencies": ["string", "string"],
        "actions": ["string", "string"],
        "chek_tools": ["string", "string"]

    The first KMA should start with the  2025-01-01
    Translate in the following language: {language}
    """
    prompt = ChatPromptTemplate.from_template(template)

    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{text}"),
        ])


    chain = (
        {
            "text": itemgetter("text"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser()
    )
   
    with get_openai_callback() as cb:
        response = await chain.ainvoke({"text": inputs, "language": language})
        print(response, type(response))
        total_cost = float(cb.total_cost)

    return response, total_cost
