# tests/test_OPT_300_procedure_sprovider.py
from pathlib import Path
import pytest
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_300_procedure_sprovider_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:Contractingparty>
            <cac:party>
                <cac:ServiceProviderparty>
                    <cac:party>
                        <cac:partyIdentification>
                            <cbc:ID>ORG-0001</cbc:ID>
                        </cac:partyIdentification>
                    </cac:party>
                </cac:ServiceProviderparty>
            </cac:party>
        </cac:Contractingparty>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:organizations>
                            <efac:organization>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:partyIdentification>
                                    <cac:partyName>
                                        <cbc:Name languageID="ENG">Service Provider Ltd</cbc:Name>
                                    </cac:partyName>
                                </efac:company>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_sprovider.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Service Provider Ltd"


if __name__ == "__main__":
    pytest.main()
