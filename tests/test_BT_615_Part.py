# tests/test_BT_615_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_615_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <cbc:DocumentType>restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_documents_restricted_url_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert len(result["tender"]["documents"]) == 1, f"Expected 1 document, got {len(result['tender']['documents'])}"

    document = result["tender"]["documents"][0]
    assert document["id"] == "20210521/CTFD/ENG/7654-02", f"Expected document id '20210521/CTFD/ENG/7654-02', got {document['id']}"
    assert document["accessDetailsURL"] == "https://mywebsite.com/proc/2019024/accessinfo", f"Expected accessDetailsURL 'https://mywebsite.com/proc/2019024/accessinfo', got {document['accessDetailsURL']}"

if __name__ == "__main__":
    pytest.main()