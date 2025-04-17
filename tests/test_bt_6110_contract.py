import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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


def test_bt_6110_contract_description(tmp_path, temp_output_dir) -> None:
    """Test extraction of contract EU funds details using Description element."""
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <cbc:Description>Program for the development ...</cbc:Description>
                                </efac:Funding>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_contract_eu_funds_description.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "contracts" in result, "Expected 'contracts' in result"
    assert len(result["contracts"]) == 1
    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert len(contract["finance"]) == 1
    assert contract["finance"][0]["description"] == "Program for the development ..."
    assert contract["awardID"] == "RES-0001"


def test_bt_6110_contract_funding_program(tmp_path, temp_output_dir) -> None:
    """Test extraction of contract EU funds details using FundingProgram element."""
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <cbc:FundingProgram>European Regional Development Fund</cbc:FundingProgram>
                                </efac:Funding>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_contract_eu_funds_program.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "contracts" in result, "Expected 'contracts' in result"
    assert len(result["contracts"]) == 1
    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert len(contract["finance"]) == 1
    assert contract["finance"][0]["description"] == "European Regional Development Fund"
    assert contract["awardID"] == "RES-0001"


def test_bt_6110_contract_both_funding_elements(tmp_path, temp_output_dir) -> None:
    """Test extraction of contract EU funds details using both Description and FundingProgram elements."""
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <cbc:FundingProgram>European Regional Development Fund</cbc:FundingProgram>
                                    <cbc:Description>Program for the development of rural areas</cbc:Description>
                                </efac:Funding>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_contract_eu_funds_both.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "contracts" in result, "Expected 'contracts' in result"
    assert len(result["contracts"]) == 1
    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert len(contract["finance"]) == 2
    
    descriptions = [finance["description"] for finance in contract["finance"]]
    assert "European Regional Development Fund" in descriptions
    assert "Program for the development of rural areas" in descriptions
    assert contract["awardID"] == "RES-0001"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
