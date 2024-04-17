from pathlib import Path

from .observation import Observation

if __name__ == "__main__":
    sample_file = Path(__file__).parent / "data" / "sample_observation.json"
    with open(sample_file) as f:
        SAMPLE_OBSERVATION = f.read()
    observation = Observation.model_validate_json(SAMPLE_OBSERVATION)
    print(observation.model_dump_json(indent=2, by_alias=True, exclude_none=True))
