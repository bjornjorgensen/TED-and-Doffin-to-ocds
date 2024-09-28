# tests/test_bt_737_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_737_lot_integration(tmp_path):
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
                                    <efac:NonOfficialLanguages>
                                        <cac:Language>
                                            <cbc:ID>ENG</cbc:ID>
                                        </cac:Language>
                                        <cac:Language>
                                            <cbc:ID>FRA</cbc:ID>
                                        </cac:Language>
                                    </efac:NonOfficialLanguages>
                                </efext:EformsExtension>
                            </ext:ExtensionContent>
                        </ext:UBLExtension>
                    </ext:UBLExtensions>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_documents_unofficial_language.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert (
        len(result["tender"]["documents"]) == 1
    ), f"Expected 1 document, got {len(result['tender']['documents'])}"

    document = result["tender"]["documents"][0]
    assert (
        document["id"] == "20210521/CTFD/ENG/7654-02"
    ), f"Expected document id '20210521/CTFD/ENG/7654-02', got {document['id']}"
    assert (
        "unofficialTranslations" in document
    ), "Expected 'unofficialTranslations' in document"
    assert (
        set(document["unofficialTranslations"]) == {"en", "fr"}
    ), f"Expected unofficial translations ['en', 'fr'], got {document['unofficialTranslations']}"
    assert "relatedLots" in document, "Expected 'relatedLots' in document"
    assert document["relatedLots"] == [
        "LOT-0001",
    ], f"Expected related lots ['LOT-0001'], got {document['relatedLots']}"


if __name__ == "__main__":
    pytest.main()
