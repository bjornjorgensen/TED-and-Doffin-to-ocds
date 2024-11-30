# tests/test_bt_111_Lot.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_111_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cac:SubsequentProcessTenderRequirement>
                        <cbc:Name>buyer-categories</cbc:Name>
                        <cbc:Description languageID="ENG">Offices of the "greater region" ...</cbc:Description>
                    </cac:SubsequentProcessTenderRequirement>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cac:SubsequentProcessTenderRequirement>
                        <cbc:Name>buyer-categories</cbc:Name>
                        <cbc:Description languageID="ENG">All hospitals in the Tuscany region</cbc:Description>
                    </cac:SubsequentProcessTenderRequirement>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_framework_buyer_categories.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert "techniques" in lot_1, "Expected 'techniques' in LOT-0001"
    assert (
        "frameworkAgreement" in lot_1["techniques"]
    ), "Expected 'frameworkAgreement' in LOT-0001 techniques"
    assert (
        lot_1["techniques"]["frameworkAgreement"]["buyerCategories"]
        == 'Offices of the "greater region" ...'
    ), "Unexpected buyerCategories for LOT-0001"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "techniques" in lot_2, "Expected 'techniques' in LOT-0002"
    assert (
        "frameworkAgreement" in lot_2["techniques"]
    ), "Expected 'frameworkAgreement' in LOT-0002 techniques"
    assert (
        lot_2["techniques"]["frameworkAgreement"]["buyerCategories"]
        == "All hospitals in the Tuscany region"
    ), "Unexpected buyerCategories for LOT-0002"


if __name__ == "__main__":
    pytest.main(["-v"])
