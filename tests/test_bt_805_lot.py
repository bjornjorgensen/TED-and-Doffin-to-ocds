# tests/test_bt_805_Lot.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt_805_lot_integration(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">eu</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">national</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">none</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_green_procurement_criteria.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert lot["hasSustainability"] is True, "Expected hasSustainability to be True"
    assert "sustainability" in lot, "Expected 'sustainability' in lot"
    assert (
        len(lot["sustainability"]) == 2
    ), f"Expected 2 sustainability entries, got {len(lot['sustainability'])}"

    strategies = [
        item
        for sustainability in lot["sustainability"]
        for item in sustainability["strategies"]
    ]
    assert "euGPPCriteria" in strategies, "Expected 'euGPPCriteria' in strategies"
    assert (
        "nationalGPPCriteria" in strategies
    ), "Expected 'nationalGPPCriteria' in strategies"

    # Check that LOT-0002 is not included
    assert all(
        lot["id"] != "LOT-0002" for lot in result["tender"]["lots"]
    ), "LOT-0002 should not be included"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
