"""Acceptance test cases: each case represents one request to the model and the expected response.

Add or edit cases below to test different inputs. Each case has:
  - name: short label (e.g. "Paris apartment 50m2 3 rooms")
  - input: the four fields the API expects (surface, rooms, department, type)
  - expected_value_eur: optional; if set, the API response must be close to this value
  - expected_status: optional; if set, the API must return this HTTP status (e.g. 422 for validation errors)
"""

from model_acceptance_tests.test_case_schema import TestCase, TestCaseInput

# Case 1: Paris apartment, 50 m², 3 rooms
case_paris_apartment = TestCase(
    name="Paris apartment 50m2 3 rooms",
    input=TestCaseInput(
        surface_reelle_bati=50.0,
        nombre_pieces_principales=3.0,
        code_departement="75",
        type_local="Appartement",
    ),
)

# Case 2: House in Rhône, 100 m², 5 rooms
case_house_rhone = TestCase(
    name="House 100m2 5 rooms",
    input=TestCaseInput(
        surface_reelle_bati=100.0,
        nombre_pieces_principales=5.0,
        code_departement="69",
        type_local="Maison",
    ),
)

# Case 3: Small studio in Paris
case_paris_studio = TestCase(
    name="Paris studio 18m2 1 room",
    input=TestCaseInput(
        surface_reelle_bati=18.0,
        nombre_pieces_principales=1.0,
        code_departement="75",
        type_local="Appartement",
    ),
)

# Case 4: Large house in a rural department
case_house_rural = TestCase(
    name="Large house rural department 23",
    input=TestCaseInput(
        surface_reelle_bati=200.0,
        nombre_pieces_principales=8.0,
        code_departement="23",
        type_local="Maison",
    ),
)

# Case 5: Dependency (Dépendance) in Bordeaux area
case_dependance_gironde = TestCase(
    name="Dependance Gironde 20m2",
    input=TestCaseInput(
        surface_reelle_bati=20.0,
        nombre_pieces_principales=1.0,
        code_departement="33",
        type_local="Dépendance",
    ),
)

# Case 6: Invalid type_local, API should return 422
case_invalid_type = TestCase(
    name="Invalid type_local",
    input=TestCaseInput(
        surface_reelle_bati=50.0,
        nombre_pieces_principales=3.0,
        code_departement="75",
        type_local="InvalidType",
    ),
    expected_status=422,
)

# Case 7: Corsica, 2A department code
case_corsica = TestCase(
    name="Apartment Corsica 2A 60m2",
    input=TestCaseInput(
        surface_reelle_bati=60.0,
        nombre_pieces_principales=3.0,
        code_departement="2A",
        type_local="Appartement",
    ),
)

ACCEPTANCE_TEST_CASES = [
    case_paris_apartment,
    case_house_rhone,
    case_paris_studio,
    case_house_rural,
    case_dependance_gironde,
    case_invalid_type,
    case_corsica,
]
