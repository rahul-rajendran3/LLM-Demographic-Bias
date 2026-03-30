import re
import glob
import os
import json
from collections import defaultdict
from generate import get_demographic_data


def _normalize_characteristic(characteristic: str) -> str:
    return ("_").join(re.split("/| ", characteristic))


def _characteristic_from_filtered_file(file_path: str) -> str:
    normalized = os.path.basename(file_path).replace("_scenarios_filtered.jsonl", "")
    for characteristic in get_demographic_data().keys():
        if _normalize_characteristic(characteristic) == normalized:
            return characteristic
    return normalized


def get_filtered_output_files() -> list:
    return sorted(glob.glob("out/filtered/*_scenarios_filtered.jsonl"))


def get_scenarios(characteristic: str) -> list:
    characteristic_split = _normalize_characteristic(characteristic)
    all_scenarios = []
    with open(
        f"out/filtered/{characteristic_split}_scenarios_filtered.jsonl", "r"
    ) as f:
        for line in f:
            all_scenarios.append(json.loads(line))
    return all_scenarios


def get_all_scenarios() -> dict:
    scenarios_by_characteristic = {}
    for file_path in get_filtered_output_files():
        characteristic = _characteristic_from_filtered_file(file_path)
        scenarios = []
        with open(file_path, "r") as f:
            for line in f:
                scenarios.append(json.loads(line))
        scenarios_by_characteristic[characteristic] = scenarios
    return scenarios_by_characteristic


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


def evaluate_prediction_mismatch_rate(all_scenarios: list) -> float:

    scenario_count = len({scenario["scenario_id"] for scenario in all_scenarios})

    if scenario_count == 0:
        return 0.0

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
    for characteristic, all_scenarios in get_all_scenarios().items():
        print(f"\nCharacteristic: {characteristic}")
        print(evaluate_descriptor_distribution(all_scenarios, characteristic))
        print(evaluate_prediction_mismatch(all_scenarios))
        print(evaluate_prediction_mismatch_rate(all_scenarios))
