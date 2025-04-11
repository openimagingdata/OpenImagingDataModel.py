import pytest
import json
from pathlib import Path
from typing import List, Optional
from scripts.finding_to_cde import finding_json_to_cde_set, create_specialty
from openimagingdatamodel.cde_set.data.finding_test_data import test_finding_model
from openimagingdatamodel.cde_set.data.sample_finding_json import sample_finding_json

finding_model_test_data = test_finding_model
finding_model_oifma = sample_finding_json

def test_create_specialty_valid():
    specialty = create_specialty("Chest")
    assert specialty.name == "Chest"
    assert specialty.abbreviation=="CH"

def test_create_specialty_invalid():
    with pytest.raises(ValueError, match="Specialty 'Invalid' not found."):
        create_specialty("Invalid")
'''
def test_finding_json_to_cde_set_valid():
    test_finding_model = finding_model_test_data
    specialty = "Chest"
    result = finding_json_to_cde_set(test_finding_model, specialty)
    assert isinstance(result, str)
    result_json = json.loads(result)
    assert "specialties" in result_json
    assert "name" in result_json
    assert "elements" in result_json
    assert "id" in result_json
    assert "schema_version" in result_json
    assert "current_status" in result_json
    assert "set_version" in result_json
    assert "description" in result_json
'''

def test_finding_json_to_cde_set_oifma():
    test_finding_model = finding_model_oifma
    specialty = "Chest"
    result = finding_json_to_cde_set(test_finding_model, specialty)
    assert isinstance(result, str)
    result_json = json.loads(result)
    assert "specialties" in result_json
    assert "name" in result_json
    assert "elements" in result_json
    assert "id" in result_json
    assert "schema_version" in result_json
    assert "current_status" in result_json
    assert "set_version" in result_json
    assert "description" in result_json
    print(result_json)