# BT_263_part.py

from lxml import etree


def parse_additional_classification_code_part(xml_content):
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

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    for part in parts:
        classifications = part.xpath(
            "cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
            namespaces=namespaces,
        )

        if classifications:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [],
            }

            for classification in classifications:
                code = classification.text
                scheme = classification.get("listName", "").upper()
                item["additionalClassifications"].append({"id": code, "scheme": scheme})

            result["tender"]["items"].append(item)

    return result


def merge_additional_classification_code_part(release_json, classification_code_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in classification_code_data["tender"]["items"]:
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
                existing_classification = next(
                    (
                        ec
                        for ec in existing_classifications
                        if ec.get("scheme") == new_classification["scheme"]
                    ),
                    None,
                )
                if existing_classification:
                    existing_classification.update(new_classification)
                else:
                    existing_classifications.append(new_classification)
        else:
            existing_items.append(new_item)
