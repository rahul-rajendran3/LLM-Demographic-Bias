import json
from collections import defaultdict
from generate import get_demographic_data

all_scenarios = []

with open("out/scenarios.jsonl", "r") as f:
    for line in f:
        all_scenarios.append(json.loads(line))


def evaluate_descriptor_distribution(factor: str):
    descriptors = get_demographic_data(factor)
    label_distribution = defaultdict()

    for descriptor in descriptors:
        label_distribution[descriptor] = {"moral": 0, "immoral": 0, "total": 0}

    for scenario in all_scenarios:
        descriptor = scenario["descriptor"]
        label = scenario["label"]
        label_distribution[descriptor][label] += 1

    for data in label_distribution.values():
        data["total"] = data["moral"] + data["immoral"]
    print(label_distribution)


if __name__ == "__main__":
    evaluate_descriptor_distribution("race/ethnicity")
