# tests/test_bt_165_organization_company.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_165_organization_company import parse_winner_size


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


def test_bt_165_organization_company_eforms_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                    <efbc:CompanySizeCode listName="economic-operator-size">large</efbc:CompanySizeCode>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_winner_size_eforms.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "details" in party, "Expected 'details' in party"
    assert "scale" in party["details"], "Expected 'scale' in party details"
    assert (
        party["details"]["scale"] == "large"
    ), f"Expected scale 'large', got {party['details']['scale']}"


def test_bt_165_organization_company_ted_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT xmlns="http://publications.europa.eu/resource/schema/ted/2016/05/01/ted">
        <FORM_SECTION>
            <F03_2014>
                <AWARD_CONTRACT>
                    <AWARDED_CONTRACT>
                        <CONTRACTORS>
                            <CONTRACTOR>
                                <OFFICIALNAME>Contractor Company Ltd</OFFICIALNAME>
                                <SME>YES</SME>
                            </CONTRACTOR>
                        </CONTRACTORS>
                    </AWARDED_CONTRACT>
                </AWARD_CONTRACT>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_winner_size_ted.xml"
    xml_file.write_text(xml_content)

    # Test direct parsing first
    parsed_data = parse_winner_size(xml_content)
    assert parsed_data is not None, "Expected parsed data to not be None"
    assert len(parsed_data["parties"]) == 1, f"Expected 1 party, got {len(parsed_data['parties'])}"
    assert parsed_data["parties"][0]["id"] == "Contractor Company Ltd"
    assert parsed_data["parties"][0]["details"]["scale"] == "sme"

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) >= 1
    ), f"Expected at least 1 party, got {len(result['parties'])}"

    # Find the contractor party
    contractor_party = next((p for p in result["parties"] if p["id"] == "Contractor Company Ltd"), None)
    assert contractor_party is not None, "Expected to find contractor party"
    assert "details" in contractor_party, "Expected 'details' in party"
    assert "scale" in contractor_party["details"], "Expected 'scale' in party details"
    assert (
        contractor_party["details"]["scale"] == "sme"
    ), f"Expected scale 'sme', got {contractor_party['details']['scale']}"


def test_bt_165_organization_company_ted_no_sme_integration(
    tmp_path, setup_logging
) -> None:
    """Test handling of TED format without SME value."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT xmlns="http://publications.europa.eu/resource/schema/ted/2016/05/01/ted">
        <FORM_SECTION>
            <F03_2014>
                <AWARD_CONTRACT>
                    <AWARDED_CONTRACT>
                        <CONTRACTORS>
                            <CONTRACTOR>
                                <OFFICIALNAME>Contractor Company Ltd</OFFICIALNAME>
                            </CONTRACTOR>
                        </CONTRACTORS>
                    </AWARDED_CONTRACT>
                </AWARD_CONTRACT>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Test direct parsing
    parsed_data = parse_winner_size(xml_content)
    # Without SME element, no parties should be returned
    assert parsed_data is None or len(parsed_data["parties"]) == 0, "Expected no parties when SME element is missing"


def test_bt_165_organization_company_ted_no_integration(
    tmp_path, setup_logging
) -> None:
    """Test handling of TED format with SME=NO value."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT xmlns="http://publications.europa.eu/resource/schema/ted/2016/05/01/ted">
        <FORM_SECTION>
            <F03_2014>
                <AWARD_CONTRACT>
                    <AWARDED_CONTRACT>
                        <CONTRACTORS>
                            <CONTRACTOR>
                                <OFFICIALNAME>Large Company Ltd</OFFICIALNAME>
                                <SME>NO</SME>
                            </CONTRACTOR>
                        </CONTRACTORS>
                    </AWARDED_CONTRACT>
                </AWARD_CONTRACT>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Test direct parsing
    parsed_data = parse_winner_size(xml_content)
    assert parsed_data is not None, "Expected parsed data to not be None"
    assert len(parsed_data["parties"]) == 1, f"Expected 1 party, got {len(parsed_data['parties'])}"
    assert parsed_data["parties"][0]["id"] == "Large Company Ltd"
    assert parsed_data["parties"][0]["details"]["scale"] == "large"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
