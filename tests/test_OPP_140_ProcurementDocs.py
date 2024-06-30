# tests/test_OPP_140_ProcurementDocs.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opp_140_procurement_docs_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-03</cbc:ID>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_procurement_documents.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 2

    lot_doc = next((doc for doc in result["tender"]["documents"] if doc["id"] == "20210521/CTFD/ENG/7654-02"), None)
    assert lot_doc is not None
    assert "relatedLots" in lot_doc
    assert lot_doc["relatedLots"] == ["LOT-0001"]

    part_doc = next((doc for doc in result["tender"]["documents"] if doc["id"] == "20210521/CTFD/ENG/7654-03"), None)
    assert part_doc is not None
    assert "relatedLots" not in part_doc

if __name__ == "__main__":
    pytest.main()