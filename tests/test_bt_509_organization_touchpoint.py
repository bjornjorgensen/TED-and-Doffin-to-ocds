# tests/test_bt_509_organization_touchpoint.py
from pathlib import Path
import pytest
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_509_organization_touchpoint_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:organizations>
                            <efac:organization>
                                <efac:company>
                                    <cac:partyLegalEntity>
                                        <cbc:companyID>998298</cbc:companyID>
                                    </cac:partyLegalEntity>
                                </efac:company>
                                <efac:touchpoint>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:partyIdentification>
                                    <cbc:EndpointID>https://drive.xpertpro.eu/</cbc:EndpointID>
                                </efac:touchpoint>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_touchpoint_edelivery_gateway.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "TPO-0001"
    assert "eDeliveryGateway" in party
    assert party["eDeliveryGateway"] == "https://drive.xpertpro.eu/"
    assert "identifier" in party
    assert party["identifier"]["id"] == "998298"
    assert party["identifier"]["scheme"] == "internal"


if __name__ == "__main__":
    pytest.main()
