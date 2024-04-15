from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Identifier(BaseModel):
    system: str
    value: str


class Coding(BaseModel):
    """COding with system and code.
    Note that the FHIR spec has all fields optional, but we require system and code."""

    system: str  # TODO: Use URI type
    code: str
    version: str | None = None
    display: str | None = None
    user_selected: bool | None = Field(default=None, alias="userSelected")


class CodeableConcept(BaseModel):
    codings: list[Coding] | None = Field(default=None, alias="coding")
    text: str | None = None


StatusValue = Literal[
    "registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"
]


class Observation(BaseModel):
    """
    The Observation class is the model for FHIR Observation objects
    """

    model_config = ConfigDict(allow_population_by_field_name=True)

    resourceType: Literal["Observation"] = "Observation"
    id_: str = Field(alias="id")
    identifiers: list[Identifier] | None = Field(default=None, alias="identifier")
    status: StatusValue
    # subject
    # focus
    # derivedFrom
    # bodySite
    # components


SAMPLE_OBSERVATION = """
{
    "resourceType": "Observation",
    "id": "example1OIDMradiologist",
    "identifier": [
        {
            "system": "urn:dicom:uid",
            "value": "urn:oid:1.3.6.1.4.1.14519.5.2.1.4334.1501.109763379583496662079353689166.1",
        }
    ],
    "code": {"coding": [{"system": "https://radelement.org", "code": "RDES195", "display": "Pulmonary Nodule"}]},
    "status": "final",
    "subject": {"reference": "Patient/example1OIDM"},
    "focus": [
        {
            "bodyStructure": [
                {
                    "identifier": {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/uv/dicom-sr/CodeSystem/dicom-identifier-type",
                                    "code": "tracking-uid",
                                    "display": "Tracking UID",
                                }
                            ]
                        },
                        "system": "urn:dicom:uid",
                        "value": "urn:oid:2.25.293638943492893970490299793280.5.9.114.1",
                    },
                    "includedStructure": {
                        "structure": {
                            "valueCodeableConcept": {
                                "coding": [
                                    {"system": "http://radlex.org", "code": "RID50149", "display": "pulmonary nodule"}
                                ]
                            }
                        }
                    },
                }
            ]
        },
        {
            "imagingSelection": [
                {
                    "identifier": {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/uv/dicom-sr/CodeSystem/dicom-identifier-type",
                                    "code": "tracking-uid",
                                    "display": "Tracking UID",
                                }
                            ]
                        },
                        "system": "urn:dicom:uid",
                        "value": "urn:oid:2.25.293638943492893970490299793280.5.9.114.1",
                    },
                    "status": "unknown",
                    "code": {"text": "Region selected from image"},
                    "studyUid": "1.3.6.1.4.1.14519.5.2.1.4334.1501.109763379583496662079353689166",
                    "seriesUid": "1.3.6.1.4.1.14519.5.2.1.4334.1501.493076156577048480691957527964",
                    "instance": [
                        {"uid": "1.3.6.1.4.1.14519.5.2.1.4334.1501.114045620398352064908952520781"},
                        {
                            "imageRegion": [
                                {
                                    "regionType": "circle",
                                    "coordinate": [
                                        374.594249201278,
                                        284.0809371671991,
                                        379.5015974440895,
                                        288.98828541001063,
                                    ],
                                }
                            ]
                        },
                    ],
                }
            ]
        },
    ],
    "bodySite": {
        "code": {
            "coding": [
                {"system": "https://anatomiclocations.org/", "code": "RID1338", "display": "lower lobe of left lung"},
                {"system": "http://snomed.info/sct", "code": "41224006", "display": "left lower lobe"},
            ]
        }
    },
    "derivedFrom": [{"reference": "ImagingStudy/example1OIDMstudy"}],
    "component": [
        {
            "code": {"coding": [{"system": "https://radelement.org", "code": "RDE1717", "display": "Presence"}]},
            "valueCodeableConcept": {"coding": [{"code": "RDE1717.1", "display": "present"}]},
        },
        {
            "code": {"coding": [{"system": "https://radelement.org", "code": "RDE1301", "display": "Composition"}]},
            "valueCodeableConcept": {"coding": [{"code": "RDE1301.0", "display": "solid"}]},
        },
        {
            "code": {"coding": [{"system": "https://radelement.org", "code": "RDE1304", "display": "Location"}]},
            "valueCodeableConcept": {"coding": [{"code": "RDE1304.4", "display": "left lower lobe"}]},
        },
        {
            "code": {"coding": [{"system": "https://radelement.org", "code": "RDE1305", "display": "Morphology"}]},
            "valueCodeableConcept": {"coding": [{"code": "RDE1305.1", "display": "lobulated"}]},
        },
    ],
}
"""
