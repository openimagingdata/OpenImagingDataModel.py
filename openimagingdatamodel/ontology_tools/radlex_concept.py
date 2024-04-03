from pydantic import BaseModel, ConfigDict, validator
import caseswitcher

# ConfigDict for RadLex Properties
class RadLexConcept(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Field validator for model_config dictionary keys
    @validator('model_config', pre=True)
    def convert_model_config_keys(cls, value):
        if isinstance(value, dict):
            snake_case_config = {}
            for key, val in value.items():
                snake_case_config[caseswitcher.to_snake(key)] = val
            return snake_case_config
        return value