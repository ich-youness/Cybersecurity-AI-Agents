from typing import Text
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, CodeInterpreterTool
import subprocess
from crewai.tools import tool
from litellm import completion
import os

os.environ['GEMINI_API_KEY'] = "AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k"

# from custom_tool import NmapTool # my nmap custom tool
 
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# def run_nmap_scan( target: str, options: str ="-sV"):
#   """
#   nmap scanner 
#   """
#   try:
#     result = subprocess.run(["nmap"] + options.split() + [target],
#       capture_output= True,
#       Text= True
#     )
#     return result.stdout
#   except Exception as e:
#     return f"=======Error handeling the nmap command======={str(e)}"
#  
scraper = ScrapeWebsiteTool()
interp_nmap = CodeInterpreterTool()
gemini_llm = {
      "model": "gemini/gemini-1.5-flash",
      "api_key": "AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k",
}

# Learn more about YAML configuration files here:
# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'
code_interpreter = CodeInterpreterTool()
@tool("nmap scanner")
def my_tool(target: str, options: str):
  """
  Nmap scanner tool that executes an Nmap scan on a given target.
  """
  try:
    result = subprocess.run(
      ["nmap"] + options.split() + [target], 
      capture_output=True,
      text=True  
    )
    return result.stdout + " =====> "+ options
  except Exception as e:
    return f"=> Error handling the Nmap command {str(e)}"

  
@CrewBase
class CrewaiProject():
	"""CrewaiProject crew"""
	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	# agents_config = 'config/agents.yaml'
	# tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
      tools = [my_tool],
			config=self.agents_config['researcher'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CrewaiProject crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge
    
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
      chat_llm="gemini/gemini-1.5-flash",
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

