# tests/test_bt_195_bt_541_lotsgroup_fixed.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


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


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt195_bt541_lotsgroup_fixed_unpublished_identifier_integration(
    tmp_path,
    setup_logging,
    temp_output_dir,
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:AwardingCriterion>
                    <cac:SubordinateAwardingCriterion>
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:AwardCriterionParameter>
                                            <efbc:ParameterCode listName="number-fixed">awa-cri-num</efbc:ParameterCode>
                                            <efac:FieldsPrivacy>
                                                <efbc:FieldIdentifierCode>awa-cri-num</efbc:FieldIdentifierCode>
                                            </efac:FieldsPrivacy>
                                        </efac:AwardCriterionParameter>
                                    </efext:EformsExtension>
                                </ext:ExtensionContent>
                            </ext:UBLExtension>
                        </ext:UBLExtensions>
                    </cac:SubordinateAwardingCriterion>
                </cac:AwardingCriterion>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt541_lotsgroup_fixed.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "awa-cri-num-fixed-GLO-0001"
    ), "Unexpected id for withheld information"
    assert (
        withheld_item["field"] == "awa-cri-num"
    ), "Unexpected field for withheld information"
    assert (
        withheld_item["name"] == "Award Criterion Number Fixed"
    ), "Unexpected name for withheld information"


def test_bt195_bt541_lotsgroup_fixed_multiple_groups(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:AwardingCriterion>
                    <cac:SubordinateAwardingCriterion>
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:AwardCriterionParameter>
                                            <efbc:ParameterCode listName="number-fixed">awa-cri-num</efbc:ParameterCode>
                                            <efac:FieldsPrivacy>
                                                <efbc:FieldIdentifierCode>awa-cri-num</efbc:FieldIdentifierCode>
                                            </efac:FieldsPrivacy>
                                        </efac:AwardCriterionParameter>
                                    </efext:EformsExtension>
                                </ext:ExtensionContent>
                            </ext:UBLExtension>
                        </ext:UBLExtensions>
                    </cac:SubordinateAwardingCriterion>
                </cac:AwardingCriterion>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="LotsGroup">GLO-0002</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:AwardingCriterion>
                    <cac:SubordinateAwardingCriterion>
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:AwardCriterionParameter>
                                            <efbc:ParameterCode listName="number-fixed">awa-cri-num</efbc:ParameterCode>
                                            <efac:FieldsPrivacy>
                                                <efbc:FieldIdentifierCode>awa-cri-num</efbc:FieldIdentifierCode>
                                            </efac:FieldsPrivacy>
                                        </efac:AwardCriterionParameter>
                                    </efext:EformsExtension>
                                </ext:ExtensionContent>
                            </ext:UBLExtension>
                        </ext:UBLExtensions>
                    </cac:SubordinateAwardingCriterion>
                </cac:AwardingCriterion>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt541_lotsgroup_fixed_multiple_groups.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), "Expected two withheld information items"

    group_ids = ["GLO-0001", "GLO-0002"]
    for withheld_item, group_id in zip(
        result["withheldInformation"],
        group_ids,
        strict=False,
    ):
        assert (
            withheld_item["id"] == f"awa-cri-num-fixed-{group_id}"
        ), f"Unexpected id for withheld information of {group_id}"
        assert (
            withheld_item["field"] == "awa-cri-num"
        ), f"Unexpected field for withheld information of {group_id}"
        assert (
            withheld_item["name"] == "Award Criterion Number Fixed"
        ), f"Unexpected name for withheld information of {group_id}"


def test_bt195_bt541_lotsgroup_fixed_no_unpublished_identifier(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:AwardingCriterion>
                    <cac:SubordinateAwardingCriterion>
                        <!-- No unpublished identifier -->
                    </cac:SubordinateAwardingCriterion>
                </cac:AwardingCriterion>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt541_lotsgroup_fixed_no_unpublished.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
