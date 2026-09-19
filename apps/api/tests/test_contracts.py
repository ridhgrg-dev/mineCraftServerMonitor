import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[3]


def test_build_contract_fixtures() -> None:
    schema = json.loads((ROOT / "packages/schemas/v1/build-info.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    fixtures = ROOT / "packages/schemas/fixtures/v1"
    validator.validate(json.loads((fixtures / "build-info.valid.json").read_text()))
    with pytest.raises(ValidationError):
        validator.validate(json.loads((fixtures / "build-info.invalid.json").read_text()))
