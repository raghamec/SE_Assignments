from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
inputs = input("Enter a word to find synonyms: ")
prompt = ChatPromptTemplate.from_template("Give few synonymns for {word}")
model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
chain = prompt | model | StrOutputParser()

print(chain.invoke({"word": inputs}))