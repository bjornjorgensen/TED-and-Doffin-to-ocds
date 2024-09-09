# tests/test_OPP_034_Tender.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_opp_034_tender_integration(tmp_path):
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
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ContractTerm>
                                    <efac:FinancialPerformanceRequirement>
                                        <efbc:FinancialPerformanceTypeCode>penalty</efbc:FinancialPerformanceTypeCode>
                                        <efbc:FinancialPerformanceDescription>Penalty for late delivery</efbc:FinancialPerformanceDescription>
                                    </efac:FinancialPerformanceRequirement>
                                </efac:ContractTerm>
                                <efac:ContractTerm>
                                    <efac:FinancialPerformanceRequirement>
                                        <efbc:FinancialPerformanceTypeCode>reward</efbc:FinancialPerformanceTypeCode>
                                        <efbc:FinancialPerformanceDescription>Bonus for early completion</efbc:FinancialPerformanceDescription>
                                    </efac:FinancialPerformanceRequirement>
                                </efac:ContractTerm>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_penalties_and_rewards.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "penaltiesAndRewards" in lot, "Expected 'penaltiesAndRewards' in lot"
    assert (
        "penalties" in lot["penaltiesAndRewards"]
    ), "Expected 'penalties' in penaltiesAndRewards"
    assert (
        "rewards" in lot["penaltiesAndRewards"]
    ), "Expected 'rewards' in penaltiesAndRewards"
    assert lot["penaltiesAndRewards"]["penalties"] == [
        "Penalty for late delivery"
    ], "Unexpected penalties"
    assert lot["penaltiesAndRewards"]["rewards"] == [
        "Bonus for early completion"
    ], "Unexpected rewards"


if __name__ == "__main__":
    pytest.main()
