import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from utils import *


# Now the Streamlit app

# Sidebar contents
with st.sidebar:
    st.title('Financial QnA Engine')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - Streamlit
    - Open AI Davinci LLM Model
    - LangChain
    - Finance

    ''')
    add_vertical_space(5)
    st.write('Running in Docker!')

# from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate  # Changed
# from langchain_core.example_selectors import LengthBasedExampleSelector  # Changed
# from langchain_openai import OpenAI  # Changed
# from langchain_community.utilities import SQLDatabase  # Changed
# from langchain_community.agent_toolkits import SQLDatabaseToolkit  # Changed
# from langchain_community.agent_toolkits.sql.base import create_sql_agent
# from langchain.agents.agent_types import AgentType

# # Database credentials
# DB_USER = 'my_user'
# DB_PASSWORD = 'my_pass'
# DB_NAME = 'tickers_db'
# DB_HOST = 'db'
# DB_PORT = 3306
# # mysql_uri = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# mysql_uri = f"mysql+mysqlconnector://my_user:my_pass@localhost:3306/tickers_db"

# # Initialize the SQLDatabase and SQLDatabaseToolkit
# db = SQLDatabase.from_uri(mysql_uri)
# toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

# # Create SQL agent
# agent_executor = create_sql_agent(
#     llm=OpenAI(temperature=0),
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     handle_parsing_errors=True
# )

# # Modified the generate_response function to now use the SQL agent
# def query_db(prompt):
#     return agent_executor.run(prompt)

# Generate empty lists for generated and past.
## generated stores AI generated responses
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hi, how can I help today?"]
## past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = ['Hi!']

# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

# User input
## Function for taking user provided prompt as input
def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text

## Applying the user input box
with input_container:
    user_input = get_text()

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    response = utils.query_db(prompt)
    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style='identicon',seed=123)
            message(st.session_state["generated"][i], key=str(i),avatar_style='icons',seed=123)