# tests/test_BT_195_BT_554_Tender.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

logger = logging.getLogger(__name__)

def test_bt_195_bt_554_unpublished_subcontracting_description_tender_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                <efac:SubcontractingTerm>
                    <efbc:TermCode listName="applicability"/>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode listName="non-publication-identifier">sub-des</efbc:FieldIdentifierCode>
                    </efac:FieldsPrivacy>
                </efac:SubcontractingTerm>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_subcontracting_description_tender.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result.get("withheldInformation", [])) > 0, "Expected at least one withheld information item"

    expected_item = {
        "id": "sub-des-TEN-0001",
        "field": "sub-des",
        "name": "Subcontracting Description"
    }
    assert expected_item in result.get("withheldInformation", []), f"Expected {expected_item} in withheldInformation"

    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

if __name__ == "__main__":
    pytest.main()