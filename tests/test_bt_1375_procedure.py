# tests/test_bt_1375_procedure.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_1375_procedure_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:LotDistribution>
                <cac:LotsGroup>
                    <cbc:LotsGroupID schemeName="LotsGroup">GLO-0001</cbc:LotsGroupID>
                    <cac:ProcurementProjectLotReference>
                        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                    </cac:ProcurementProjectLotReference>
                </cac:LotsGroup>
            </cac:LotDistribution>
        </cac:TenderingTerms>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_group_lot_identifier.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in tender"
    assert (
        len(result["tender"]["lotGroups"]) == 1
    ), f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"

    lot_group = result["tender"]["lotGroups"][0]
    assert (
        lot_group["id"] == "GLO-0001"
    ), f"Expected lot group id 'GLO-0001', got {lot_group['id']}"
    assert "relatedLots" in lot_group, "Expected 'relatedLots' in lot group"
    assert (
        len(lot_group["relatedLots"]) == 1
    ), f"Expected 1 related lot, got {len(lot_group['relatedLots'])}"
    assert (
        lot_group["relatedLots"][0] == "LOT-0002"
    ), f"Expected related lot 'LOT-0002', got {lot_group['relatedLots'][0]}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
