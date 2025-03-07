# converters/eforms/bt_773_tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract the subcontracting information for each tender.

    Handles Business Term BT-773-Tender: Whether at least a part of the contract will be subcontracted.

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

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender"
    tenders: list = root.xpath(xpath, namespaces=namespaces)

    for tender in tenders:
        tender_id_elements = tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )

        if not tender_id_elements:
            logger.warning("Found tender without ID, skipping")
            continue

        tender_id: str = tender_id_elements[0]

        subcontracting_code: list = tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermCode/text()",
            namespaces=namespaces,
        )

        if subcontracting_code:
            has_subcontracting = subcontracting_code[0].lower() == "yes"

            result["bids"]["details"].append(
                {
                    "id": tender_id,
                    "hasSubcontracting": has_subcontracting,
                },
            )
    return result


def merge_subcontracting(release_json: dict, subcontracting_data: dict | None) -> None:
    """Merge the parsed subcontracting data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        subcontracting_data (Optional[Dict]): The parsed subcontracting data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if "bids" not in release_json:
        release_json["bids"] = {"details": []}
    elif "details" not in release_json["bids"]:
        release_json["bids"]["details"] = []

    # Keep track of updates made
    updated_bids = 0

    if subcontracting_data and subcontracting_data.get("bids", {}).get("details"):
        # Create a dictionary of existing bids by ID for quick lookup
        existing_bids = (
            {bid["id"]: bid for bid in release_json["bids"]["details"]}
            if release_json["bids"]["details"]
            else {}
        )

        for subcontracting_bid in subcontracting_data["bids"]["details"]:
            bid_id = subcontracting_bid["id"]

            if bid_id in existing_bids:
                # Update existing bid with subcontracting information
                existing_bids[bid_id]["hasSubcontracting"] = subcontracting_bid[
                    "hasSubcontracting"
                ]
            else:
                # Add new bid with subcontracting information
                release_json["bids"]["details"].append(subcontracting_bid)

            updated_bids += 1

        logger.info(
            "Added/updated subcontracting data for %d bids",
            updated_bids,
        )
    else:
        logger.warning("No subcontracting data to merge")
