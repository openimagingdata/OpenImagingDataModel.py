"""Represents a CDE Set with its component Elements.
"""

from pydantic import BaseModel


class CDESet(BaseModel):
    """Represents a CDE Set with its component Elements.
    """

    name: str