import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_opp_031_tender_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">soc-stand</efbc:TermCode>
                                    <efbc:TermDescription>Description of the social-standards blablabla ...</efbc:TermDescription>
                                </efac:ContractTerm>
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">exc-right</efbc:TermCode>
                                    <efbc:TermDescription>Exclusive rights description</efbc:TermDescription>
                                </efac:ContractTerm>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_contract_conditions.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "contractTerms" in lot
    assert (
        lot["contractTerms"]["socialStandards"]
        == "Description of the social-standards blablabla ..."
    )
    assert lot["contractTerms"]["hasExclusiveRights"] is True


def test_opp_031_tender_multilingual_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test handling of multilingual contract term descriptions."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cbc:ID>notice-2</cbc:ID>
        <cbc:ContractFolderID>cf-2</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <!-- Term with multiple language variants -->
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">cost-comp</efbc:TermCode>
                                    <efbc:TermDescription languageID="ENG">Financial terms in English</efbc:TermDescription>
                                    <efbc:TermDescription languageID="FRA">Conditions financières en français</efbc:TermDescription>
                                    <efbc:TermDescription languageID="NOR">Økonomiske betingelser på norsk</efbc:TermDescription>
                                </efac:ContractTerm>
                                <!-- Term with single language specified -->
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">other</efbc:TermCode>
                                    <efbc:TermDescription languageID="ENG">Other terms in English only</efbc:TermDescription>
                                </efac:ContractTerm>
                                <!-- Term with no language specified -->
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">publ-ser-obl</efbc:TermCode>
                                    <efbc:TermDescription>Performance terms with no language specified</efbc:TermDescription>
                                </efac:ContractTerm>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_multilingual_contract_conditions.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002"
    assert "contractTerms" in lot
    
    # Verify multilingual term handling - should use first description value
    assert lot["contractTerms"]["financialTerms"] == "Financial terms in English"
    
    # Verify single language term handling
    assert lot["contractTerms"]["otherTerms"] == "Other terms in English only"
    
    # Verify no language specified term handling
    assert lot["contractTerms"]["performanceTerms"] == "Performance terms with no language specified"


def test_opp_031_tender_all_rev_tic_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test that contract terms with 'all-rev-tic' code are discarded."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cbc:ID>notice-3</cbc:ID>
        <cbc:ContractFolderID>cf-3</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                                <!-- This term should be discarded in the mapping -->
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">all-rev-tic</efbc:TermCode>
                                    <efbc:TermDescription>Revenue allocation that should be discarded</efbc:TermDescription>
                                </efac:ContractTerm>
                                <!-- This term should be mapped -->
                                <efac:ContractTerm>
                                    <efbc:TermCode listName="contract-detail">other</efbc:TermCode>
                                    <efbc:TermDescription>Other terms that should be included</efbc:TermDescription>
                                </efac:ContractTerm>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_revenue_allocation_term.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0003"
    
    # Verify the contractTerms object exists
    assert "contractTerms" in lot
    
    # Verify that 'all-rev-tic' term is not included in any contract terms
    assert "revenueAllocation" not in lot["contractTerms"]
    
    # Verify that other terms are included
    assert lot["contractTerms"]["otherTerms"] == "Other terms that should be included"


if __name__ == "__main__":
    pytest.main(["-v"])
