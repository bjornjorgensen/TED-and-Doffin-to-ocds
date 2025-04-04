import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_atypical_url(xml_content: str | bytes) -> dict | None:
    """Parse atypical tool URL information from TED XML for each lot.

    Extract information about URLs for tools and devices that are not generally
    available as defined in BT-124. Maps to `tender.lots[*].communication.atypicalToolUrl`.

    Args:
        xml_content: The TED XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "communication": {
                            "atypicalToolUrl": str
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
        "ted": "http://publications.europa.eu/resource/schema/ted/R2.0.9/publication",
        "n2016": "http://publications.europa.eu/resource/schema/ted/2016/nuts",
        "xs": "http://www.w3.org/2001/XMLSchema",
    }

    result = {"tender": {"lots": []}}

    # TED XML paths for different form types
    form_paths = [
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F01_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F02_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F04_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F05_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F07_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F08_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F12_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F21_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F22_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
        "//ted:TED_EXPORT/ted:FORM_SECTION/ted:F24_2014/ted:CONTRACTING_BODY/ted:URL_TOOL",
    ]

    url_tool = None
    for path in form_paths:
        url_elements = root.xpath(path, namespaces=namespaces)
        if url_elements:
            url_tool = url_elements[0].text
            break

    if not url_tool:
        return None

    # Find lot information
    lots_nodes = root.xpath("//ted:OBJECT_DESCR", namespaces=namespaces)

    # If no lots are explicitly defined, create a single default lot
    if not lots_nodes:
        lot_data = {"id": "1", "communication": {"atypicalToolUrl": url_tool}}
        result["tender"]["lots"].append(lot_data)
    else:
        # Process each lot
        for i, lot_node in enumerate(lots_nodes):
            lot_id = lot_node.xpath("./ted:LOT_NO/text()", namespaces=namespaces)
            lot_id = lot_id[0] if lot_id else str(i + 1)

            lot_data = {"id": lot_id, "communication": {"atypicalToolUrl": url_tool}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_tool_atypical_url(release_json: dict, atypical_url_data: dict | None) -> None:
    """Merge atypical tool URL data into the OCDS release.

    Updates the release JSON in-place by adding or updating communication information
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        atypical_url_data: The parsed atypical tool URL data
            in the same format as returned by parse_tool_atypical_url().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not atypical_url_data:
        logger.info("No atypical tool URL lot data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in atypical_url_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            communication = existing_lot.setdefault("communication", {})
            communication["atypicalToolUrl"] = new_lot["communication"][
                "atypicalToolUrl"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged atypical tool URL data for %d lots",
        len(atypical_url_data["tender"]["lots"]),
    )
