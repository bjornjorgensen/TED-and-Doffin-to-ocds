import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt193_unpublished_identifier(
    xml_content: str | bytes,
) -> dict | None:
    """Parse XML content to extract unpublished identifier for winning tender variant.

    Processes XML content to find winning tender variant fields that are marked as
    unpublished, creating a structured dictionary of withheld information.

    Args:
        xml_content: XML content as either a string or bytes object.

    Returns:
        Optional[Dict]: Dictionary containing withheld information with structure:
            {
                "withheldInformation": [
                    {
                        "id": "field_identifier-tender_id",
                        "field": "win-ten-var",
                        "name": "Winning Tender Variant"
                    },
                    ...
                ]
            }
        Returns None if no withheld information is found.

    Example:
        >>> xml = '<efac:NoticeResult>...</efac:NoticeResult>'
        >>> result = parse_bt195_bt193_unpublished_identifier(xml)
        >>> print(result)
        {'withheldInformation': [{'id': 'win-ten-var-TEN-0001', 'field': 'win-ten-var',
          'name': 'Winning Tender Variant'}]}
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

    result = {"withheldInformation": []}

    lot_tenders = root.xpath(
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        lot_tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)
        field_identifier = lot_tender.xpath(
            "efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-ten-var']/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_tender_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_tender_id[0]}",
                "field": "win-ten-var",
                "name": "Winning Tender Variant",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt193_unpublished_identifier(
    release_json: dict, unpublished_identifier_data: dict | None
) -> None:
    """Merge unpublished identifier data into the main OCDS release JSON.

    Takes the parsed unpublished identifier data and merges it into the main OCDS
    release JSON structure under the withheldInformation array.

    Args:
        release_json: The main OCDS release JSON dictionary to be updated.
            Will be modified in-place.
        unpublished_identifier_data: Dictionary containing the parsed unpublished
            identifier data to be merged. Should contain a 'withheldInformation' key
            with an array value.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {}
        >>> data = {'withheldInformation': [{'id': 'win-ten-var-TEN-0001'}]}
        >>> merge_bt195_bt193_unpublished_identifier(release, data)
        >>> print(release)
        {'withheldInformation': [{'id': 'win-ten-var-TEN-0001'}]}
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-193)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-193): %d items",
        len(unpublished_identifier_data["withheldInformation"]),
    )
