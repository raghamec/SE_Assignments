from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini",openai_api_key=os.getenv("OPENAI_API_KEY"),temperature=0.9)
prompt = "exactly 5 healthy breakfast ideas as numbered, one line each, no preamble"
response = llm.invoke(prompt)
print(response.content)
