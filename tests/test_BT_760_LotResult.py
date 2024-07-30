# tests/test_BT_760_LotResult.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging

def test_bt_760_lotresult_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
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
                                <efac:ReceivedSubmissionsStatistics>
                                    <efbc:StatisticsCode listName="received-submission-type">t-sme</efbc:StatisticsCode>
                                </efac:ReceivedSubmissionsStatistics>
                                <efac:ReceivedSubmissionsStatistics>
                                    <efbc:StatisticsCode listName="received-submission-type">t-oth-eea</efbc:StatisticsCode>
                                </efac:ReceivedSubmissionsStatistics>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_received_submissions_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "bids" in result, "Expected 'bids' in result"
    assert "statistics" in result["bids"], "Expected 'statistics' in bids"
    assert len(result["bids"]["statistics"]) == 2, f"Expected 2 statistics, got {len(result['bids']['statistics'])}"

    stat_sme = next((stat for stat in result["bids"]["statistics"] if stat["measure"] == "smeBids"), None)
    stat_foreign_eu = next((stat for stat in result["bids"]["statistics"] if stat["measure"] == "foreignBidsFromEU"), None)

    assert stat_sme is not None, "Expected to find smeBids statistic"
    assert stat_foreign_eu is not None, "Expected to find foreignBidsFromEU statistic"
    assert stat_sme["relatedLot"] == "LOT-0001", f"Expected relatedLot 'LOT-0001' for smeBids, got {stat_sme['relatedLot']}"
    assert stat_foreign_eu["relatedLot"] == "LOT-0001", f"Expected relatedLot 'LOT-0001' for foreignBidsFromEU, got {stat_foreign_eu['relatedLot']}"

if __name__ == "__main__":
    pytest.main(['-v', '-s'])