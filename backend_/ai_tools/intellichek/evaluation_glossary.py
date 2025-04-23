"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed to guide
users through building permit processes and assist with terminology from the CHEK glossary.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing 
smooth and informed assistance.
The module includes functions to facilitate AI chat interactions with users, specifying 
responses in the user's chosen language, and evaluates user descriptions based on a 
predefined glossary.

Author: Elias Niederwieser
Date: 23.07.2024
"""

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
from operator import itemgetter
import config

path_to_glossary = "./ai_tools/chek_database/glossary.txt"
loader = TextLoader(path_to_glossary)
data = loader.load()

embeddings_model = OpenAIEmbeddings(
    openai_api_key=config.OPENAI_API_KEY,
    model=config.EMBEDDING_MODEL
    )

vectorstore = FAISS.from_documents(
    data, 
    embedding=embeddings_model
    )

retriever = vectorstore.as_retriever()

def get_glossary_task(
    inputs: str, 
    language: str,
    model: ChatOpenAI
    ) -> str:
    """
    Perform a chat with a ChatOpenAI model based on provided inputs and update the conversation log.

    Args:
        inputs (str): The input question or statement for the chat.
        model (ChatOpenAI): The ChatOpenAI model for generating responses.

    Returns:
        tuple: A tuple containing the generated response and the total cost of the API call.
    """
  
    template = """Answer the question based only on the following context:
    {context}

    Please formulate the answer as a list seperated by a colon:
    
    - 1. First element in the list should be a special sign:  
        - $FOUND$ if an action was matched
        - $UNSURE$ ifone action is not matchen perfectly or multiple actions were found or the identification is not unique.
        - $NOTFOUND$ if no corresponding action was found.
    - 2. Second element is A list containing the corresponding found action (JUST THE NAME, NO UID or ELEMENTTYPE):
        - NONE if there was no match.
        - if there are multiple possible matches add all.
    - 3. Third element in the list is you responding to the users question. Keep it very short, formal but friendly. Keep in mind that your an AI assistant.
        - If the an action was matched: give a very short positive feedback and ask the user for confirmation by clicking on the text field.
        - if no match tell the user that there was no match with the CHEK glossary. the user should try with a different formulation or to go on.
        - if other, mention as ai assistant that there are suggested matches and that the user should choose a suitable on for updating the process map.
    ------------------
    EXAMPLE: 
    Exmple for a possible output: [$NOTFOUND$, NONE, AI RESPONSE] or [$FOUND$, NAME OF ACTION, AI RESPONSE] or [$UNSURE$, [NAME OF ACTION, NAME OF ACTION], AI RESPONSE]
    Output should be in json format with keywords: status and list_of_actions and chat_response
    Translate AI RESPONSE in the following language and rewrite them in a formal, short but warmly way: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{question}"),
        ])


    chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
            "language": itemgetter("language"),
        }
        | prompt
        | model
        | SimpleJsonOutputParser()
     
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"question": inputs, "language": language})
        total_cost = float(cb.total_cost)
    print(cb)
   
    return response, total_cost

def transform_user_process_description(
    inputs: str, 
    glossary: str, 
    language: str, 
    model: ChatOpenAI
    ) -> str:
    """
    Perform a chat with a ChatOpenAI model based on provided inputs and update the conversation log.

    Args:
        inputs (str): The input question or statement for the chat.
        model (ChatOpenAI): The ChatOpenAI model for generating responses.

    Returns:
        tuple: A tuple containing the generated response and the total cost of the API call.
    """
    
    template = """
    The user provides a description of a building permit process.

    Input:

    {input}

    Adjust the description using the correct terminology from the glossary provided.

    Glossary:

    {glossary}

    Evaluate any described tasks found in the glossary by assigning the appropriate 
    Level of Maturity. If unsure between two levels, select the lower one.
    Furthemore, give also a detailed description how the task is done.

    Example:

    Input:
    "The applicant begins by requesting information from the municipality regarding the building 
    permit process. Information is typically requested and provided in written form, either electronically
    via email or through in-person consultations."

    Output Format:
    "Glossary Name: Gather City Regulatory Information with Level: 1 with Description: detailed description"

    Exclude reasoning from your output. Use this language: {language}
    """
    prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{input}"),
        ])

    chain = (
        {
            "input": itemgetter("input"),
            "glossary": itemgetter("glossary"),
            "language": itemgetter("language")
        }
        | prompt
        | model
        | StrOutputParser()
    )

    with get_openai_callback() as cb:
        response = chain.invoke({"input": inputs, "glossary": glossary, "language": language})
        total_cost = float(cb.total_cost)
        
    return response, total_cost
