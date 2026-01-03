import yaml
import os
import gradio as gr
from smolagents import CodeAgent

# Tool imports
from llm.model import LocalGGUFModel, llm
from tools.gardening_manual import GardeningKnowledgeTool as GardeningManual
from tools.gardening_memory_tool import GardenMemoryTool as GardenMemory
from tools.seasonal_context import SeasonalContextTool as SeasonalContext
from tools.web_search import DuckDuckGoSearchTool as WebSearch
from tools.visit_webpage import VisitWebpageTool as VisitWebpage
from tools.final_answer import FinalAnswerTool as FinalAnswer



CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Tools
gardening_manual = GardeningManual()
seasonal_context = SeasonalContext()
web_search = WebSearch()
visit_webpage = VisitWebpage()
garden_memory = GardenMemory()
final_answer = FinalAnswer()

model = LocalGGUFModel(llm)

with open(os.path.join(CURRENT_DIR, "data/prompts.yaml"), 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# Consolidated Persona
custom_persona = """
"""

# Ensure the persona is at the very top
# prompt_templates['system_prompt'] = custom_persona + "\n" + prompt_templates['system_prompt']

agent = CodeAgent(
    model=model,
    tools=[gardening_manual, seasonal_context, web_search, visit_webpage, garden_memory, final_answer],
    max_steps=5,
    verbosity_level=1,
    planning_interval=None,
    prompt_templates=prompt_templates,
    additional_authorized_imports=["datetime", "json", "difflib"],
    code_block_tags=("```python", "```")
)

def agent_chat(message, history):
    try:        
        response = agent.run(message, reset=False)
        return str(response)
    except Exception as e:
        return f"🌱 I ran into a bit of a sprout-error: {str(e)}"

demo = gr.ChatInterface(
    fn=agent_chat,
    title="🌱 GreenThumb Plant Agent",
    description="I remember your garden and provide expert botanical advice.",
    examples=["Is Aloe Vera toxic to cats?", "What's wrong with my sansevieria?", "How often should I water my ficus elastica?", "List my current plants."],
)

if __name__ == "__main__":
    demo.launch()