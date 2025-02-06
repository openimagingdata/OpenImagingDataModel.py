test_finding_model = {
    "finding_name": "adrenal nodule",
    "description": "",
    "attributes": [
        {
            "name": "presence",
            "description": None,
            "type": "choice",
            "values": [
                {
                    "name": "present",
                    "description": "None"
                },
                {
                    "name": "absent",
                    "description": "None"
                }
            ],
            "required": True
        },
        {
            "name": "status",
            "description": None,
            "type": "choice",
            "values": [
                {
                    "name": "new",
                    "description": "None"
                },
                {
                    "name": "stable",
                    "description": "None"
                },
                {
                    "name": "enlarged",
                    "description": "None"
                }
            ],
            "required": True
        },
        {
            "name": "size",
            "description": None,
            "type": "numeric",
            "minimum": None,
            "maximum": None,
            "unit": "mm",
            "required": True
        },
        {
            "name": "side",
            "description": None,
            "type": "choice",
            "values": [
                {
                    "name": "right",
                    "description": "None"
                },
                {
                    "name": "left",
                    "description": "None"
                }
            ],
            "required": True
        },
        {
            "name": "Hounsfield units (HU)",
            "description": "Hounsfield units (HU) at non-contrast CT",
            "type": "numeric",
            "minimum": None,
            "maximum": None,
            "unit": None,
            "required": True
        },
        {
            "name": "enhancement pattern",
            "description": None,
            "type": "choice",
            "values": [
                {
                    "name": "nonenhancing",
                    "description": "None"
                },
                {
                    "name": "enhancing",
                    "description": "None"
                },
                {
                    "name": "rapid wash-in and wash-out",
                    "description": "None"
                },
                {
                    "name": "delayed wash-out",
                    "description": "None"
                }
            ],
            "required": True
        }
    ]
}