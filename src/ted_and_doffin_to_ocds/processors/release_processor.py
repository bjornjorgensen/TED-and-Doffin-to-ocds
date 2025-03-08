"""Release processor for creating OCDS releases from eForm notices.

This module implements the business logic for creating OCDS releases from XML notices,
including special handling for PIN-only notices and related processes.
"""

import logging
import uuid
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


class ReleaseProcessor:
    """Process eForm notices and create OCDS releases."""

    def __init__(self, ocid_prefix: str, scheme: str = "eu-oj") -> None:
        """Initialize the release processor.

        Args:
            ocid_prefix: Prefix to use for new OCIDs
            scheme: Default scheme for related processes
        """
        self.ocid_prefix = ocid_prefix
        self.scheme = scheme
        self.namespaces = {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        }

    def create_releases(
        self, tree: etree._Element, notice_info: dict[str, Any], tracker=None
    ) -> list[dict[str, Any]]:
        """Create releases from an eForm notice.

        For PIN-only notices, creates separate releases for each part.
        For other notices, creates a single release.

        Args:
            tree: XML element tree of the notice
            notice_info: Basic notice information
            tracker: Optional notice tracker for OCID management

        Returns:
            List of OCDS release dictionaries
        """
        if notice_info["is_pin_only"]:
            return self._create_pin_only_releases(tree, notice_info, tracker)
        return [self._create_standard_release(tree, notice_info, tracker)]

    def _create_pin_only_releases(
        self, tree: etree._Element, notice_info: dict[str, Any], tracker=None
    ) -> list[dict[str, Any]]:
        """Create releases for a PIN-only notice, handling parts separately.

        For PIN-only notices, each part is treated as a separate planning process.

        Args:
            tree: XML element tree of the notice
            notice_info: Basic notice information
            tracker: Optional notice tracker for OCID management

        Returns:
            List of OCDS release dictionaries
        """
        parts = self._get_parts(tree)

        # If no parts found, create a single release
        if not parts:
            return [self._create_standard_release(tree, notice_info, tracker)]

        # Process each part as a separate release
        releases = []
        for part in parts:
            # Generate a new OCID for each part
            ocid = f"{self.ocid_prefix}-{uuid.uuid4()}"
            part_id = part.xpath("string(cbc:ID)", namespaces=self.namespaces)

            # Track the part if tracker is available
            if tracker:
                tracker.track_part(notice_info["notice_id"], part_id, ocid)

            release = {
                "id": notice_info["notice_id"],
                "ocid": ocid,
                "initiationType": "tender",
                "tender": {
                    "id": part_id  # Add this line to correctly set the part ID
                }
            }

            # Add related processes for this part
            related_processes = self._get_part_related_processes(part)
            if related_processes:
                release["relatedProcesses"] = related_processes

            releases.append(release)

        return releases

    def _create_standard_release(
        self, tree: etree._Element, notice_info: dict[str, Any], tracker=None
    ) -> dict[str, Any]:
        """Create a standard release for non-PIN-only notices.

        Args:
            tree: XML element tree of the notice
            notice_info: Basic notice information
            tracker: Optional notice tracker for OCID management

        Returns:
            OCDS release dictionary
        """
        # Determine the OCID according to the rules
        ocid = self._determine_ocid(tree, tracker)

        # Create the base release
        release = {
            "id": notice_info["notice_id"],
            "ocid": ocid,
            "initiationType": "tender",
        }

        # Add related processes references
        related_processes = self._get_related_processes(tree)
        if related_processes:
            release["relatedProcesses"] = related_processes

        return release

    def _determine_ocid(self, tree: etree._Element, tracker=None) -> str:
        """Determine OCID based on specified rules.

        New OCID is assigned if:
        - First publication (no previous references)
        - CAN for framework/DPS
        - Previous publication was a PIN-only notice

        Otherwise, use previous OCID.

        Args:
            tree: XML element tree of the notice
            tracker: Optional notice tracker for OCID management

        Returns:
            OCID string
        """
        # Check if this is first publication
        prev_pub_ref = tree.xpath(
            "//cac:NoticeDocumentReference", namespaces=self.namespaces
        )
        if not prev_pub_ref:
            logger.info("First publication - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Check if this is CAN for framework/DPS
        if self._is_can_for_framework_or_dps(tree):
            logger.info("CAN for framework/DPS - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Get previous publication ID
        prev_pub_id = self._get_previous_publication_id(tree)
        if not prev_pub_id:
            logger.info("No previous publication ID found - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Check if previous was PIN-only
        if tracker:
            prev_notice = tracker.get_previous_notice(prev_pub_id)
            if prev_notice:
                if prev_notice[3]:  # is_pin_only flag in position 3
                    logger.info("Previous was PIN-only - generating new OCID")
                    return f"{self.ocid_prefix}-{uuid.uuid4()}"
                if prev_notice[1]:  # OCID in position 1
                    logger.info("Using previous OCID: %s", prev_notice[1])
                    return prev_notice[1]

        # Default case - generate new OCID
        logger.warning(
            "Previous publication referenced but OCID not found - generating new OCID"
        )
        return f"{self.ocid_prefix}-{uuid.uuid4()}"

    def _get_related_processes(
        self, tree: etree._Element
    ) -> list[dict[str, Any]] | None:
        """Get related processes references for a notice.

        Args:
            tree: XML element tree of the notice

        Returns:
            List of related process objects or None if none found
        """
        references = []
        ref_id = 1

        # Find notice document references
        notice_refs = tree.xpath(
            "//cac:TenderingProcess/cac:NoticeDocumentReference",
            namespaces=self.namespaces,
        )

        for ref in notice_refs:
            notice_id = ref.xpath("string(cbc:ID)", namespaces=self.namespaces)
            scheme_name = ref.xpath(
                "string(cbc:ID/@schemeName)", namespaces=self.namespaces
            )

            if notice_id:
                # Prefix scheme with "eu-" if needed
                scheme = scheme_name
                if scheme and not scheme.startswith("eu-"):
                    scheme = f"eu-{scheme}"
                else:
                    scheme = self.scheme

                # Create related process object
                process = {
                    "id": str(ref_id),
                    "relationship": ["planning"],
                    "scheme": scheme,
                    "identifier": notice_id,
                }

                # Check for lot reference
                lot_ref = ref.xpath(
                    "ancestor::cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cbc:ID/text()",
                    namespaces=self.namespaces,
                )
                if lot_ref:
                    process["relatedLots"] = [lot_ref[0]]

                references.append(process)
                ref_id += 1

                # If OCDS reference is available, add it too
                if scheme_name == "ocds":
                    ocid_process = process.copy()
                    ocid_process["id"] = str(ref_id)
                    ocid_process["scheme"] = "ocid"
                    references.append(ocid_process)
                    ref_id += 1

        return references if references else None

    def _get_part_related_processes(
        self, part: etree._Element
    ) -> list[dict[str, Any]] | None:
        """Get related processes for a specific part.

        Args:
            part: XML element tree of a part

        Returns:
            List of related process objects or None if none found
        """
        references = []
        ref_id = 1

        # Find notice document references within this part
        notice_refs = part.xpath(
            ".//cac:NoticeDocumentReference", namespaces=self.namespaces
        )

        for ref in notice_refs:
            notice_id = ref.xpath("string(cbc:ID)", namespaces=self.namespaces)
            internal_ref = ref.xpath(
                "string(cbc:ReferencedDocumentInternalAddress)",
                namespaces=self.namespaces,
            )

            if notice_id:
                # Use compound identifier if internal reference exists
                identifier = (
                    f"{notice_id}-{internal_ref}" if internal_ref else notice_id
                )

                references.append(
                    {
                        "id": str(ref_id),
                        "relationship": ["planning"],
                        "scheme": self.scheme,
                        "identifier": identifier,
                    }
                )
                ref_id += 1

        return references if references else None

    def _get_parts(self, tree: etree._Element) -> list[etree._Element]:
        """Get all parts from a notice.

        Args:
            tree: XML element tree

        Returns:
            List of part elements
        """
        return tree.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
            namespaces=self.namespaces,
        )

    def _is_can_for_framework_or_dps(self, tree: etree._Element) -> bool:
        """Check if notice is a Contract Award Notice for framework agreement or DPS.

        Args:
            tree: XML element tree

        Returns:
            True if CAN for framework/DPS, False otherwise
        """
        # First check if it's a CAN at all
        is_can = etree.QName(tree).localname == "ContractAwardNotice"
        if not is_can:
            return False

        # Check for framework agreement
        is_framework = tree.xpath(
            """boolean(/*/cac:ProcurementProject//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'] |
            /*/cac:ProcurementProjectLot//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'])""",
            namespaces=self.namespaces,
        )

        # Check for DPS
        is_dps = tree.xpath(
            """boolean(
                /*/cac:ProcurementProject//cbc:ProcurementTypeCode[
                    @listName='contract-nature' and text()='dps'] |
                /*/cac:ProcurementProjectLot//cbc:ProcurementTypeCode[
                    @listName='contract-nature' and text()='dps'] |
                /*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/
                    cac:TenderingProcess/cac:ContractingSystem[
                        cbc:ContractingSystemTypeCode/@listName='dps-usage']/
                        cbc:ContractingSystemTypeCode[text()!='none']
            )""",
            namespaces=self.namespaces,
        )

        return is_framework or is_dps

    def _get_previous_publication_id(self, tree: etree._Element) -> str | None:
        """Get ID of the previous planning notice if it exists.

        Args:
            tree: XML element tree

        Returns:
            Previous publication ID or None if not found
        """
        refs = tree.xpath(
            "//cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref']/text()",
            namespaces=self.namespaces,
        )

        if refs:
            logger.debug("Found previous publication ID: %s", refs[0])
            return refs[0]

        return None
