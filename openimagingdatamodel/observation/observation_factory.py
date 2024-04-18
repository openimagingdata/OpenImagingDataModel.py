import uuid

from caseswitcher import CaseSwitcher
from nanoid import generate as generate_nanoid

from openimagingdatamodel.cde_set import CdeSet

from .observation import Identifier, Observation, StatusValue


class ObservationFactory:
    def __init__(self, cde_set: CdeSet):
        self.cde_set = cde_set

    def generate_observation_id(self) -> str:
        finding_name = CaseSwitcher.to_snake(self.cde_set.name)
        return f"{finding_name}_{generate_nanoid(size=10)}"

    def generate_observation_identifier(self, identifier: str | None = None) -> Identifier:
        identifier = identifier or "urn:oid:2.25." + str(uuid.uuid4().int)
        return Identifier.model_parse(system="urn:dicom:uid", value=identifier)

    DEFAULT_STATUS: StatusValue = "preliminary"

    def create_observation(
        self,
        /,
        id: str | None = None,
        identifier: str | Identifier | None = None,
        status: StatusValue | None = None,
    ) -> Observation:
        id = id or self.generate_observation_id()
        if not isinstance(identifier, Identifier):
            identifier = self.generate_observation_identifier(identifier)
        status = status or self.DEFAULT_STATUS
        return Observation()
