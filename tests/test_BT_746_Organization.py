# tests/test_BT_746_Organization.py

import pytest
import json
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    configure_logging()
    caplog.set_level(logging.DEBUG)

def test_bt_746_organization_listed(tmp_path, caplog):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
    <ext:UBLExtension>
    <ext:ExtensionContent>
    <efext:EformsExtension>
    <efac:Organizations>
    <efac:Organization>
    <efbc:ListedOnRegulatedMarketIndicator>false</efbc:ListedOnRegulatedMarketIndicator>
    <efac:Company>
    <cac:PartyIdentification>
    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
    </cac:PartyIdentification>
    </efac:Company>
    </efac:Organization>
    </efac:Organizations>
    </efext:EformsExtension>
    </ext:ExtensionContent>
    </ext:UBLExtension>
    </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_organization_listed.xml"
    xml_file.write_text(xml_content)
    
    main(str(xml_file), "ocds-test-prefix")
    
    with open('output.json', 'r') as f:
        result = json.load(f)
    
    logging.debug(f"Result JSON: {result}")
    
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "details" in party, f"'details' not found in party: {party}"
    assert "listedOnRegulatedMarket" in party["details"]
    assert party["details"]["listedOnRegulatedMarket"] == False

    # Print captured logs for debugging
    print("\nCaptured logs:")
    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

if __name__ == "__main__":
    pytest.main()
