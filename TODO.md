# TODO for OpenImagingDataModel.py

## Testing

- Get tests going similar using `pytest` similar to those used for `OpenImagingDataModel.ts`
- Make sure to cover the functionality in `notebooks/observation_factory_demo.ipynb` and `notebooks/set_factory_demo.ipynb` especially because we will be using these a lot
- `FindingModel` is also important to make sure we have basic tests for

## Tooling

- Switch from [poetry](https://python-poetry.org) to [uv](https://docs.astral.sh/uv/)
- Make sure main dev tools ([ruff](https://docs.astral.sh/ruff/), [mypy](https://www.mypy-lang.org/)) are using updated versions
- Switch from using the poetry-based poe-the-poet task runner to [task](https://taskfile.dev) and make the new `Taskfile.toml` to take in the tasks there
- Update versions of dependencies
