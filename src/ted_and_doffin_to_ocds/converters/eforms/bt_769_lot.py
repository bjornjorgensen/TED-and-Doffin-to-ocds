# converters/bt_769_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_multiple_tenders(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract the multiple tenders information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed multiple tenders data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "submissionTerms": {
                                  "multipleBidsAllowed": true/false
                              }
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
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict] = {"tender": {"lots": []}}

    lots: list = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        multiple_tenders_code: list = lot.xpath(
            "cac:TenderingTerms/cbc:MultipleTendersCode[@listName='permission']/text()",
            namespaces=namespaces,
        )

        if multiple_tenders_code:
            result["tender"]["lots"].append(
                {
                    "id": lot_id,
                    "submissionTerms": {
                        "multipleBidsAllowed": multiple_tenders_code[0].lower()
                        == "allowed",
                    },
                },
            )

    return result if result["tender"]["lots"] else None


def merge_multiple_tenders(
    release_json: dict,
    multiple_tenders_data: dict | None,
) -> None:
    """Merge the parsed multiple tenders data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        multiple_tenders_data (Optional[Dict]): The parsed multiple tenders data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not multiple_tenders_data:
        logger.warning("No multiple tenders data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])

    for new_lot in multiple_tenders_data["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged multiple tenders data for %d lots",
        len(multiple_tenders_data["tender"]["lots"]),
    )
