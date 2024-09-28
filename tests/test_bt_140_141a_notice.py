# tests/test_bt_140_141a_notice.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_140_141a_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Changes>
                            <efac:Change>
                                <efbc:ChangedSectionIdentifier>LOT-0001</efbc:ChangedSectionIdentifier>
                                <efbc:ChangeDescription languageID="ENG">The changes have been applied to Lot 1</efbc:ChangeDescription>
                            </efac:Change>
                            <efac:Change>
                                <efbc:ChangedSectionIdentifier>LOT-0002</efbc:ChangedSectionIdentifier>
                                <efbc:ChangeDescription languageID="ENG">The changes have been applied to Lot 2</efbc:ChangeDescription>
                            </efac:Change>
                            <efac:ChangeReason>
                                <cbc:ReasonCode listName="change-corrig-justification">update-add</cbc:ReasonCode>
                            </efac:ChangeReason>
                        </efac:Changes>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_change_reason_code_and_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "amendments" in result["tender"], "Expected 'amendments' in tender"
    assert (
        len(result["tender"]["amendments"]) == 2
    ), f"Expected 2 amendments, got {len(result['tender']['amendments'])}"

    for i, amendment in enumerate(result["tender"]["amendments"], start=1):
        assert amendment["id"] == str(
            i,
        ), f"Expected amendment id '{i}', got {amendment['id']}"
        assert "relatedLots" in amendment, f"Expected 'relatedLots' in amendment {i}"
        assert amendment["relatedLots"] == [
            f"LOT-000{i}",
        ], f"Expected relatedLots ['LOT-000{i}'], got {amendment['relatedLots']}"
        assert (
            "rationaleClassifications" in amendment
        ), f"Expected 'rationaleClassifications' in amendment {i}"
        assert (
            len(amendment["rationaleClassifications"]) == 1
        ), f"Expected 1 rationaleClassification, got {len(amendment['rationaleClassifications'])}"
        classification = amendment["rationaleClassifications"][0]
        assert (
            classification["id"] == "update-add"
        ), f"Expected classification id 'update-add', got {classification['id']}"
        assert (
            classification["description"] == "Information updated"
        ), f"Expected description 'Information updated', got {classification['description']}"
        assert (
            classification["scheme"] == "eu-change-corrig-justification"
        ), f"Expected scheme 'eu-change-corrig-justification', got {classification['scheme']}"
        assert "description" in amendment, f"Expected 'description' in amendment {i}"
        assert (
            amendment["description"] == f"The changes have been applied to Lot {i}"
        ), f"Expected description 'The changes have been applied to Lot {i}', got {amendment['description']}"


if __name__ == "__main__":
    pytest.main()
