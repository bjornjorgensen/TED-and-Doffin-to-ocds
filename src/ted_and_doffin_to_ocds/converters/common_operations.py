# converters/Common_operations.py
import json
from lxml import etree


class NoticeProcessor:
    def __init__(self, ocid_prefix):
        self.ocid_prefix = ocid_prefix
        self.item_id_counter = 1

    def create_release(self, xml_content):
        # Ensure xml_content is bytes
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        tree = etree.fromstring(xml_content)

        # Extract notice identifier
        notice_id = tree.xpath(
            "string(/*/cbc:ID)",
            namespaces={
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            },
        )

        # Create an empty JSON object
        release = {}
        release["id"] = notice_id
        release["initiationType"] = "tender"

        return json.dumps(release)
