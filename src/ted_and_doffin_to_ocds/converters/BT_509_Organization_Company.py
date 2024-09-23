# converters/BT_509_Organization_Company.py

from lxml import etree


def parse_organization_edelivery_gateway(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organization", namespaces=namespaces)

    for org in organizations:
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        endpoint_id = org.xpath(
            "efac:Company/cbc:EndpointID/text()", namespaces=namespaces,
        )

        if org_id and endpoint_id:
            result["parties"].append(
                {"id": org_id[0], "eDeliveryGateway": endpoint_id[0]},
            )

    return result if result["parties"] else None


def merge_organization_edelivery_gateway(release_json, edelivery_gateway_data):
    if not edelivery_gateway_data:
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in edelivery_gateway_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["eDeliveryGateway"] = new_party["eDeliveryGateway"]
        else:
            existing_parties.append(new_party)
