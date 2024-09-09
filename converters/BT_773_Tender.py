# converters/BT_773_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the subcontracting information for each tender.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed subcontracting data in the format:
              {
                  "bids": {
                      "details": [
                          {
                              "id": "tender_id",
                              "hasSubcontracting": true/false
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root: etree._Element = etree.fromstring(xml_content)
    namespaces: dict[str, str] = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result: dict[str, dict] = {"bids": {"details": []}}

    tenders: list = root.xpath("//efac:LotTender", namespaces=namespaces)

    for tender in tenders:
        tender_id: str = tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )[0]
        subcontracting_code: list = tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermCode/text()",
            namespaces=namespaces,
        )

        if subcontracting_code:
            result["bids"]["details"].append(
                {
                    "id": tender_id,
                    "hasSubcontracting": subcontracting_code[0].lower() == "yes",
                }
            )

    return result if result["bids"]["details"] else None


def merge_subcontracting(release_json: dict, subcontracting_data: dict | None) -> None:
    """
    Merge the parsed subcontracting data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        subcontracting_data (Optional[Dict]): The parsed subcontracting data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subcontracting_data:
        logger.warning("No subcontracting data to merge")
        return

    bids: dict = release_json.setdefault("bids", {})
    existing_details: list = bids.setdefault("details", [])

    for new_bid in subcontracting_data["bids"]["details"]:
        existing_bid: dict | None = next(
            (bid for bid in existing_details if bid["id"] == new_bid["id"]), None
        )
        if existing_bid:
            existing_bid["hasSubcontracting"] = new_bid["hasSubcontracting"]
        else:
            existing_details.append(new_bid)

    logger.info(
        f"Merged subcontracting data for {len(subcontracting_data['bids']['details'])} bids"
    )
