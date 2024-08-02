# converters/BT_537_Part.py

from lxml import etree
from utils.date_utils import EndDate

def parse_part_duration_end_date(xml_content):
    """
    Parse the Duration End Date (BT-537) for Parts from the XML content.

    This function extracts the end date of the contract period from the procurement project lot
    where the ID scheme name is 'Part'.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data, or None if no relevant data is found.

    Example of returned data:
    {
        "tender": {
            "contractPeriod": {
                "endDate": "2019-11-19T23:59:59+01:00"
            }
        }
    }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {}}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:EndDate"
    end_date_elements = root.xpath(xpath_query, namespaces=namespaces)
    
    if end_date_elements:
        try:
            end_date = end_date_elements[0].text
            iso_end_date = EndDate(end_date)
            result["tender"]["contractPeriod"] = {
                "endDate": iso_end_date
            }
        except ValueError as e:
            print(f"Warning: Invalid date format for part end date: {str(e)}")

    return result if "contractPeriod" in result["tender"] else None

def merge_part_duration_end_date(release_json, part_duration_end_date_data):
    """
    Merge the parsed Part Duration End Date data into the release JSON.

    Args:
        release_json (dict): The current release JSON data.
        part_duration_end_date_data (dict): The parsed Part Duration End Date data to be merged.

    Returns:
        None. The function modifies the release_json in place.
    """
    if not part_duration_end_date_data:
        return

    release_json.setdefault("tender", {}).setdefault("contractPeriod", {}).update(
        part_duration_end_date_data["tender"]["contractPeriod"]
    )