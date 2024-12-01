# tests/test_OPP_051_organization.py
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


def test_awarding_cpb_buyer_indicator_values(tmp_path, temp_output_dir) -> None:
    test_cases = [
        # Test case 1: value "true"
        (
            """
            <efac:Organization>
                <efbc:AwardingCPBIndicator>true</efbc:AwardingCPBIndicator>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        """,
            True,
        ),
        # Test case 2: value "TRUE"
        (
            """
            <efac:Organization>
                <efbc:AwardingCPBIndicator>TRUE</efbc:AwardingCPBIndicator>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        """,
            True,
        ),
        # Test case 3: value "false"
        (
            """
            <efac:Organization>
                <efbc:AwardingCPBIndicator>false</efbc:AwardingCPBIndicator>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0003</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        """,
            False,
        ),
        # Test case 4: empty organization
        ("", False),
        # Test case 5: missing indicator
        (
            """
            <efac:Organization>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0004</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        """,
            False,
        ),
    ]

    for org_xml, should_be_included in test_cases:
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
            xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
            xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
            xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
            xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:Organizations>
                                {org_xml}
                            </efac:Organizations>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </ContractNotice>
        """

        xml_file = tmp_path / "test_input_awarding_cpb_buyer_indicator.xml"
        xml_file.write_text(xml_content)

        result = run_main_and_get_result(xml_file, temp_output_dir)

        if should_be_included:
            assert "parties" in result
            assert any(
                (
                    party["id"] == "ORG-0001"
                    and "procuringEntity" in party.get("roles", [])
                )
                or (
                    party["id"] == "ORG-0002"
                    and "procuringEntity" in party.get("roles", [])
                )
                for party in result["parties"]
            )
        else:
            assert all(
                "procuringEntity" not in party.get("roles", [])
                for party in result.get("parties", [])
            )


if __name__ == "__main__":
    pytest.main(["-v"])
