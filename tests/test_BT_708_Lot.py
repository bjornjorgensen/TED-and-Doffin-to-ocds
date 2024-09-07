import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_708_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <ext:UBLExtensions>
                        <ext:UBLExtension>
                            <ext:ExtensionContent>
                                <efext:EformsExtension>
                                    <efac:OfficialLanguages>
                                        <cac:Language>
                                            <cbc:ID>ENG</cbc:ID>
                                        </cac:Language>
                                    </efac:OfficialLanguages>
                                </efext:EformsExtension>
                            </ext:ExtensionContent>
                        </ext:UBLExtension>
                    </ext:UBLExtensions>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_708_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    document = result["tender"]["documents"][0]
    assert document["id"] == "20210521/CTFD/ENG/7654-02"
    assert document["languages"] == ["en"]
    assert document["relatedLots"] == ["LOT-0001"]


if __name__ == "__main__":
    pytest.main()
