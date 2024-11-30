# tests/test_bt_735_LotResult.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.bt_735_lotresult import (
    merge_cvd_contract_type_lotresult,
    parse_cvd_contract_type_lotresult,
)
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def xml_template() -> str:
    """XML template with properly defined namespaces."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                <cbc:ID>{lot_id}</cbc:ID>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efbc:ProcurementCategoryCode listName="cvd-contract-type">{cvd_code}</efbc:ProcurementCategoryCode>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


@pytest.mark.parametrize(
    ("lot_id", "cvd_code", "expected_description"),
    [
        ("RES-0001", "oth-serv-contr", "Other service contract"),
        ("RES-0002", "pass-tran-serv", "Passenger road transport services"),
        ("RES-0003", "veh-acq", "Vehicle purchase, lease or rent"),
    ],
)
def test_cvd_contract_type_parsing(
    xml_template, lot_id, cvd_code, expected_description
) -> None:
    xml_content = xml_template.format(lot_id=lot_id, cvd_code=cvd_code)
    result = parse_cvd_contract_type_lotresult(xml_content)

    assert result is not None
    assert "awards" in result
    award = result["awards"][0]
    classification = award["items"][0]["additionalClassifications"][0]

    assert award["id"] == lot_id
    assert classification["id"] == cvd_code
    assert classification["scheme"] == "eu-cvd-contract-type"
    assert classification["description"] == expected_description


def test_invalid_cvd_code(xml_template) -> None:
    xml_content = xml_template.format(lot_id="RES-0001", cvd_code="invalid-code")
    result = parse_cvd_contract_type_lotresult(xml_content)

    assert result is not None
    classification = result["awards"][0]["items"][0]["additionalClassifications"][0]
    assert classification["id"] == "invalid-code"
    assert classification["description"] == "Unknown CVD contract type"


def test_merge_with_existing_award() -> None:
    release_json = {
        "awards": [
            {"id": "RES-0001", "items": [{"id": "1", "additionalClassifications": []}]}
        ]
    }

    new_data = {
        "awards": [
            {
                "id": "RES-0001",
                "items": [
                    {
                        "id": "1",
                        "additionalClassifications": [
                            {
                                "id": "oth-serv-contr",
                                "scheme": "eu-cvd-contract-type",
                                "description": "Other service contract",
                            }
                        ],
                    }
                ],
            }
        ]
    }

    merge_cvd_contract_type_lotresult(release_json, new_data)

    award = release_json["awards"][0]
    classification = award["items"][0]["additionalClassifications"][0]
    assert classification["id"] == "oth-serv-contr"
    assert classification["scheme"] == "eu-cvd-contract-type"


def test_no_cvd_contract_type(xml_template) -> None:
    modified_template = xml_template.replace(
        '<efbc:ProcurementCategoryCode listName="cvd-contract-type">{cvd_code}</efbc:ProcurementCategoryCode>',
        "",
    )
    xml_content = modified_template.format(lot_id="RES-0001", cvd_code="")
    result = parse_cvd_contract_type_lotresult(xml_content)
    assert result is None


def test_bt_735_lotresult_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                <cbc:ID>RES-0001</cbc:ID>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efbc:ProcurementCategoryCode listName="cvd-contract-type">oth-serv-contr</efbc:ProcurementCategoryCode>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_cvd_contract_type_lotresult.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)
    logger.info("Output directory: %s", temp_output_dir)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 1, f"Expected 1 award, got {len(result['awards'])}"

    award = result["awards"][0]
    assert award["id"] == "RES-0001", f"Expected award id 'RES-0001', got {award['id']}"
    assert "items" in award, "Expected 'items' in award"
    assert len(award["items"]) == 1, f"Expected 1 item, got {len(award['items'])}"

    item = award["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert (
        "additionalClassifications" in item
    ), "Expected 'additionalClassifications' in item"
    assert (
        len(item["additionalClassifications"]) == 1
    ), f"Expected 1 additional classification, got {len(item['additionalClassifications'])}"

    classification = item["additionalClassifications"][0]
    assert (
        classification["id"] == "oth-serv-contr"
    ), f"Expected classification id 'oth-serv-contr', got {classification['id']}"
    assert (
        classification["scheme"] == "eu-cvd-contract-type"
    ), f"Expected scheme 'eu-cvd-contract-type', got {classification['scheme']}"
    assert (
        classification["description"] == "Other service contract"
    ), f"Expected description 'Other service contract', got {classification['description']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
