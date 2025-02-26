# tests/test_bt_171_Tender.py

import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_171_tender import (
    merge_tender_rank,
    parse_tender_rank,
)


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_parse_tender_rank() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <cbc:RankCode>1</cbc:RankCode>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:noticeResult>
    </ContractAwardNotice>
    """

    result = parse_tender_rank(xml_content)

    assert result == {
        "bids": {
            "details": [{"id": "TEN-0001", "rank": 1, "relatedLots": ["LOT-0001"]}],
        },
    }


def test_merge_tender_rank() -> None:
    release_json = {}

    tender_rank_data = {
        "bids": {
            "details": [{"id": "TEN-0001", "rank": 1, "relatedLots": ["LOT-0001"]}],
        },
    }

    merge_tender_rank(release_json, tender_rank_data)

    assert release_json == tender_rank_data


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
