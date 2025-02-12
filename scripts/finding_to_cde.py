import argparse
import json
from pathlib import Path
from openimagingdatamodel.cde_set.finding_model import FindingModel
from openimagingdatamodel.cde_set.set_factory import SetFactory
from openimagingdatamodel.cde_set.common import Specialty, SPECIALTY_NAMES
from openimagingdatamodel.cde_set.data.finding_test_data import test_finding_model


def create_specialty(specialty: str) -> Specialty:
    for abbreviation, name in SPECIALTY_NAMES.items():
        if name == specialty:
            return Specialty(abbreviation=abbreviation, name=name)
    raise ValueError(f"Specialty '{specialty}' not found.")
        

def finding_json_to_cde_set(findingModeljson: str, specialtyName: str) -> str:
    findingModelInstance = FindingModel.model_validate(findingModeljson)
    cdeSet = SetFactory.create_set_from_finding_model(findingModelInstance)
    specialty = create_specialty(specialtyName)
    cdeSet.specialties.append(specialty)
    return cdeSet.model_dump_json(exclude_defaults=True, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Convert a finding model JSON to a CDE set with specified specialty.")
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input JSON file containing the finding model."
    )
    parser.add_argument(
        "specialty",
        type=str,
        help="Name of the specialty to add to the CDE set."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Path to the output JSON file to save the CDE set. Defaults to the same directory as the input file."
    )
    args = parser.parse_args()

    # Determine the output file path
    input_path = Path(args.input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file '{args.input_file}' not found.")

    output_path = (
        Path(args.output_file)
        if args.output_file
        else input_path.with_name(f"{input_path.stem}.cde.json")
    )

    # Load the finding model JSON from the input file
    with open(input_path, "r") as infile:
        finding_model_json = json.load(infile)

    # Process the finding model and convert to CDE set
    try:
        cde_set_json = finding_json_to_cde_set(finding_model_json, args.specialty)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Write the resulting CDE set JSON to the output file
    with open(output_path, "w") as outfile:
        outfile.write(cde_set_json)

    print(f"CDE set saved to '{output_path}'.")


if __name__ == "__main__":
    main()