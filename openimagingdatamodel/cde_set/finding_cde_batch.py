import click
import json
from pathlib import Path
from openimagingdatamodel.cde_set.finding_model import FindingModel
from openimagingdatamodel.cde_set.set_factory import SetFactory
from openimagingdatamodel.cde_set.common import Specialty, SPECIALTY_NAMES

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

def process_directory(directory: Path, specialty: str = "Chest"):
    if not directory.exists() or not directory.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a valid directory.")

    for file in directory.iterdir():
        if file.suffix == ".json" and not file.name.endswith(".cde.json"):
            output_file = file.with_name(f"{file.stem}.cde.json")

            if file.stat().st_size == 0:
                raise ValueError(f"Error: '{file.name}' is empty.")

            try:
                with open(file, "r") as infile:
                    finding_model_json = json.load(infile)
                cde_set_json = finding_json_to_cde_set(finding_model_json, specialty)
                with open(output_file, "w") as outfile:
                    outfile.write(cde_set_json)
                click.echo(f"Converted '{file.name}' -> '{output_file.name}'")
            except json.JSONDecodeError:
                raise ValueError(f"Error: '{file.name}' contains invalid JSON.")
            except ValueError as e:
                raise ValueError(f"Error processing '{file.name}': {e}")

@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path))
@click.option("--specialty", default="Chest", help="Name of the specialty to add to each CDE set. Defaults to 'Chest'.")
def main(directory, specialty):
    """Batch convert all JSON finding models in a directory to CDE sets."""
    process_directory(directory, specialty)

if __name__ == "__main__":
    main()
