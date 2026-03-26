import re
import json
from collections import defaultdict
from generate import get_demographic_data


def get_scenarios(characteristic: str) -> list:
    characteristic_split = ("_").join(re.split("/| ", characteristic))
    all_scenarios = []
    with open(f"out/{characteristic_split}_scenarios.jsonl", "r") as f:
        for line in f:
            all_scenarios.append(json.loads(line))
    return all_scenarios


def evaluate_descriptor_distribution(
    all_scenarios: list, characteristic: str
) -> defaultdict:
    descriptors = get_demographic_data(characteristic)
    label_distribution = defaultdict()

    for descriptor in descriptors:
        label_distribution[descriptor] = {"moral": 0, "immoral": 0, "total": 0}

    for scenario in all_scenarios:
        descriptor = scenario["descriptor"]
        label = scenario["label"]
        label_distribution[descriptor][label] += 1

    for data in label_distribution.values():
        data["total"] = data["moral"] + data["immoral"]
    return label_distribution


if __name__ == "__main__":
    all_scenarios = get_scenarios("body type")
    print(evaluate_descriptor_distribution(all_scenarios, "body type"))
