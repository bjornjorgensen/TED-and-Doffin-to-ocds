# converters/OPP_050_Organization.py

from lxml import etree


def parse_buyers_group_lead_indicator(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"leadBuyerIds": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces,
    )
    for org in organizations:
        lead_indicator = org.xpath(
            "efbc:GroupLeadIndicator/text()", namespaces=namespaces,
        )
        if lead_indicator and lead_indicator[0].lower() == "true":
            org_id = org.xpath(
                "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=namespaces,
            )
            if org_id:
                result["leadBuyerIds"].append(org_id[0])

    return result if result["leadBuyerIds"] else None


def merge_buyers_group_lead_indicator(release_json, buyers_group_lead_data):
    if not buyers_group_lead_data:
        return

    parties = release_json.setdefault("parties", [])

    for party in parties:
        if party["id"] in buyers_group_lead_data["leadBuyerIds"]:
            if "roles" not in party:
                party["roles"] = []
            if "leadBuyer" not in party["roles"]:
                party["roles"].append("leadBuyer")

    # If a lead buyer is not in parties, add it
    for lead_buyer_id in buyers_group_lead_data["leadBuyerIds"]:
        if not any(party["id"] == lead_buyer_id for party in parties):
            parties.append({"id": lead_buyer_id, "roles": ["leadBuyer"]})
