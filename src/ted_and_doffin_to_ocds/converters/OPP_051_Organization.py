# converters/OPP_051_Organization.py

from lxml import etree


def parse_awarding_cpb_buyer_indicator(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    result = {"procuringEntityIds": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces,
    )
    for org in organizations:
        awarding_indicator = org.xpath(
            "efbc:AwardingCPBIndicator/text()", namespaces=namespaces,
        )
        if awarding_indicator and awarding_indicator[0].lower() == "true":
            org_id = org.xpath(
                "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=namespaces,
            )
            if org_id:
                result["procuringEntityIds"].append(org_id[0])

    return result if result["procuringEntityIds"] else None


def merge_awarding_cpb_buyer_indicator(release_json, awarding_cpb_buyer_data):
    if not awarding_cpb_buyer_data:
        return

    parties = release_json.setdefault("parties", [])

    for party in parties:
        if party["id"] in awarding_cpb_buyer_data["procuringEntityIds"]:
            if "roles" not in party:
                party["roles"] = []
            if "procuringEntity" not in party["roles"]:
                party["roles"].append("procuringEntity")

    # If a procuring entity is not in parties, add it
    for procuring_entity_id in awarding_cpb_buyer_data["procuringEntityIds"]:
        if not any(party["id"] == procuring_entity_id for party in parties):
            parties.append({"id": procuring_entity_id, "roles": ["procuringEntity"]})
