import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import Prompt
from tqdm import tqdm

load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

client = genai.Client(
    vertexai=GOOGLE_GENAI_USE_VERTEXAI,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
)


def get_demographic_data(factor: str = None) -> dict:
    with open("descriptors/reduced_descriptors.json", "r") as f:
        demographic_data = json.load(f)
        if factor:
            return demographic_data[factor]
        else:
            return demographic_data


def generate_scenarios(num_scenarios: int):
    for characteristic, descriptors in get_demographic_data().items():
        characteristic_split = ("_").join(re.split("/| ", characteristic))
        with open(f"out/{characteristic_split}_scenarios.jsonl", "w") as outfile:

            for i in tqdm(range(num_scenarios)):
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

                time.sleep(0.5)


if __name__ == "__main__":
    generate_scenarios(500)
