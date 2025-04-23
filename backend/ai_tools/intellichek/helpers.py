"""
This module defines a specialized AI assistant Chatbot named Intellichek, designed 
to interpret BPMN (Business Process Model and Notation) files for building permits 
in the European Union.
Utilizing the langchain library, Intellichek offers expertise in this domain, providing
smooth and informed assistance.
The module includes functions to facilitate AI chat interactions with users, specifying 
responses in the user's chosen language, and extracts tasks, events, and gateways from 
provided BPMN XML snippets.

Additionally, the module provides utility functions for sanitizing BPMN strings, writing 
responses to files, and reading text from files.

- `extraction_process`: Performs asynchronous evaluations of user inputs, extracting and 
   describing tasks, events, and gateways based on the given BPMN XML snippet and providing 
   justifications for each extraction.
    
- `sanitize_bpmn`: Sanitizes the BPMN input string by removing all content starting from 
    the tag containing 'bpmndi:' until the last closing tag '</bpmndi:BPMNDiagram>'.
    
- `write_response_to_file`: Writes a given response string to a .txt file.

- `read_text_from_file`: Reads text from a file and returns it as a string.

- `NoBpmndiTagsFoundError`: Exception raised when no bpmndi tags are found in the input string.

Author: Elias Niederwieser
Date: 23.07.2024
"""

import re

class NoBpmndiTagsFoundError(Exception):
    """Exception raised when no bpmndi tags are found in the input string."""
    pass

def sanitize_bpmn(input_str: str) -> str:
    """
    Sanitize the BPMN input string by removing all content starting from the tag containing 'bpmndi:' 
    until the last closing tag '</bpmndi:BPMNDiagram>'.
    
    Parameters:
        input_str (str): The input BPMN string.
    
    Returns:
        str: The sanitized BPMN string.
    
    Raises:
        NoBpmndiTagsFoundError: If no bpmndi tags are found in the input string.
    """
    start_tag = '<bpmndi:'
    end_tag = '</bpmndi:BPMNDiagram>'
    
    pattern = re.compile(f"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
    
    sanitized_str = re.sub(pattern, '', input_str)

    if sanitized_str == input_str:
        raise NoBpmndiTagsFoundError("No bpmndi tags found in the input string.")
    
    return sanitized_str

def write_response_to_file(response: str, filename: str):
    """
    Write the given response string to a .txt file.

    Args:
        response (str): The response string to write to the file.
        filename (str): The name of the file to which the response will be written.
    """
    with open(filename, 'w') as file:
        file.write(response)
    print(f"Response written to {filename}")

def read_text_from_file(file_path: str) -> str:
    """
    Read text from a file and return it as a string.

    Args:
        file_path (str): Path to the text file.

    Returns:
        str: Content of the text file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return content