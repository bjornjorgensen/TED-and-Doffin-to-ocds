from pathlib import Path
import pytest
import json
import sys
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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


def test_bt_5071_procedure_integration(tmp_path, temp_output_dir):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:CountrySubentityCode listName="nuts-lvl3">UKG23</cbc:CountrySubentityCode>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """

    xml_file = (
        tmp_path / "test_input_place_performance_country_subdivision_procedure.xml"
    )
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 1
    assert result["tender"]["deliveryAddresses"][0]["region"] == "UKG23"


def test_bt_5071_procedure_multiple_locations(tmp_path, temp_output_dir):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:CountrySubentityCode listName="nuts-lvl3">UKG23</cbc:CountrySubentityCode>
                </cac:Address>
            </cac:RealizedLocation>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:CountrySubentityCode listName="nuts-lvl3">UKG24</cbc:CountrySubentityCode>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """

    xml_file = (
        tmp_path
        / "test_input_place_performance_country_subdivision_procedure_multiple.xml"
    )
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 2
    assert result["tender"]["deliveryAddresses"][0]["region"] == "UKG23"
    assert result["tender"]["deliveryAddresses"][1]["region"] == "UKG24"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
