# converters/BT_5101a_Lot.py

from lxml import etree


def parse_lot_place_performance_street(xml_content):
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

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces
        )

        if realized_locations:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": [],
            }

            for location in realized_locations:
                address = location.xpath("cac:Address", namespaces=namespaces)[0]
                street_name = address.xpath(
                    "cbc:StreetName/text()", namespaces=namespaces
                )
                additional_street_name = address.xpath(
                    "cbc:AdditionalStreetName/text()", namespaces=namespaces
                )
                address_lines = address.xpath(
                    "cac:AddressLine/cbc:Line/text()", namespaces=namespaces
                )

                street_address_parts = []
                if street_name:
                    street_address_parts.append(street_name[0])
                if additional_street_name:
                    street_address_parts.append(additional_street_name[0])
                street_address_parts.extend(address_lines)

                street_address = ", ".join(street_address_parts)

                item["deliveryAddresses"].append({"streetAddress": street_address})

            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_lot_place_performance_street(release_json, lot_place_performance_street_data):
    if not lot_place_performance_street_data:
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in lot_place_performance_street_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_item["deliveryAddresses"] = new_item["deliveryAddresses"]
        else:
            existing_items.append(new_item)
