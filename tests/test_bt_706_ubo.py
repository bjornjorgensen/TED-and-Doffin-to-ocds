import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_706_ubo import (
    merge_ubo_nationality,
    parse_ubo_nationality,
)


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_ubo_nationality(setup_logging) -> None:
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efext:UBLExtensions>
            <efext:UBLExtension>
                <efext:ExtensionContent>
                    <efac:Organizations>
                        <efac:Organization>
                            <efac:Company>
                                <cac:PartyIdentification>
                                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                </cac:PartyIdentification>
                            </efac:Company>
                        </efac:Organization>
                        <efac:UltimateBeneficialOwner>
                            <cbc:ID schemeName="ubo">ubo-0001</cbc:ID>
                            <efac:Nationality>
                                <cbc:NationalityID>DEU</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                    </efac:Organizations>
                </efext:ExtensionContent>
            </efext:UBLExtension>
        </efext:UBLExtensions>
    </root>
    """

    result = parse_ubo_nationality(xml_content)
    # logger.info("Parse result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert len(result["parties"][0]["beneficialOwners"]) == 1
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert result["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]


def test_merge_ubo_nationality(setup_logging) -> None:
    logger = setup_logging

    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing organization"}]}

    ubo_nationality_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "ubo-0001", "nationalities": ["DE"]}],
            },
        ],
    }

    merge_ubo_nationality(release_json, ubo_nationality_data)
    # logger.info("Merged result: %s", json.dumps(release_json, indent=2) # Logging disabled)

    assert "beneficialOwners" in release_json["parties"][0]
    assert len(release_json["parties"][0]["beneficialOwners"]) == 1
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert release_json["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]


def test_bt_706_ubo_nationality_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efext:UBLExtensions>
            <efext:UBLExtension>
                <efext:ExtensionContent>
                    <efac:Organizations>
                        <efac:Organization>
                            <efac:Company>
                                <cac:PartyIdentification>
                                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                </cac:PartyIdentification>
                            </efac:Company>
                        </efac:Organization>
                        <efac:UltimateBeneficialOwner>
                            <cbc:ID schemeName="ubo">ubo-0001</cbc:ID>
                            <efac:Nationality>
                                <cbc:NationalityID>DEU</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                        <efac:UltimateBeneficialOwner>
                            <cbc:ID schemeName="ubo">ubo-0002</cbc:ID>
                            <efac:Nationality>
                                <cbc:NationalityID>FRA</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                    </efac:Organizations>
                </efext:ExtensionContent>
            </efext:UBLExtension>
        </efext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_ubo_nationality.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "parties" in result
    assert len(result["parties"]) == 1

    beneficial_owners = result["parties"][0].get("beneficialOwners", [])
    assert len(beneficial_owners) == 2

    ubo_1 = next((ubo for ubo in beneficial_owners if ubo["id"] == "ubo-0001"), None)
    assert ubo_1 is not None
    assert ubo_1["nationalities"] == ["DE"]

    ubo_2 = next((ubo for ubo in beneficial_owners if ubo["id"] == "ubo-0002"), None)
    assert ubo_2 is not None
    assert ubo_2["nationalities"] == ["FR"]


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
