# tests/test_bt_765_PartFrameworkAgreement.py
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
    configure_logging()
    return logging.getLogger(__name__)


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


@pytest.mark.parametrize(
    ("framework_code", "expected_result"),
    [
        (
            "fa-wo-rc",
            {
                "tender": {
                    "techniques": {
                        "hasFrameworkAgreement": True,
                        "frameworkAgreement": {"method": "withoutReopeningCompetition"},
                    }
                }
            },
        ),
        (
            "fa-w-rc",
            {
                "tender": {
                    "techniques": {
                        "hasFrameworkAgreement": True,
                        "frameworkAgreement": {"method": "withReopeningCompetition"},
                    }
                }
            },
        ),
        (
            "fa-mix",
            {
                "tender": {
                    "techniques": {
                        "hasFrameworkAgreement": True,
                        "frameworkAgreement": {
                            "method": "withAndWithoutReopeningCompetition"
                        },
                    }
                }
            },
        ),
        ("none", {"tender": {"techniques": {"hasFrameworkAgreement": False}}}),
    ],
)
def test_bt_765_part_framework_agreement(
    tmp_path, setup_logging, temp_output_dir, framework_code, expected_result
) -> None:
    logger = setup_logging
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="part">PART-0001</cbc:ID>
        <cac:TenderingProcess>
            <cac:ContractingSystem>
                <cbc:ContractingSystemTypeCode listName="framework-agreement">{framework_code}</cbc:ContractingSystemTypeCode>
            </cac:ContractingSystem>
        </cac:TenderingProcess>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / f"test_input_part_framework_agreement_{framework_code}.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result for %s: %s", framework_code, json.dumps(result, indent=2))

    assert "tender" in result
    assert "techniques" in result["tender"]

    expected_techniques = expected_result["tender"]["techniques"]
    assert result["tender"]["techniques"] == expected_techniques


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
