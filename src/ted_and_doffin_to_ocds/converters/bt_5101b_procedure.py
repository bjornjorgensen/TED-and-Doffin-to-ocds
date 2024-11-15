# converters/bt_5101b_procedure.py

from lxml import etree


def parse_procedure_place_performance_streetline1(xml_content):
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
        address = location.xpath("cac:Address", namespaces=namespaces)[0]
        street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
        additional_street_name = address.xpath(
            "cbc:AdditionalStreetName/text()",
            namespaces=namespaces,
        )
        address_lines = address.xpath(
            "cac:AddressLine/cbc:Line/text()",
            namespaces=namespaces,
        )

        street_address_parts = []
        if street_name:
            street_address_parts.append(street_name[0])
        if additional_street_name:
            street_address_parts.append(additional_street_name[0])
        street_address_parts.extend(address_lines)

        street_address = ", ".join(street_address_parts)

        result["tender"]["deliveryAddresses"].append({"streetAddress": street_address})

    return result if result["tender"]["deliveryAddresses"] else None


def merge_procedure_place_performance_streetline1(
    release_json,
    procedure_place_performance_streetline1_data,
):
    if not procedure_place_performance_streetline1_data:
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in procedure_place_performance_streetline1_data["tender"][
        "deliveryAddresses"
    ]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)
