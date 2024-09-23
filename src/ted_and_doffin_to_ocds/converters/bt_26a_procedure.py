# bt_26a_procedure.py

from lxml import etree


def parse_classification_type_procedure(xml_content):
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

    classifications = root.xpath(
        "//cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if classifications:
        item = {"id": "1", "additionalClassifications": []}

        for classification in classifications:
            scheme = classification.get("listName", "").upper()
            if scheme:
                item["additionalClassifications"].append({"scheme": scheme})

        if item["additionalClassifications"]:
            result["tender"]["items"].append(item)

    return result


def merge_classification_type_procedure(release_json, classification_type_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next(
            (item for item in existing_items if item["id"] == new_item["id"]),
            None,
        )

        if existing_item:
            existing_classifications = existing_item.setdefault(
                "additionalClassifications",
                [],
            )
            for new_classification in new_item["additionalClassifications"]:
                if new_classification not in existing_classifications:
                    existing_classifications.append(new_classification)
        else:
            existing_items.append(new_item)
