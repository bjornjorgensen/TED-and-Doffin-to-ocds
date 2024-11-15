# src/ted_and_doffin_to_ocds/utils/file_processor.py

import shutil
import tempfile
from pathlib import Path
from typing import ClassVar, Self
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class UninitializedError(RuntimeError):
    """Raised when temporary directory is not initialized."""


class NoticeFileProcessor:
    """Process XML notice files in correct order."""

    NOTICE_ORDER: ClassVar[list[str]] = [
        "PriorInformationNotice",
        "ContractNotice",
        "ContractAwardNotice",
        "ContractAwardNotice-Modification",
    ]

    def __init__(self, input_path: Path, output_path: Path):
        """Initialize the processor with input and output paths."""
        self.input_path = input_path
        self.output_path = output_path
        self.temp_dir = None

    def __enter__(self) -> Self:
        """Set up the context manager by creating temporary directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        logger.info("Created temporary directory: %s", self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up the context manager by removing temporary directory."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary directory: %s", self.temp_dir)

    def get_notice_type(self, file_path: Path) -> str | None:
        """
        Determine the notice type from an XML file.
        Handles XML declarations, comments, and namespaces.
        """
        try:
            # Parse the XML with lxml to handle namespaces properly
            tree = etree.parse(str(file_path))
            root = tree.getroot()

            # Get the local name (without namespace)
            root_tag = etree.QName(root).localname
            logger.debug("Found root tag: %s for file %s", root_tag, file_path)

            # Check for modification type in case of ContractAwardNotice
            if root_tag == "ContractAwardNotice":
                modification = root.xpath(
                    "//cbc:NoticeTypeCode[@listName='cont-modif']/text()",
                    namespaces=self.namespaces,
                )
                if modification and modification[0] == "can-modif":
                    return "ContractAwardNotice-Modification"

            # Verify it's one of our expected types
            if root_tag in [
                "PriorInformationNotice",
                "ContractNotice",
                "ContractAwardNotice",
            ]:
                return root_tag
            logger.warning("Unexpected root tag %s in file %s", root_tag, file_path)
            return None  # noqa: TRY300

        except Exception:
            logger.exception("Error determining notice type for %s", file_path)
            return None

    @property
    def namespaces(self) -> dict[str, str]:
        """XML namespaces used in eForms."""
        return {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
            # Add default namespaces for each notice type
            "pin": "urn:oasis:names:specification:ubl:schema:xsd:PriorInformationNotice-2",
            "cn": "urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2",
            "can": "urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2",
        }

    def categorize_files(self) -> dict[str, list[Path]]:
        """Categorize files by notice type."""
        temp_dir_error = (
            "Temporary directory not initialized. Use with context manager."
        )
        if not self.temp_dir:
            raise RuntimeError(temp_dir_error)

        categorized = {notice_type: [] for notice_type in self.NOTICE_ORDER}

        for file_path in self.temp_dir.glob("*.xml"):
            notice_type = self.get_notice_type(file_path)
            if notice_type in categorized:
                categorized[notice_type].append(file_path)
                logger.info("Categorized %s as %s", file_path.name, notice_type)
            else:
                logger.warning("Unknown notice type for %s", file_path.name)

        # Log summary
        for notice_type, files in categorized.items():
            if files:
                logger.info("Found %d files of type %s", len(files), notice_type)

        return categorized

    def copy_input_files(self) -> None:
        """Copy input files to temporary directory."""
        temp_dir_error = (
            "Temporary directory not initialized. Use with context manager."
        )
        if not self.temp_dir:
            raise RuntimeError(temp_dir_error)

        if self.input_path.is_file():
            shutil.copy2(self.input_path, self.temp_dir)
            logger.info("Copied %s to temporary directory", self.input_path.name)
        elif self.input_path.is_dir():
            count = 0
            for xml_file in self.input_path.glob("*.xml"):
                shutil.copy2(xml_file, self.temp_dir)
                count += 1
            logger.info("Copied %d XML files to temporary directory", count)
        else:
            error_msg = f"Invalid input path: {self.input_path}"
            raise ValueError(error_msg)

    def get_sorted_files(self) -> list[Path]:
        """Get files sorted in processing order."""
        if not self.temp_dir:
            raise UninitializedError

        categorized = self.categorize_files()
        sorted_files = []

        # Add files in specified order
        for notice_type in self.NOTICE_ORDER:
            files = sorted(categorized[notice_type])
            if files:
                logger.info(
                    "Adding %d files of type %s to processing queue",
                    len(files),
                    notice_type,
                )
                sorted_files.extend(files)

        if not sorted_files:
            logger.warning("No valid XML files found in any category")

        return sorted_files
