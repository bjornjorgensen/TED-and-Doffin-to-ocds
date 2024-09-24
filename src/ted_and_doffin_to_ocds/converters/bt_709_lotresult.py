# converters/bt_709_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_maximum_value(xml_content):
    """
    Parse the XML content to extract the framework maximum value for each LotResult.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "awards": [
                      {
                          "id": "award_id",
                          "maximumValue": {
                              "amount": float_value,
                              "currency": "currency_code"
                          },
                          "relatedLots": ["lot_id"]
                      }
                  ]
              }
        None: If no relevant data is found.

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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:noticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        max_value = lot_result.xpath(
            "efac:FrameworkAgreementValues/cbc:MaximumValueAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_result.xpath(
            "efac:FrameworkAgreementValues/cbc:MaximumValueAmount/@currencyID",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if award_id and max_value and currency and lot_id:
            award = {
                "id": award_id[0],
                "maximumValue": {
                    "amount": float(max_value[0]),
                    "currency": currency[0],
                },
                "relatedLots": [lot_id[0]],
            }
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_framework_maximum_value(release_json, framework_max_value_data):
    """
    Merge the parsed framework maximum value data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        framework_max_value_data (dict): The parsed framework maximum value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not framework_max_value_data:
        logger.warning("No framework maximum value data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in framework_max_value_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award["maximumValue"] = new_award["maximumValue"]
            existing_award.setdefault("relatedLots", []).extend(
                new_award["relatedLots"],
            )
            existing_award["relatedLots"] = list(
                set(existing_award["relatedLots"]),
            )  # Remove duplicates
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged framework maximum value data for %d awards",
        len(framework_max_value_data["awards"]),
    )
