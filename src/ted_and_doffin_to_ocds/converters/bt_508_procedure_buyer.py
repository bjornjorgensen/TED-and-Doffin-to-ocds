# converters/bt_508_procedure_buyer.py

from lxml import etree


def parse_buyer_profile_url(xml_content):
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

    result = {"parties": []}

    contracting_parties = root.xpath("//cac:Contractingparty", namespaces=namespaces)

    for party in contracting_parties:
        buyer_profile_uri = party.xpath(
            "cbc:buyerProfileURI/text()",
            namespaces=namespaces,
        )
        org_id = party.xpath(
            "cac:party/cac:partyIdentification/cbc:ID/text()",
            namespaces=namespaces,
        )

        if buyer_profile_uri and org_id:
            result["parties"].append(
                {
                    "id": org_id[0],
                    "details": {"buyerProfile": buyer_profile_uri[0]},
                    "roles": ["buyer"],
                },
            )

    return result if result["parties"] else None


def merge_buyer_profile_url(release_json, buyer_profile_data):
    if not buyer_profile_data:
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in buyer_profile_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {})["buyerProfile"] = new_party[
                "details"
            ]["buyerProfile"]
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            existing_parties.append(new_party)
