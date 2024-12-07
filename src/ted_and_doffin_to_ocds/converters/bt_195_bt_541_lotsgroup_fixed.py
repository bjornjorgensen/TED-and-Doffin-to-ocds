import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier(
    xml_content: str | bytes,
) -> dict | None:
    """Parse XML content to extract unpublished identifier for award criterion number fixed.

    Processes XML content to find award criterion number fixed fields that are marked as
    unpublished within LotsGroup, creating a structured dictionary of withheld information.

    Args:
        xml_content: XML content as either a string or bytes object.

    Returns:
        Optional[Dict]: Dictionary containing withheld information with structure:
            {
                "withheldInformation": [
                    {
                        "id": "field_identifier-fixed-lots_group_id",
                        "field": "awa-cri-num",
                        "name": "Award Criterion Number Fixed"
                    },
                    ...
                ]
            }
        Returns None if no withheld information is found.

    Example:
        >>> xml = '<cac:ProcurementProjectLot>...</cac:ProcurementProjectLot>'
        >>> result = parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier(xml)
        >>> print(result)
        {'withheldInformation': [{'id': 'awa-cri-num-fixed-GLO-0001', 'field': 'awa-cri-num',
          'name': 'Award Criterion Number Fixed'}]}
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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']"
    fields_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)

    for fields_privacy in fields_privacy_elements:
        lots_group_id = fields_privacy.xpath(
            "ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='LotsGroup']/text()",
            namespaces=namespaces,
        )
        field_identifier = fields_privacy.xpath(
            "efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lots_group_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-fixed-{lots_group_id[0]}",
                "field": "awa-cri-num",
                "name": "Award Criterion Number Fixed",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier(
    release_json: dict,
    unpublished_identifier_data: dict | None,
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
        >>> data = {'withheldInformation': [{'id': 'awa-cri-num-fixed-GLO-0001'}]}
        >>> merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier(release, data)
        >>> print(release)
        {'withheldInformation': [{'id': 'awa-cri-num-fixed-GLO-0001'}]}
    """
    if not unpublished_identifier_data:
        logger.warning(
            "No unpublished identifier data to merge for BT-195(BT-541) LotsGroup Fixed",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-541) LotsGroup Fixed for %d lots groups",
        len(unpublished_identifier_data["withheldInformation"]),
    )
