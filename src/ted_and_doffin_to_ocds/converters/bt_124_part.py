import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_atypical_url_part(xml_content: str | bytes) -> dict | None:
    """Parse atypical tool URL information from XML for the part.

    Extract information about URLs for tools and devices that are not generally
    available as defined in BT-124.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "communication": {
                    "atypicalToolUrl": str
                }
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    urls = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cbc:AccessToolsURI/text()",
        namespaces=namespaces,
    )

    if urls:
        return {"tender": {"communication": {"atypicalToolUrl": urls[0]}}}

    return None


def merge_tool_atypical_url_part(
    release_json: dict, atypical_url_data: dict | None
) -> None:
    """Merge atypical tool URL part data into the OCDS release.

    Updates the release JSON in-place by adding or updating communication information
    in the tender.

    Args:
        release_json: The main OCDS release JSON to be updated.
        atypical_url_data: The parsed atypical tool URL data
            in the same format as returned by parse_tool_atypical_url_part().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not atypical_url_data:
        logger.info("No atypical tool URL part data to merge")
        return

    tender = release_json.setdefault("tender", {})

    if "communication" in atypical_url_data["tender"]:
        communication = tender.setdefault("communication", {})
        communication["atypicalToolUrl"] = atypical_url_data["tender"]["communication"][
            "atypicalToolUrl"
        ]
        logger.info("Merged atypical tool URL part data")
