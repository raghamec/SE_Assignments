from dotenv import load_dotenv
import os   
from crewai import LLM, Agent, Task, Crew, Process
from crewai_tools import SerperDevTool



load_dotenv()

Search_Tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"), verbose=True)


# Initialize the LLM with your OpenAI API key
llm = LLM(model="gpt-4o-mini")
print("Brain Created Successfully")

# Create an agent with the LLM
Researcher = Agent(role="Technology Researcher",goal="Finding Top trending technology news stories for Research", backstory="You are a skilled researcher with a keen eye for the latest technology trends.",
                   tools=[Search_Tool],Verbose=True, llm=llm)
print("Researcher Agent Created Successfully")

Writer = Agent(role="Content Writer",goal="Write a concise summary of the news stories found by the researcher", backstory="You are a talented content writer with a knack for summarizing complex information into clear and engaging content.",Verbose=True, llm=llm)
print("Writer Agent Created Successfully")

# Create a task for the Researcher agent to find top trending technology news stories
ResearchTask = Task(description="Find today's top 3 trending technology news stories", expected_output="List of top 3 technology news stories", agent=Researcher)
WriteTask = Task(description="Write a concise summary of the news stories found by the researcher in just 5 brief lines", expected_output="Concise summary of the news stories into 5 lines as first line for summary, next 3 lines for top 3 stories as numeric bullet points, last line for conclusion", agent=Writer)

print("Tasks Created Successfully")

# Create a crew with the Researcher and Writer agents and their respective tasks
NewsCrew = Crew(name="Technology News Crew", agents=[Researcher, Writer], tasks=[ResearchTask, WriteTask],process=Process.sequential,verbose=True)

Result = NewsCrew.kickoff()
print("Crew Execution Completed Successfully")
print("Final Result:", Result)


