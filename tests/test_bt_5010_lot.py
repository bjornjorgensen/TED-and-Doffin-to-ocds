# tests/test_bt_5010_lot.py
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
    configure_logging()
    return logging.getLogger(__name__)


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


def test_bt_5010_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:Funding>
                                    <efbc:FinancingIdentifier>CON_PRO-123/ABC</efbc:FinancingIdentifier>
                                </efac:Funding>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_eu_funds_financing_identifier.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "parties" in result, "Expected 'parties' in result"
    eu_party = next(
        (party for party in result["parties"] if party["name"] == "European Union"),
        None,
    )
    assert eu_party is not None, "Expected to find European Union party"
    assert "roles" in eu_party, "Expected 'roles' in European Union party"
    assert (
        "funder" in eu_party["roles"]
    ), "Expected 'funder' role in European Union party roles"

    assert "planning" in result, "Expected 'planning' in result"
    assert "budget" in result["planning"], "Expected 'budget' in planning"
    assert "finance" in result["planning"]["budget"], "Expected 'finance' in budget"

    finance = result["planning"]["budget"]["finance"]
    assert len(finance) == 1, f"Expected 1 finance item, got {len(finance)}"
    assert (
        finance[0]["id"] == "CON_PRO-123/ABC"
    ), f"Expected finance id 'CON_PRO-123/ABC', got {finance[0]['id']}"
    assert (
        finance[0]["financingParty"]["name"] == "European Union"
    ), "Expected financingParty name to be 'European Union'"
    assert (
        finance[0]["financingParty"]["id"] == eu_party["id"]
    ), "Expected financingParty id to match European Union party id"
    assert finance[0]["relatedLots"] == [
        "LOT-0001",
    ], "Expected relatedLots to contain 'LOT-0001'"


if __name__ == "__main__":
    pytest.main(["-v"])
