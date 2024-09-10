# tests/test_OPT_201_Organization_TouchPoint.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_201_organization_touchpoint_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:TouchPoint>
                            </efac:Organization>
                            <efac:Organization>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0002</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:TouchPoint>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_touchpoint_technical_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    touchpoint_ids = [party["id"] for party in result["parties"]]
    assert "TPO-0001" in touchpoint_ids
    assert "TPO-0002" in touchpoint_ids


if __name__ == "__main__":
    pytest.main()
