from crewai import LLM, Agent, Task, Crew
from dotenv import load_dotenv
import os
load_dotenv()

city = input("Enter the city you want to travel to: ")

# Initialize the LLM with your OpenAI API key
llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
print("Brain Created Successfully")

# Create an agent with the LLM
agent = Agent(role="Travel Planner",goal="Suggest best 3 places to visit in the city with few words about that place and best timings to vist on that day",
              backstory="You are a travel planner toured around 50+ countries and have a lot of experience in suggesting places to visit in different cities around the world. You are very good at providing key details about the places you suggest.",
                llm=llm,verbose=True)

# Create a task for the agent to suggest places to visit in the specified city
task = Task(name="Suggest Places to Visit", description=f"Suggest best 3 places to visit in {city} with few words about place and best timings to visit on that day", 
            expected_output="bullet_points", agent=agent, verbose=True) 

#Create a crew with the agent and task
crew = Crew(name="Travel Planner Crew", agents=[agent], tasks=[task])

# Execute the task using the crew
print(crew.kickoff())