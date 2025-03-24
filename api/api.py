from fastapi import FastAPI, HTTPException
from openimagingdatamodel.cde_set.finding_model import FindingModel
from openimagingdatamodel.cde_set.set import CDESet
from scripts.finding_to_cde import finding_json_to_cde_set

app = FastAPI()

@app.post("/convert")
def convert_finding(finding: FindingModel):
    try:
        cdeset = finding_json_to_cde_set(finding.model_dump(), "Chest")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cdeset
