# tests/test_BT_76_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_76_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a registered company</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a partnership</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_tenderer_legal_form.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert len(result["tender"]["lots"]) == 2, f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")

    assert "contractTerms" in lot1, "Expected 'contractTerms' in LOT-0001"
    assert "tendererLegalForm" in lot1["contractTerms"], "Expected 'tendererLegalForm' in LOT-0001 contractTerms"
    assert lot1["contractTerms"]["tendererLegalForm"] == "The tenderer must be a registered company", \
        "Unexpected tendererLegalForm content for LOT-0001"

    assert "contractTerms" in lot2, "Expected 'contractTerms' in LOT-0002"
    assert "tendererLegalForm" in lot2["contractTerms"], "Expected 'tendererLegalForm' in LOT-0002 contractTerms"
    assert lot2["contractTerms"]["tendererLegalForm"] == "The tenderer must be a partnership", \
        "Unexpected tendererLegalForm content for LOT-0002"

if __name__ == "__main__":
    pytest.main()