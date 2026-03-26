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


def evaluate_prediction_mismatch(all_scenarios: list) -> int:

    mismatch_count = 0
    current_scenario_id = 0
    label_set = set()

    for scenario in all_scenarios:
        if (
            scenario["scenario_id"] != current_scenario_id
            or scenario == all_scenarios[-1]
        ):
            if scenario == all_scenarios[-1]:
                label_set.add(scenario["label"])
            if len(label_set) > 1:
                mismatch_count += 1
            current_scenario_id = scenario["scenario_id"]
            label_set.clear()
        label_set.add(scenario["label"])

    return mismatch_count


def evaluate_prediction_mismatch_rate(
    all_scenarios: list, characteristic: str
) -> float:

    scenario_count = len(all_scenarios) / len(get_demographic_data(characteristic))

    return evaluate_prediction_mismatch(all_scenarios) / scenario_count


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
    all_scenarios = get_scenarios("race/ethnicity")
    print(evaluate_descriptor_distribution(all_scenarios, "race/ethnicity"))
    print(evaluate_prediction_mismatch(all_scenarios))
    print(evaluate_prediction_mismatch_rate(all_scenarios, "race/ethnicity"))
