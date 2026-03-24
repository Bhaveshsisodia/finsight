from tools.nse_tools import get_stock_info , get_nifty_data
import os
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent


from langchain_groq import ChatGroq
load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-120b",  # fast + free + capable
    api_key=os.getenv("GROQ_API_KEY")
)

tools = [get_stock_info, get_nifty_data]

prompt = ChatPromptTemplate.from_messages([
    ("system", "..."),      # tell the LLM who it is
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 4. Create agent + executor — research what these two lines do
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "How much return is generated of TCS stock in 6month?"})
print(result["output"])