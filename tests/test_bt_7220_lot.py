import json
import logging
import tempfile
from pathlib import Path

import pytest

from ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    """Configure logging for tests."""
    configure_logging("DEBUG")
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file: Path, output_dir: Path) -> dict:
    """Helper function to run main and get JSON result."""
    main(
        input_path=str(xml_file),
        output_folder=str(output_dir),
        ocid_prefix="ocds-test-prefix",
        scheme="test-scheme",
    )

    output_files = list(output_dir.glob("*_release_*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"

    with output_files[0].open() as f:
        return json.load(f)


def test_bt_7220_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test BT-7220-Lot EU Funds Programme integration."""
    logger = setup_logging

    # Test input XML with EU funds programme data
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice
        xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>folder-1</cbc:ContractFolderID>
        <cbc:IssueDate>2024-01-01</cbc:IssueDate>
        <cbc:IssueTime>12:00:00Z</cbc:IssueTime>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:Funding>
                                    <cbc:FundingProgramCode listName="eu-programme">ERDF_2021</cbc:FundingProgramCode>
                                </efac:Funding>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """

    # Write test XML file
    xml_file = tmp_path / "test_bt_7220_lot.xml"
    xml_file.write_text(xml_content)

    # Run conversion and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Generated OCDS: %s", json.dumps(result, indent=2))

    # Verify the lots array exists
    assert "lots" in result, "Expected 'lots' in root of release"

    # Verify we have exactly one lot
    assert len(result["lots"]) == 1, f"Expected 1 lot, got {len(result['lots'])}"

    # Get the lot and verify its structure
    lot = result["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"

    # Verify the planning budget finance structure
    assert "planning" in lot, "Missing 'planning' in lot"
    assert "budget" in lot["planning"], "Missing 'budget' in lot planning"
    assert "finance" in lot["planning"]["budget"], "Missing 'finance' in lot budget"

    # Verify finance array
    finance_array = lot["planning"]["budget"]["finance"]
    assert (
        len(finance_array) == 1
    ), f"Expected 1 finance entry, got {len(finance_array)}"

    # Verify finance entry
    finance = finance_array[0]
    assert finance["id"] == "1", f"Expected finance id '1', got {finance['id']}"
    assert (
        finance["title"] == "ERDF_2021"
    ), f"Expected finance title 'ERDF_2021', got {finance['title']}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
