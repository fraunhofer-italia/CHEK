"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed 
to guide users through building permit processes and evaluate technology-related 
information based on a maturity model.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing 
smooth and informed assistance.
The module includes functions to facilitate AI chat interactions with users, specifying 
responses in the user's chosen language, and assesses user-provided tasks, events, and 
gateways according to predefined maturity models.

The primary function, `evaluate_technology`, performs asynchronous evaluations of user
inputs, rating them based on specific maturity steps and providing justifications for each rating.

Author: Elias Niederwieser
Date: 23.07.2024
"""

from operator import itemgetter
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
import config
from langchain.output_parsers.json import SimpleJsonOutputParser

path_to_maturity_tech = "./ai_tools/chek_database/maturity_technology.txt"
with open(path_to_maturity_tech, 'r') as file:
    maturity_tech_content = file.read()

async def evaluate_technology(
    inputs: str, 
    language: str,
    model: ChatOpenAI
    ) -> str:
    """
    Perform a chat with a ChatOpenAI model based on provided inputs and update the conversation log.

    Args:
        action (str): The input action for the chat.
        inputs (str): The input question or statement for the chat.
        language (str): The language for the response.
        model (ChatOpenAI): The ChatOpenAI model for generating responses.

    Returns:
        tuple: A tuple containing the generated response and the total cost of the API call.
    """
  
    template = """
    The user will provide a list of tasks, events, and gateways involved in a building permit process,
    along with DESCRIPTIONS of how each is done:
    {input}

    You will also get a maturity model with maturity category elements and the different possible levels of maturity and how to reach them: 
    {context}
    
    As a professional maturity model checker, evaluate each of thee maturity category elements based on the list of tasks, action etc. 
    
    Be precise and do not invent details and do only evaluate the maturity elements NOT the actions and tasks.

    For each step in the evaluation, provide:
    
        - A detailed justification for the assigned level in the maturity model.
        - If undecided between two levels, choose the lower one.
        - If there is no information, assign a zero and justify it by stating that there is no information.
        
    Output should be in JSON format like this:
    
    Label: Data management environment and network platform, 
    Leve: 0, 
    Jusification: Your justification

    Keep your answer concise. The JSON should have the same amount of elements than the elements 
    in the CONTEXT file.
    Respond in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{input}"),
        ])

    chain = (
        {
            "context": itemgetter("context"),#itemgetter("description") | retriever,
            "input": itemgetter("input"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser() 
    )

    with get_openai_callback() as cb:
        response = await chain.ainvoke({ "input": inputs, "language": language, "context":maturity_tech_content})
        total_cost = float(cb.total_cost)

    return response, total_cost


