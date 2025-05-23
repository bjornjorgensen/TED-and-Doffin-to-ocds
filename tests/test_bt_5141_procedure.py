# tests/test_bt_5141_procedure.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_5141_procedure_integration(
    tmp_path, temp_output_dir
) -> None:
    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cac:Country>
                        <cbc:IdentificationCode listName="country">GBR</cbc:IdentificationCode>
                    </cac:Country>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_procedure_country.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "deliveryAddresses" in result["tender"]
    ), "Expected 'deliveryAddresses' in tender"
    assert (
        len(result["tender"]["deliveryAddresses"]) == 1
    ), f"Expected 1 delivery address, got {len(result['tender']['deliveryAddresses'])}"

    address = result["tender"]["deliveryAddresses"][0]
    assert "country" in address, "Expected 'country' in delivery address"
    assert (
        address["country"] == "GB"
    ), f"Expected country 'GB', got {address['country']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
