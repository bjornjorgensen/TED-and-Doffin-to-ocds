# tests/test_OPT_301_part_FiscalLegis.py

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_301_part_fiscallegis_integration(tmp_path):
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
                        <efac:organizations>
                            <efac:organization>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:partyIdentification>
                                </efac:company>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:FiscalLegislationDocumentReference>
                    <cbc:ID>Fiscal1</cbc:ID>
                    <cac:Issuerparty>
                        <cac:partyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:partyIdentification>
                    </cac:Issuerparty>
                </cac:FiscalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_fiscallegis.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "roles" in party
    assert "informationService" in party["roles"]

    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    document = result["tender"]["documents"][0]
    assert document["id"] == "Fiscal1"
    assert "publisher" in document
    assert document["publisher"]["id"] == "ORG-0001"


if __name__ == "__main__":
    pytest.main()