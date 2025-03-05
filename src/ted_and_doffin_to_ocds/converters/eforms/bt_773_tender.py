# converters/bt_773_Tender.py

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

    # Use the exact XPath from the BT-773-Tender specification
    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender"
    tenders: list = root.xpath(xpath, namespaces=namespaces)

    # Only process tenders with subcontracting information
    for tender in tenders:
        # Extract tender ID
        tender_id_elements = tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )

        if not tender_id_elements:
            logger.warning("Found tender without ID, skipping")
            continue

        tender_id: str = tender_id_elements[0]

        # Check for subcontracting term with applicability code
        subcontracting_code: list = tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermCode/text()",
            namespaces=namespaces,
        )

        # Only include tenders that have subcontracting information
        if subcontracting_code:
            # According to eForms guidance:
            # If "yes", set the bid's .hasSubcontracting to true
            # If "no", set it to false
            has_subcontracting = subcontracting_code[0].lower() == "yes"

            result["bids"]["details"].append(
                {
                    "id": tender_id,
                    "hasSubcontracting": has_subcontracting,
                },
            )
        # Do not include tenders without subcontracting information

    # After the results are collected
    if not result["bids"]["details"]:
        return None

    # Return the structure with only bids that have subcontracting information
    # Add explicit marker field so we can identify these bids later
    for bid in result["bids"]["details"]:
        bid["_has_subcontracting_info"] = True

    return result


def merge_subcontracting(release_json: dict, subcontracting_data: dict | None) -> None:
    """Merge the parsed subcontracting data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        subcontracting_data (Optional[Dict]): The parsed subcontracting data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not subcontracting_data or not subcontracting_data.get("bids", {}).get(
        "details"
    ):
        logger.warning("No subcontracting data to merge")
        # Create empty bids structure if needed
        if "bids" not in release_json:
            release_json["bids"] = {"details": []}
        elif "details" not in release_json["bids"]:
            release_json["bids"]["details"] = []
        # Always set to empty array to ensure no bids without subcontracting info
        release_json["bids"]["details"] = []
        return

    # Create a new bid details list with ONLY bids that have subcontracting info
    new_details = []

    for bid in subcontracting_data["bids"]["details"]:
        if bid.get("_has_subcontracting_info"):
            # Remove our marker field
            if "_has_subcontracting_info" in bid:
                del bid["_has_subcontracting_info"]
            # Add to new details
            new_details.append(bid)

    # Set the bids structure
    if "bids" not in release_json:
        release_json["bids"] = {"details": new_details}
    else:
        # Always replace the entire details array
        release_json["bids"]["details"] = new_details

    logger.info("Added subcontracting data for %d bids", len(new_details))
