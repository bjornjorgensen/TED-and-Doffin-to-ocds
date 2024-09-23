# converters/BT_5071_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_place_performance_country_subdivision(xml_content):
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

    result = {"tender": {"deliveryAddresses": []}}

    realized_locations = root.xpath(
        "//cac:ProcurementProject/cac:RealizedLocation",
        namespaces=namespaces,
    )

    for location in realized_locations:
        country_subdivision = location.xpath(
            "cac:Address/cbc:CountrySubentityCode/text()",
            namespaces=namespaces,
        )

        if country_subdivision:
            address = {"region": country_subdivision[0]}
            result["tender"]["deliveryAddresses"].append(address)

    return result if result["tender"]["deliveryAddresses"] else None


def merge_procedure_place_performance_country_subdivision(release_json, procedure_data):
    if not procedure_data:
        logger.warning(
            "No Procedure Place Performance Country Subdivision data to merge",
        )
        return

    tender_delivery_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in procedure_data["tender"]["deliveryAddresses"]:
        existing_address = next(
            (addr for addr in tender_delivery_addresses if "region" not in addr),
            None,
        )
        if existing_address:
            existing_address["region"] = new_address["region"]
        else:
            tender_delivery_addresses.append(new_address)

    logger.info(
        f"Merged Procedure Place Performance Country Subdivision data for {len(procedure_data['tender']['deliveryAddresses'])} addresses",
    )
