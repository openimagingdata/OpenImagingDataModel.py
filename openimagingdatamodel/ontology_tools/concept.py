from abc import ABC, abstractmethod
from pprint import pprint
from typing import ClassVar, NamedTuple

from pydantic import BaseModel, Field


# defined a named tuple called Code with three fields: system, code, and display
class Code(NamedTuple):
    system: str
    code: str
    display: str | None = None

    def __str__(self):
        return f"{self.system} {self.code}{f' {self.display}' if self.display else ''}"


class Concept(BaseModel, ABC):
    SYSTEM_NAME: ClassVar[str]
    id: str = Field(alias="_id")
    embedding_vector: list[float] | None = None

    @abstractmethod
    def text_for_embedding(self) -> str: ...

    @abstractmethod
    def to_system_code_display(self) -> Code: ...

    def print(self):
        pprint(self.model_dump(exclude_none=True, exclude={"embedding_vector"}))
