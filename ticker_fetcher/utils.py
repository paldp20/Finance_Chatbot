from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate  # Changed
from langchain_core.example_selectors import LengthBasedExampleSelector  # Changed
from langchain_openai import OpenAI  # Changed
from langchain_community.utilities import SQLDatabase  # Changed
from langchain_community.agent_toolkits import SQLDatabaseToolkit  # Changed
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType

# Database credentials
DB_USER = 'my_user'
DB_PASSWORD = 'my_pass'
DB_NAME = 'tickers_db'
DB_HOST = 'db'
DB_PORT = 3306
# mysql_uri = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
mysql_uri = f"mysql+mysqlconnector://my_user:my_pass@localhost:3306/tickers_db"

# Initialize the SQLDatabase and SQLDatabaseToolkit
db = SQLDatabase.from_uri(mysql_uri)
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

# Create SQL agent
agent_executor = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

# Modified the generate_response function to now use the SQL agent
def query_db(prompt):
    return agent_executor.run(prompt)