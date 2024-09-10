# tests/test_BT_22_Lot.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_22_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0000</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ID schemeName="InternalID">1</cbc:ID>
                <cbc:Name>Agence centre</cbc:Name>
                <cbc:Description>Service d'entretien de remise en état et de nettoyage des espaces verts.</cbc:Description>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    xml_file = tmp_path / "test_input_lot_internal_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]

    # Check BT-22 implementation
    assert lot["id"] == "LOT-0000"
    assert "identifiers" in lot
    assert isinstance(lot["identifiers"], dict)
    assert lot["identifiers"]["id"] == "1"
    assert lot["identifiers"]["scheme"] == "internal"

    # Check that other fields are present (but don't assert their values)
    assert "title" in lot
    assert "description" in lot

    # Note: The following fields may or may not be present, depending on other implementations
    # We're not asserting their presence or values in this test
    # "awardCriteria", "mainProcurementCategory", "items", "reviewDetails", "coveredBy", "techniques"


if __name__ == "__main__":
    pytest.main()
