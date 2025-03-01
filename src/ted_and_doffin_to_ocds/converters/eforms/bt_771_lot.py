# converters/bt_771_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

CODE_TO_LABEL = {
    "late-all": "At the discretion of the buyer, all missing tenderer-related documents may be submitted later.",
    "late-none": "No documents can be submitted later.",
    "late-some": "At the discretion of the buyer, some missing tenderer-related documents may be submitted later.",
}


def parse_late_tenderer_info(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract the late tenderer information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed late tenderer information in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "submissionMethodDetails": "late tenderer information"
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
        late_info_code: list = lot.xpath(
            "cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:CompanyLegalFormCode)]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='reserved-procurement'])]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='selection-criteria-source'])]"
            "/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='missing-info-submission']"
            "/cbc:TendererRequirementTypeCode/text()",
            namespaces=namespaces,
        )

        if late_info_code:
            late_info_label = CODE_TO_LABEL.get(late_info_code[0], "")
            if late_info_label:
                result["tender"]["lots"].append(
                    {"id": lot_id, "submissionMethodDetails": late_info_label},
                )

    return result if result["tender"]["lots"] else None


def merge_late_tenderer_info(
    release_json: dict,
    late_tenderer_info: dict | None,
) -> None:
    """Merge the parsed late tenderer information into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        late_tenderer_info (Optional[Dict]): The parsed late tenderer information to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not late_tenderer_info:
        logger.warning("No late tenderer information to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])

    for new_lot in late_tenderer_info["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            if "submissionMethodDetails" in existing_lot:
                existing_lot["submissionMethodDetails"] += (
                    f" {new_lot['submissionMethodDetails']}"
                )
            else:
                existing_lot["submissionMethodDetails"] = new_lot[
                    "submissionMethodDetails"
                ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged late tenderer information for %d lots",
        len(late_tenderer_info["tender"]["lots"]),
    )
