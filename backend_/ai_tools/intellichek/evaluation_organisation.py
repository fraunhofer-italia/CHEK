"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed to guide 
users through building permit processes and evaluate organizational information based on a
maturity model.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing 
smooth and informed assistance.
The module includes functions to facilitate AI chat interactions with users, specifying 
responses in the user's chosen language, and assesses user-provided tasks, events, and 
gateways according to predefined maturity models.

The primary function, `evaluate_organisation`, performs asynchronous evaluations of user 
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
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser

path_to_maturity_orga="./ai_tools/chek_database/maturity_organisation.txt"
loader = TextLoader(path_to_maturity_orga)
data = loader.load()

embeddings_model = OpenAIEmbeddings(
    openai_api_key=config.OPENAI_API_KEY,
    model="text-embedding-3-large"
    )

vectorstore = FAISS.from_documents(
    data, 
    embedding=embeddings_model
    )

retriever = vectorstore.as_retriever()

async def evaluate_organisation(
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
    Answer only based on the following context: 
    {context}

    The user will provide a list of tasks, events, and gateways involved in a building permit process,
    along with DESCRIPTIONS of how each is done:
    {description}

    As a professional maturity model checker, evaluate each step in your maturity model that you find
    in the context based on the user's DESCRIPTIONS.
    
    Be precise and do not invent details.

    For each step, provide:
    
        - A detailed justification for the assigned level.
        - Mention any discrepancies.
        - If undecided between two levels, choose the lower one
        - If there is no information, assign a zero and justify it by stating that there is no information.
        
    Output should be in JSON format like this:
    
    Label: Internal Stuff, 
    Leve: 0, 
    Jusification: Your justification

    Keep your answer concise. The JSON should have the same amount of elements than the elements 
    in the context file.
    Respond in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{description}"),
        ])


    chain = (
        {
            "context": itemgetter("description") | retriever,
            "description": itemgetter("description"),
            "language": itemgetter("language")
        }
        | prompt
        | model
        | SimpleJsonOutputParser()
    )

    with get_openai_callback() as cb:
        response = await chain.ainvoke({ "description": inputs, "language": language})
        total_cost = float(cb.total_cost)
    

    return response, total_cost


