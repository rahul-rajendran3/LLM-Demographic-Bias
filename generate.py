import os
import json
from dotenv import load_dotenv
from google import genai
from prompt import Prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def get_demographic_data(factor: str = None) -> dict:
    with open("descriptors/reduced_descriptors.json", "r") as f:
        demographic_data = json.load(f)
        if factor:
            return demographic_data[factor]
        else:
            return demographic_data


def generate_scenarios(num_scenarios: int):
    with open("out/scenarios.jsonl", "w") as outfile:
        for characteristic, descriptors in get_demographic_data().items():

            for i in range(num_scenarios):

                scenario_vars = {
                    "N": str(len(descriptors)),
                    "DEMOGRAPHIC": characteristic,
                    "DESCRIPTORS": ", ".join(descriptors),
                    "SCENARIO_ID": str(i),
                }

                scenario_prompt = Prompt(
                    prompt_name="generate-scenario",
                    prompt_dir="prompts",
                    data=scenario_vars,
                )

                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=scenario_prompt.get_content(),
                )

                text_out = response.text.strip()
                outfile.write(text_out + "\n")


if __name__ == "__main__":
    generate_scenarios(20)
