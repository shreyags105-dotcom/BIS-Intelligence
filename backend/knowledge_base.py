# Temporary mock knowledge base until Rohan sends the final dataset

MOCK_BIS_DATABASE = {
    "IS 2347": {
        "product_name": "Pressure Cooker",
        "standard_id": "IS 2347",
        "scope": "Domestic pressure cookers made of stainless steel or aluminum alloy.",
        "requirements": [
            "Must use food-grade stainless steel or aluminum alloy meeting IS 2347 specs.",
            "Gasket must be non-toxic and temperature resistant.",
            "Safety valve must operate between specified burst pressure thresholds."
        ],
        "testing": [
            "Hydrostatic pressure test (1.5x working pressure)",
            "Bursting test for safety valve",
            "Thermal shock test for handles and lid knobs"
        ],
        "documents": [
            "Factory layout plan & manufacturing machinery list",
            "Calibration certificates for pressure gauges & testing equipment",
            "In-house laboratory test report sample"
        ],
        "certification_scheme": "Scheme-I (ISI Mark Scheme / Option 1 Normal Procedure)",
        "sources": ["BIS Official Manakonline Portal", "IS 2347:2017 Gazette Notification"]
    }
}

def get_standard_by_id(standard_id: str):
    clean_id = standard_id.upper().strip()
    return MOCK_BIS_DATABASE.get(clean_id, None)