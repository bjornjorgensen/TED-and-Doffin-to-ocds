# tests/test_OPP_051_Organization.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_opp_051_organization_awarding_cpb_buyer_indicator_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efbc:AwardingCPBIndicator>true</efbc:AwardingCPBIndicator>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:Company>
                            </efac:Organization>
                            <efac:Organization>
                                <efbc:AwardingCPBIndicator>false</efbc:AwardingCPBIndicator>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
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
    xml_file = tmp_path / "test_input_awarding_cpb_buyer_indicator.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    procuring_entity = next(
        (party for party in result["parties"] if party["id"] == "ORG-0001"), None
    )
    assert procuring_entity is not None
    assert "roles" in procuring_entity
    assert "procuringEntity" in procuring_entity["roles"]

    non_procuring_entity = next(
        (party for party in result["parties"] if party["id"] == "ORG-0002"), None
    )
    assert non_procuring_entity is not None
    assert (
        "roles" not in non_procuring_entity
        or "procuringEntity" not in non_procuring_entity.get("roles", [])
    )


if __name__ == "__main__":
    pytest.main()
