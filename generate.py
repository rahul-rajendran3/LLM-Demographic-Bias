import os
import json
from dotenv import load_dotenv
from google import genai
from prompt import Prompt


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

with open('descriptors/reduced_descriptors.json', 'r') as reduced_descriptors:
    data = json.load(reduced_descriptors)

scenario_data = {}

for characteristic in data.keys():
    scenario_data = {
        "N": str(len(data[characteristic])),
        "DEMOGRAPHIC": characteristic,
        "DESCRIPTORS": ', '.join(data[characteristic])
    }

print(scenario_data)

scenario_prompt = Prompt(prompt_name="generate-scenario", prompt_dir="prompts", data=scenario_data)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=scenario_prompt.get_content()
)

print(response.text)

with open('out/sample_response.jsonl', 'w') as outfile:
    outfile.write(response.text)