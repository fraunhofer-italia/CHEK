"""
This module defines a specialized AI assistant Chatbot named Intellichek, 
designed to guide users through building permit processes and evaluate actions
based on a maturity model.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing 
smooth and informed assistance. 
In case of inquiries outside its focus, Intellichek informs users of its specialization, 
apologizes, and reaffirms its commitment to assist within the scope of the web tool.

The module includes functions to facilitate AI chat interactions with users, specifying 
responses in the user's chosen language, and evaluates actions according to a maturity model.

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
from langchain_core.output_parsers import StrOutputParser
import config
from langchain.output_parsers.json import SimpleJsonOutputParser
from typing import Union, List
from pydantic import BaseModel

path_to_maturity="./ai_tools/chek_database/maturity.txt"
loader = TextLoader(path_to_maturity)
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

class CustomObject(BaseModel):
    status: str
    actions: Union[str, List[str]]
    
def chat_with_maturity_intro(
    action: str, 
    language: str,
    model: ChatOpenAI) -> str:
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
    You are an AI assisstant that should evaluate a building permit process according to a maturity model.

    The user will provide you with an action: {action}.

    Don't say thank you! Based on this action, which you should mention, ask the user in a formal but warmly 
    way to describe in detail who this is usually proceede in the workflow.
    No introduction and no regards from you at the end!


    IF the action is equal to '$REMAINING$' tell the user thank you for the customisation of the task and that
    in order to have a full picture for the maturity model, ,the remaining actions should be described in the same 
    fashion. 
    
    Answer in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{action}"),
        ])

    chain = (
        {
            "action": itemgetter("action"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"action": action, "language": language})
        total_cost = float(cb.total_cost)
        
    return response, total_cost

def evaluate_level_of_maturity_with_chat(
    action: str,
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
  
    template = """Answer the question based only on the following context:
    {context}



    The user will provide you with an action: {action}.
    Additionally, the user will describe how this action is done: {question}.

    As a professional maturity model checker for building permits in the European Union, your task is to give an ANSWER:

    1. Match the provided action to one of the levels you know from (0-5) and justify your decision.

    2. If the description of the user was enough to make an evaluation and to get a level, say thank you and give a positive feedback that you evaluated the action. Furthermore,  return CODE: $Success$ 
    
    3. If the description of the user was not giving sense or no level could be found, say thank you and give a negative feedback but give a suggestion what would be helfull to. Furthermore, return CODE: $Fail$ and level $-1$
    
    NEVER GIVE REASONING BACK IN THE RESPONSE

    Please always add at the end a STATUS in your answer that correspondes to the matched level of maturity, 
    e.g $0$ for level 0 or $1$ for level 1 etc.
    
    Form of output: [ANSWER, STATUS, CODE]

    Example:
    - ["Perfect, the evaluation is done, you can proceed.", $5$, $Success$]
    - ["I need more information to proceed.", $-1$, $Fail$]

    Output should be in json format with keywords: status and chat_response and code

    Keep your answer very short!
    Answer in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{question}"),
        ])

    chain = (
        {
            "context": itemgetter("question") | retriever,
            "action": itemgetter("action"),
            "question": itemgetter("question"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser()
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"action": action, "question": inputs, "language": language, "history": 'conversation_log'})
        total_cost = float(cb.total_cost)
 
    return response, total_cost

def evaluate_level_of_maturity_with_chat_final(
    action: str, 
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
    template = """Answer the question based only on the following context:
    {context}



    The user will provide you with an action: {action}.
    Additionally, the user will describe how this action is done: {question}.

    As a professional maturity model checker for building permits in the European Union, your task is to give an ANSWER:

    1. Match the provided action to one of the levels you know from (0-5) and justify your decision.

    2. Say thank you and give a positive feedback that you evaluated the action. 
   
    NEVER GIVE REASONING BACK IN THE RESPONSE

    Please always add at the end a STATUS in your answer that correspondes to the matched level of maturity, 
    e.g $0$ for level 0 or $1$ for level 1 etc.
    
    Form of output: [ANSWER, STATUS, $Final_Success$ ]

    Example:
    - ["Perfect, the evaluation is done, you can proceed.", $5$, $Final_Success$ ]


    Output should be in json format with keywords: status and chat_response and code
   
    Keep your answer very short!
    Answer in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{question}"),
        ])


    chain = (
        {
            "context": itemgetter("question") | retriever,
            "action": itemgetter("action"),
            "question": itemgetter("question"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser() #StrOutputParser()
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"action": action, "question": inputs, "language": language})
        total_cost = float(cb.total_cost)

    return response, total_cost

def evaluate_level_of_maturity_pre(
    action: str,
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

    The user will provide you with an action: {action}.
    
    Find this action in the following description: {evaluated_description}

    If the action is mentioned in the description give back the Level, which is a integer from 0 to 5 
    and tell the user, thanky you and give a short friendly positive feedback that the evaluation is 
    done by the previous description and always mention the name of the action the user provided. Give 
    also back the Description. If the action was found the code is: $Success$

    If the action is not mentioned the Level is -1 and the code: $Fail$. So not say anything else.

    Please always add at the end a STATUS in your answer that correspondes to the matched level, 
    e.g $0$ for level 0 or $1$ for level 1 etc.
    
    Form of output: [ANSWER, DESCRIPTION, STATUS, CODE]

    Examples: 
    - ["Good, I already evaluated this action based on your description","description how the task is done", $5$, $Success$]
    - ["BLANK MESSAGE","No Description Given", $-1$, $Fail$]

    Output should be in json format with these keywords in the following order: 
    chat_resonse, description, status and code

    Keep your answer short!
    Answer in this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{evaluated_description}"),
        ])

    chain = (
        {
            "action": itemgetter("action"),
            "evaluated_description": itemgetter("evaluated_description"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser()
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"action": action, "evaluated_description": inputs, "language": language})
        total_cost = float(cb.total_cost)
 
    return response, total_cost