# CHEK Backend

![Version](https://img.shields.io/badge/version-0.1.3:alpha-lightblue.svg) ![Docker Compose](https://img.shields.io/badge/docker--compose-available-blue.svg?logo=docker) ![Swagger](https://img.shields.io/badge/swagger-docs-brightgreen.svg?logo=swagger&link=https://[yourdomain.com/swagger](http://10.30.104.71:7780/docs#/)) ![Documentation](https://img.shields.io/badge/docs-available-orange.svg) ![License](https://img.shields.io/badge/license-Custom-yellow.svg)


CHEK Backend is the backend for a web application that utilizes AI functionality through the virtual assistant IntelliCHEK. IntelliCHEK assists in evaluating building permits in the European Union according to a maturity check, and it creates a roadmap to achieve specific benchmarks.

## Features
![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue.svg?logo=postgresql)

-**FastAPI**: For high performance and easy-to-use features for building APIs.
-**PostgreSQL**: As the database system, ensuring reliable data storage and retrieval.
-**Docker**: Containerization to streamline deployment and scaling.
-**Swagger UI**: For easy access and testing of all API endpoints.

The application is built with the following major dependencies:


![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI Version](https://img.shields.io/badge/fastapi-0.104.1-green.svg)
![Langchain Version](https://img.shields.io/badge/langchain-0.1.4-cyan.svg)
![OpenAI Version](https://img.shields.io/badge/openai-1.3.6-blueviolet.svg)
![Python-dotenv Version](https://img.shields.io/badge/python--dotenv-1.0.0-lightgrey.svg)
![Tiktoken Version](https://img.shields.io/badge/tiktoken-0.5.2-brightgreen.svg)
![SQLAlchemy Version](https://img.shields.io/badge/sqlalchemy-2.0.25-red.svg)
![Psycopg2-binary Version](https://img.shields.io/badge/psycopg2--binary-2.9.9-darkred.svg)
![Passlib Version](https://img.shields.io/badge/passlib-1.7.4-yellowgreen.svg)
![Python-jose Version](https://img.shields.io/badge/python--jose-3.3.0-darkorange.svg)
![Langchain-openai Version](https://img.shields.io/badge/langchain--openai-0.1.1-teal.svg)
![Asyncpg Version](https://img.shields.io/badge/asyncpg-0.29.0-blue.svg)
![Langchain-community Version](https://img.shields.io/badge/langchain--community-0.0.38-magenta.svg)
![Psycopg-binary Version](https://img.shields.io/badge/psycopg--binary-3.1.19-brown.svg)
[![reCAPTCHA v3](https://img.shields.io/badge/reCAPTCHA-v3-brightgreen)](https://www.google.com/recaptcha)

## Prerequisites
Before you begin, ensure you have the following installed:

- Docker
- Docker Compose

## Installation
### Set Up Environment
Ensure Docker and Docker Compose are installed on your system. 

### Configuration Instructions

Before running the application, make sure to properly configure the following fields in your `.env` file. These fields include sensitive information such as passwords and API keys. Update the placeholders with your actual values.

#### Security and Secret Management
-`OPENAI_API_KEY`: Your OpenAI API key.

#### Database Setup
-`POSTGRES_DB`: Name of your primary PostgreSQL database.
-`POSTGRES_USER`: Username for your primary PostgreSQL database.
-`POSTGRES_PASSWORD`: Password for your primary PostgreSQL database.
-`POSTGRES_HOST`: Host for your primary PostgreSQL database.
-`POSTGRES_PORT`: Port number for your primary PostgreSQL database.

### Authentication
-`SECRET_KEY`: Secret key for authentication.
-`ALGORITHM`: Algorithm used for token generation.
-`ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes.

#### PgAdmin
-`PGADMIN_DEFAULT_EMAIL`: Default email for PgAdmin login.
-`PGADMIN_DEFAULT_PASSWORD`: Default password for PgAdmin login.

#### Google reCAPTCHA
-`RECAPTCHA_SECRET_KEY`: Your Google reCAPTCHA secret key.

Ensure all these fields are correctly set to match your environment and security requirements.


### Build and Deploy with Docker
Use Docker Compose to build and deploy the services. This will set up the application and the database, ready for use:

1.**Clone the repository:**
```bash
   git clone https://fhi-git.fraunhofer.it/chek/check-ai-microservice
   cd backend
```

2.**Build Docker images:**

```bash
   docker-compose build
```

5.**Run the containers:**

```bash
   docker-compose up
```
### First-Time Database Initialization

If the database is initialized for the first time, migrations will be applied automatically, and a user with an admin role will be created. The credentials for this admin user are defined in the `.env` file.

## Software Architecture

### Service Structure

```
├── db                        - PostgreSQL database service for storing data.
│                               Accessible on port 5420.
├── api                       - Main API service for the Climagruen application.
│                               Accessible on port 9980.
└── pgadmin                   - PGAdmin service for managing PostgreSQL databases.
                                Accessible on port 5555.
```

### Project Structure

```
├── ai_tools         - AI models and utilities for advanced rag processing.
├── api              - Core application code, including models, services, and APIs.
│ ├── authentication - Configuration files and global settings.
│ ├── models         - Data models for SQLAlchemy ORM.
│ ├── routers        - API routers for organizing endpoints into logical groups.
│ ├── schemas        - Pydantic schemas for request and response validation.
│ └── utils          - Global helper functions.
├── uploads          - Static assets, including project generated files.
├── data             - Persistent data storage for databases and other data sets.
│ └── db             - Postgres Database for main backend.
└── main             - main.py
```

## Usage

After successfully running the containers:

- Access the **FastAPI MAIN Backend application** and its Swagger UI at `http://localhost9980/docs`.
-**PGAdmin** can be accessed at `http://localhost:5555`. Use the credentials specified in your `.env` file to log in and manage the PostgreSQL database.

# Functionality
## Introduction to AI Functions

In the following, all the AI functions are listed with their functionalities:

### The AI function defined by `chat_introduction` performs the following tasks:

1. **Introduction**: The AI greets the user, introduces itself as IntelliCHEK, created by Fraunhofer Italia, and acknowledges the user by their provided first and last name.
2. **Template Loading**: It informs the user that it will load an appropriate template for the process based on the user's municipality.
3. **Template Modification Reminder**: The AI reminds the user that they can change the template using the online editor.
4. **Modification Analysis**: It tells the user that after each modification, IntelliCHEK will analyze the changes and provide suggestions to enhance the input.
5. **Further Assistance Offer**: The AI informs the user that they can ask more questions about the next steps or the project in general.
6. **Formal and Friendly Tone**: The AI ensures the response is formal and friendly, and it replies in the language specified by the user.
7. **Chat Format**: The AI maintains a short and direct format suitable for chat, avoiding email-like phrases and ending phrases such as "How can I assist you today?" or "Best regards."

### The AI function defined by `basic_ai_chat`  performs the following tasks:

1. **Specialization Acknowledgment**: The AI introduces itself as Intellichek, a chatbot specializing in guiding users through building permit processes.
2. **Expertise Focus**: It ensures the user understands that its expertise is specifically in building permits and maturity models.
3. **Scope Limitation**: If the user's inquiry is unrelated to building permits or maturity models, the AI politely informs the user of its specialized focus, offers apologies, and reassures them of its commitment to assist within the scope of this web tool.
4. **Guidance Offer**: At the end of the response, the AI adds a note that the user can ask for more guidance or help with the CHEK application if needed.
5. **Language Specification**: The AI delivers its response in the language specified by the user.
6. **User's Text Utilization**: The AI takes the user's text and processes it within the context of building permit guidance, ensuring the response is relevant and helpful.
7. **Formal and Friendly Tone**: The AI maintains a formal and friendly tone throughout the conversation, ensuring clarity and professionalism.

### The AI function `transform_user_process_description` performs the following tasks:

1. **Input Processing**: It takes a user's description of a building permit process, a glossary of correct terminology, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to understand how to process the user's input. This template guides the AI to adjust the description using the correct terminology from the glossary and to evaluate tasks described in the input.
3. **Terminology Adjustment**: The AI refines the user's description by replacing general terms with specific terms from the ***glossary***, ensuring the description uses the correct terminology.
4. **Maturity Level Assignment**: The AI evaluates tasks mentioned in the description and assigns them an appropriate Level of Maturity based on the glossary. If there is ambiguity between two levels, it selects the higher one.
5. **Description Assignment:** The AI reformulates the description of the user.
6. ****Language Translation**: The AI provides the refined description in the specified language.**
7. ****Output Generation**: Finally, the AI produces a refined description of the building permit process, adjusted for correct terminology and maturity levels, and in the desired language.**

### The AI function `get_glossary_task` performs the following tasks:

1. **Input Processing**: It takes a user's question or statement and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to understand how to process the user's input. This template guides the AI to search for relevant actions from a given context and format the answer as a list.
3. **Context Matching**: The AI matches the user's input against a given context to identify corresponding actions. It determines whether an action is found, not found, or if the match is uncertain due to multiple possibilities.
4. **List Formatting**: The AI formats its findings into a list:

   - The first element indicates the match status: action found, not found, or unsure.
   - The second element lists the corresponding action names, or indicates "NONE" if no match is found.
   - The third element provides a concise, formal, and friendly response to the user's question, tailored based on the match status.
5. **Language Translation**: The AI translates its response into the specified language, ensuring it is formal, concise, and warm.
6. **Output Generation**: The AI produces a JSON-formatted response containing:

   - The match status.
   - The list of found actions.
   - The translated response to the user's question.

### The AI function `chat_with_maturity_intro `guides the user through evaluating a building permit process according to a maturity model.

- **User Input**: The user provides an action and a preferred language.
- **Template Utilization**: The AI uses a template to formulate a response based on the provided action.
- **Guidance**: The AI asks the user to describe how the action is typically proceeded in the workflow.
- **Special Handling**: If the action is "$REMAINING$", the AI thanks the user and informs them that the remaining actions should also be described for a full evaluation.
- **Language Specification**: The response is provided in the specified language.
- **Output**: The AI generates a formal yet friendly response, maintaining brevity and relevance to the user's input.

### The AI function `evaluate_level_of_maturity_with_chat` evaluates the maturity level of an action within a building permit process.

- **User Input**: The user provides an action, a detailed description of how the action is done, and a preferred language.
- **Template Utilization**: The AI uses a template to match the action to a maturity level (0-5).
- **Evaluation**: The AI provides an evaluation based on the description, giving positive feedback if the description is sufficient, or suggesting improvements if it is not.
- **Output Formatting**: The response includes the evaluation result, status, and a code indicating success or failure.
- **Language Specification**: The response is provided in the specified language.

### The AI function `evaluate_level_of_maturity_with_chat_final`  performs a final evaluation of the maturity level of an action.

- **User Input**: The user provides an action, a detailed description of how the action is done, and a preferred language.
- **Template Utilization**: The AI uses a template to match the action to a maturity level (0-5).
- **Evaluation**: The AI evaluates the action, providing positive feedback and the maturity level without giving any reasoning in the response.
- **Output Formatting**: The response includes the evaluation result, status, and a code indicating final success.
- **Language Specification**: The response is provided in the specified language.

### The Ai function `evaluate_level_of_maturity_pre` checks if an action has already been evaluated based on a provided description.

- **User Input**: The user provides an action, an evaluated description, and a preferred language.
- **Template Utilization**: The AI uses a template to find the action in the description.
- **Evaluation**: If the action is found, the AI provides the corresponding maturity level and positive feedback. If not, it indicates failure with a blank message.
- **Output Formatting**: The response includes the evaluation result, status, and a code indicating success or failure.
- **Language Specification**: The response is provided in the specified language.

### The AI function `evaluate_information` performs the following tasks:

1. **Input Processing**: It takes a user's list of tasks, events, and gateways related to a building permit process, along with the description of how these are done, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to understand how to process the user's input. This template guides the AI to evaluate each task based on Key Maturity Areas (KMAs) from a maturity model context.
3. **Maturity Rating**: The AI rates each task according to the input provided by the user, ensuring precise evaluation without inventing any information.
4. **Justification**: For each rating, the AI provides a detailed justification, mentioning any differences observed and explaining the reasoning behind the assigned level.
5. **Output Formatting**: The response is formatted in JSON, including labels, levels, and justifications for each KMA.
6. **Language Translation**: The AI translates its response into the specified language, ensuring clarity and conciseness.
7. **Output Generation**: The AI generates a short, precise, and well-justified evaluation of the tasks, presented in the desired language.

### The AI function `evaluate_organisation` performs the following tasks:

1. **Input Processing**: It takes a user's list of tasks, events, and gateways related to a building permit process, along with descriptions of how these are done, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to process the user's input. This template guides the AI to evaluate each step based on the maturity model context.
3. **Maturity Rating**: The AI rates each step in the maturity model according to the user's input, ensuring precise evaluation without inventing any information.
4. **Justification**: For each rating, the AI provides a detailed justification, explaining why a particular level was assigned and mentioning any observed differences.
5. **Output Formatting**: The response is formatted in JSON, including labels, levels, and justifications for each step.
6. **Language Translation**: The AI translates its response into the specified language, ensuring clarity and conciseness.
7. **Output Generation**: The AI generates a short, precise, and well-justified evaluation of the tasks, incorporating conversation history and presented in the desired language.

### The AI function `evaluate_technology` performs the following tasks:

1. **Input Processing**: It takes a user's list of tasks, events, and gateways related to a building permit process, along with descriptions of how these are done, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to process the user's input. This template guides the AI to evaluate each step based on the maturity model context.
3. **Maturity Rating**: The AI rates each step in the maturity model according to the user's input, ensuring precise evaluation without inventing any information.
4. **Justification**: For each rating, the AI provides a detailed justification, explaining why a particular level was assigned and mentioning any observed differences.
5. **Output Formatting**: The response is formatted in JSON, including labels, levels, and justifications for each step, such as "Label: Verification of procedural data, Level: 0, Justification: Your justification."
6. **Language Translation**: The AI translates its response into the specified language, ensuring clarity and conciseness.
7. **Output Generation**: The AI generates a short, precise, and well-justified evaluation of the tasks, presented in the desired language.

### The AI function `evaluate_process` performs the following tasks:

1. **Input Processing**: It takes a user's list of tasks, events, and gateways related to a building permit process, along with descriptions of how these are done, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to process the user's input. This template guides the AI to evaluate each step based on the maturity model context.
3. **Maturity Rating**: The AI rates each step in the maturity model according to the user's input, ensuring precise evaluation without inventing any information.
4. **Justification**: For each rating, the AI provides a detailed justification, explaining why a particular level was assigned and mentioning any observed differences.
5. **Output Formatting**: The response is formatted in JSON, including labels, levels, and justifications for each step, such as "Label: Understanding of the process and mapping of steps, Level: 0, Justification: Your justification."
6. **Language Translation**: The AI translates its response into the specified language, ensuring clarity and conciseness.
7. **Output Generation**: The AI generates a short, precise, and well-justified evaluation of the tasks, presented in the desired language.

### The AI function `extraction_process` performs the following tasks:

1. **Input Processing**: It takes a user's provided part of the XML of a BPMN file describing a building permit process, and the desired language for the response.
2. **Template Utilization**: The AI uses a predefined template to process the user's input. This template guides the AI to extract relevant information from the XML.
3. **Task, Event, and Gateway Extraction**: The AI extracts all tasks, events, and gateways from the provided XML.
4. **Description Assignment**: For each extracted task, event, and gateway, the AI uses the corresponding description to explain how it is done, ensuring the description is concise.
5. **Order Preservation**: The AI maintains the order of tasks, events, and gateways as they appear in the process map.
6. **Language Translation**: The AI provides the extracted information and descriptions in the specified language, ensuring clarity and brevity.
7. **Output Generation**: The AI generates a structured list of tasks, events, and gateways with their descriptions, presented in the desired language.

<!-- ### Zoomable Image

Click the image to view it in full size with zoom capabilities:

[![Large Image](images/erd.png)](images/erd.png) -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## Authors

-**Elias Niederwieser** - *Lead developer and Initial work* - [Elias Niederwieser](mailto:elias.niederwieser@fraunhofer.it)

## Acknowledgments

Thanks to all the contributors who invest their time and effort to make this project better. Your contributions are highly appreciated.




