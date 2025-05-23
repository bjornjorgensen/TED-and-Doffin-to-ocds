import json
import sys
import tempfile
from pathlib import Path

import pytest
from lxml import etree

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_3201_tender import parse_tender_identifier, determine_scheme


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_3201_tender_identifier_integration(
    tmp_path, temp_output_dir
) -> None:

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:TenderReference>
                                    <cbc:ID>BID ABD/GHI-NL/2020-002</cbc:ID>
                                </efac:TenderReference>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_tender_identifier.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in bids"
    assert (
        len(result["bids"]["details"]) == 1
    ), f"Expected 1 bid, got {len(result['bids']['details'])}"

    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001", f"Expected bid id 'TEN-0001', got {bid['id']}"
    assert "identifiers" in bid, "Expected 'identifiers' in bid"
    assert (
        len(bid["identifiers"]) == 1
    ), f"Expected 1 identifier, got {len(bid['identifiers'])}"

    identifier = bid["identifiers"][0]
    assert (
        identifier["id"] == "BID ABD/GHI-NL/2020-002"
    ), f"Expected identifier id 'BID ABD/GHI-NL/2020-002', got {identifier['id']}"
    assert identifier["scheme"] == "NL-TENDERNL", f"Expected scheme 'NL-TENDERNL', got {identifier['scheme']}"


def test_bt_3201_multiple_tenders():
    """Test parsing multiple tender identifiers in the same XML."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:TenderReference>
                                    <cbc:ID>BID ABD/GHI-NL/2020-002</cbc:ID>
                                </efac:TenderReference>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:TenderReference>
                                    <cbc:ID>BID XYZ/DEU/2020-003</cbc:ID>
                                </efac:TenderReference>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                                <efac:TenderReference>
                                    <cbc:ID>BID 123/GB/2020-004</cbc:ID>
                                </efac:TenderReference>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    
    result = parse_tender_identifier(xml_content)
    
    assert result is not None, "Expected result"
    assert len(result["bids"]["details"]) == 3, f"Expected 3 bids, got {len(result['bids']['details'])}"
    
    # Check first bid
    assert result["bids"]["details"][0]["id"] == "TEN-0001"
    assert result["bids"]["details"][0]["identifiers"][0]["scheme"] == "NL-TENDERNL"
    
    # Check second bid
    assert result["bids"]["details"][1]["id"] == "TEN-0002"
    assert result["bids"]["details"][1]["identifiers"][0]["scheme"] == "DE-TENDERNL"
    
    # Check third bid
    assert result["bids"]["details"][2]["id"] == "TEN-0003"
    assert result["bids"]["details"][2]["identifiers"][0]["scheme"] == "GB-TENDERNL"


def test_determine_scheme():
    """Test the scheme determination logic."""
    test_cases = [
        ("BID ABD/GHI-NL/2020-002", "NL-TENDERNL"),
        ("BID XYZ/DEU/2020-003", "DE-TENDERNL"),
        ("BID 123/GB/2020-004", "GB-TENDERNL"),
        ("BID FRA-PARIS/2021", "FR-TENDERNL"),
        ("BID UNKNOWN/2022", "XX-TENDERNL"),  # Should use default
        ("BID USA/2022", "US-TENDERNL"),      # 3-letter code
        ("BID IT-ROMA/2022", "IT-TENDERNL"),  # 2-letter code
    ]
    
    for identifier, expected_scheme in test_cases:
        result = determine_scheme(identifier)
        assert result == expected_scheme, f"Expected '{expected_scheme}' for '{identifier}', got '{result}'"


if __name__ == "__main__":
    pytest.main(["-v"])
