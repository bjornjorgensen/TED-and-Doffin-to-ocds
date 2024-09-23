# tests/test_BT_15_Lot_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_15_lot_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <cbc:DocumentType>non-restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-03</cbc:ID>
                    <cbc:DocumentType>non-restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo-part</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_documents_url.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert (
        len(result["tender"]["documents"]) == 2
    ), f"Expected 2 documents, got {len(result['tender']['documents'])}"

    lot_document = next(
        doc
        for doc in result["tender"]["documents"]
        if doc["id"] == "20210521/CTFD/ENG/7654-02"
    )
    assert (
        lot_document["documentType"] == "biddingDocuments"
    ), f"Expected documentType 'biddingDocuments', got {lot_document['documentType']}"
    assert (
        lot_document["url"] == "https://mywebsite.com/proc/2019024/accessinfo"
    ), "Unexpected URL for lot document"
    assert "relatedLots" in lot_document, "Expected 'relatedLots' in lot document"
    assert lot_document["relatedLots"] == [
        "LOT-0001",
    ], f"Expected relatedLots ['LOT-0001'], got {lot_document['relatedLots']}"

    part_document = next(
        doc
        for doc in result["tender"]["documents"]
        if doc["id"] == "20210521/CTFD/ENG/7654-03"
    )
    assert (
        part_document["documentType"] == "biddingDocuments"
    ), f"Expected documentType 'biddingDocuments', got {part_document['documentType']}"
    assert (
        part_document["url"] == "https://mywebsite.com/proc/2019024/accessinfo-part"
    ), "Unexpected URL for part document"
    assert (
        "relatedLots" not in part_document
    ), "Unexpected 'relatedLots' in part document"


if __name__ == "__main__":
    pytest.main()
