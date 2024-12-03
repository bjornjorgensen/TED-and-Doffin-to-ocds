import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_performing_staff_qualification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse performing staff qualification requirements from XML for each lot.

    Extract information about whether the names and professional qualifications of
    the staff assigned to perform the contract must be given as defined in BT-79.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "otherRequirements": {
                            "requiresStaffNamesAndQualifications": bool
                        }
                    }
                ]
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        curricula_code = lot.xpath(
            "cac:TenderingTerms/cbc:RequiredCurriculaCode/text()",
            namespaces=namespaces,
        )

        if curricula_code:
            code = curricula_code[0]
            if code in ["par-requ", "t-requ"]:
                requires_staff = True
            elif code == "not-requ":
                requires_staff = False
            else:
                continue  # Discard if not one of the specified codes

            lot_data = {
                "id": lot_id,
                "otherRequirements": {
                    "requiresStaffNamesAndQualifications": requires_staff,
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_performing_staff_qualification(
    release_json: dict, staff_qualification_data: dict | None
) -> None:
    """Merge performing staff qualification data into the OCDS release.

    Updates the release JSON in-place by adding or updating other requirements
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        staff_qualification_data: The parsed staff qualification data
            in the same format as returned by parse_performing_staff_qualification().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not staff_qualification_data:
        logger.warning("No Performing Staff Qualification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in staff_qualification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("otherRequirements", {}).update(
                new_lot["otherRequirements"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Performing Staff Qualification data for %d lots",
        len(staff_qualification_data["tender"]["lots"]),
    )
