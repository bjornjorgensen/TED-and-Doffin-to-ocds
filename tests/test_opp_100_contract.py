# tests/test_OPP_100_Contract.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opp_100_contract_integration(tmp_path):
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
                        <efac:noticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <cac:noticeDocumentReference>
                                    <cbc:ID schemeName="ojs-notice-id">62783-2020</cbc:ID>
                                </cac:noticeDocumentReference>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_framework_notice_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "contracts" in result
    assert len(result["contracts"]) == 1
    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert contract["awardID"] == "RES-0001"
    assert "relatedProcesses" in contract
    assert len(contract["relatedProcesses"]) == 1
    related_process = contract["relatedProcesses"][0]
    assert related_process["id"] == "1"
    assert related_process["scheme"] == "ojs-notice-id"
    assert related_process["identifier"] == "62783-2020"
    assert related_process["relationship"] == ["framework"]


if __name__ == "__main__":
    pytest.main()