# tests/test_bt_802_Lot.py
from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")

    output_files = list(output_dir.glob("*.json"))
    logging.info("Output files found: %s", [file.name for file in output_files])
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_802_lot_non_disclosure_agreement_description_integration(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="nda">true</cbc:ExecutionRequirementCode>
                <cbc:Description>A Non Disclosure Agreement will need to be signed.</cbc:Description>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="nda">false</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_non_disclosure_agreement_description.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"

    nda_lots = [
        lot
        for lot in result["tender"]["lots"]
        if "contractTerms" in lot and "nonDisclosureAgreement" in lot["contractTerms"]
    ]
    assert len(nda_lots) == 1, f"Expected one lot with NDA, got {len(nda_lots)}"

    lot_1 = nda_lots[0]
    assert lot_1["id"] == "LOT-0001", f"Expected lot ID 'LOT-0001', got {lot_1['id']}"
    assert (
        lot_1["contractTerms"]["nonDisclosureAgreement"]
        == "A Non Disclosure Agreement will need to be signed."
    ), "Expected 'nonDisclosureAgreement' to match the description for LOT-0001"

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None, "LOT-0002 should be present"
    assert "contractTerms" not in lot_2 or "nonDisclosureAgreement" not in lot_2.get(
        "contractTerms",
        {},
    ), "Did not expect 'nonDisclosureAgreement' in LOT-0002"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
