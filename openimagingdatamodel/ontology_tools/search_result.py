from pydantic import BaseModel, ConfigDict


class SearchResult(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    system: str
    code: str
    display: str
    score: float

    def print(self):
        print(self.system, self.code, self.display, self.score)
