# tests/test_BT_635_LotResult.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt_635_lot_result_integration(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <efac:AppealRequestsStatistics>
                                    <efbc:StatisticsCode listName="irregularity-type">review-requests</efbc:StatisticsCode>
                                    <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                                </efac:AppealRequestsStatistics>
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
    xml_file = tmp_path / "test_input_buyer_review_requests_count.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "statistics" in result, "Expected 'statistics' in result"
    assert (
        len(result["statistics"]) == 1
    ), f"Expected 1 statistic, got {len(result['statistics'])}"

    statistic = result["statistics"][0]
    assert (
        statistic["scope"] == "complaints"
    ), f"Expected scope 'complaints', got {statistic['scope']}"
    assert (
        statistic["relatedLot"] == "LOT-0001"
    ), f"Expected relatedLot 'LOT-0001', got {statistic['relatedLot']}"
    assert statistic["value"] == 2, f"Expected value 2, got {statistic['value']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
