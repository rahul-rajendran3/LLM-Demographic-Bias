import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import Prompt
from tqdm import tqdm
from rouge_score import rouge_scorer

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


def filter_scenarios(model: str, rouge_threshold: float = 0.85):
    scorer = rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True)

    for characteristic, descriptors in get_demographic_data().items():
        characteristic_split = ("_").join(re.split("/| ", characteristic))
        input_file = f"out/raw/{model}_{characteristic_split}_scenarios.jsonl"
        output_file = (
            f"out/filtered/{model}_{characteristic_split}_scenarios_filtered.jsonl"
        )

        scenarios_by_id = {}
        with open(input_file, "r") as f:
            for line in f:
                scenario = json.loads(line)
                scenario_id = scenario.get("scenario_id")
                if scenario_id not in scenarios_by_id:
                    scenarios_by_id[scenario_id] = []
                scenarios_by_id[scenario_id].append(scenario)

        with open(output_file, "w") as out:
            for scenario_id, scenarios in scenarios_by_id.items():
                if len(scenarios) > 1:
                    scores = [
                        scorer.score(scenarios[0]["story_text"], s["story_text"])[
                            "rouge1"
                        ].fmeasure
                        for s in scenarios[1:]
                    ]
                    if all(score >= rouge_threshold for score in scores):
                        for scenario in scenarios:
                            out.write(json.dumps(scenario) + "\n")
                else:
                    for scenario in scenarios:
                        out.write(json.dumps(scenario) + "\n")


def generate_scenarios(num_scenarios: int):
    for characteristic, descriptors in get_demographic_data().items():
        characteristic_split = ("_").join(re.split("/| ", characteristic))
        with open(f"out/raw/{characteristic_split}_scenarios.jsonl", "w") as outfile:

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
