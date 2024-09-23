# tests/test_OPP_052_organization.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opp_052_organization_acquiring_cpb_buyer_indicator_integration(tmp_path):
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
                        <efac:organizations>
                            <efac:organization>
                                <efbc:AcquiringCPBIndicator>true</efbc:AcquiringCPBIndicator>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:partyIdentification>
                                </efac:company>
                            </efac:organization>
                            <efac:organization>
                                <efbc:AcquiringCPBIndicator>false</efbc:AcquiringCPBIndicator>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                                    </cac:partyIdentification>
                                </efac:company>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_acquiring_cpb_buyer_indicator.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    wholesale_buyer = next(
        (party for party in result["parties"] if party["id"] == "ORG-0001"),
        None,
    )
    assert wholesale_buyer is not None
    assert "roles" in wholesale_buyer
    assert "wholesalebuyer" in wholesale_buyer["roles"]

    non_wholesale_buyer = next(
        (party for party in result["parties"] if party["id"] == "ORG-0002"),
        None,
    )
    assert non_wholesale_buyer is not None
    assert (
        "roles" not in non_wholesale_buyer
        or "wholesalebuyer" not in non_wholesale_buyer.get("roles", [])
    )


if __name__ == "__main__":
    pytest.main()
