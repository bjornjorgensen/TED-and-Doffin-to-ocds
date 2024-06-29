# tests/test_BT_1375_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_1375_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:LotDistribution>
                <cac:LotsGroup>
                    <cbc:LotsGroupID schemeName="LotsGroup">GLO-0001</cbc:LotsGroupID>
                    <cac:ProcurementProjectLotReference>
                        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                    </cac:ProcurementProjectLotReference>
                    <cac:ProcurementProjectLotReference>
                        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                    </cac:ProcurementProjectLotReference>
                </cac:LotsGroup>
                <cac:LotsGroup>
                    <cbc:LotsGroupID schemeName="LotsGroup">GLO-0002</cbc:LotsGroupID>
                    <cac:ProcurementProjectLotReference>
                        <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                    </cac:ProcurementProjectLotReference>
                </cac:LotsGroup>
            </cac:LotDistribution>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_group_lot_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in result['tender']"
    assert len(result["tender"]["lotGroups"]) == 2, f"Expected 2 lot groups, got {len(result['tender']['lotGroups'])}"

    group_1 = next(group for group in result["tender"]["lotGroups"] if group["id"] == "GLO-0001")
    assert "relatedLots" in group_1, "Expected 'relatedLots' in group GLO-0001"
    assert set(group_1["relatedLots"]) == set(["LOT-0001", "LOT-0002"]), f"Expected ['LOT-0001', 'LOT-0002'] in GLO-0001 relatedLots, got {group_1['relatedLots']}"

    group_2 = next(group for group in result["tender"]["lotGroups"] if group["id"] == "GLO-0002")
    assert "relatedLots" in group_2, "Expected 'relatedLots' in group GLO-0002"
    assert group_2["relatedLots"] == ["LOT-0003"], f"Expected ['LOT-0003'] in GLO-0002 relatedLots, got {group_2['relatedLots']}"

if __name__ == "__main__":
    pytest.main()