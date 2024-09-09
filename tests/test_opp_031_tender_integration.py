import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_opp_031_tender_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efac:ContractTerm>
                    <efbc:TermCode listName="contract-detail">soc-stand</efbc:TermCode>
                    <efbc:TermDescription>Description of the social-standards blablabla ...</efbc:TermDescription>
                </efac:ContractTerm>
                <efac:ContractTerm>
                    <efbc:TermCode listName="contract-detail">exc-right</efbc:TermCode>
                    <efbc:TermDescription>Exclusive rights description</efbc:TermDescription>
                </efac:ContractTerm>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_contract_conditions.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "contractTerms" in lot
    assert (
        lot["contractTerms"]["socialStandards"]
        == "Description of the social-standards blablabla ..."
    )
    assert lot["contractTerms"]["hasExclusiveRights"] == True
