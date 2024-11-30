# src/ted_and_doffin_to_ocds/utils/file_processor.py

import asyncio
import logging
import shutil
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import ClassVar, Final, Self

from lxml import etree
from tqdm import tqdm

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

    MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB limit

    def __init__(self, input_path: Path, output_path: Path) -> None:
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

    async def categorize_files_async(self) -> dict[str, list[Path]]:
        """Async version of categorize_files."""
        if not self.temp_dir:
            raise UninitializedError

        loop = asyncio.get_event_loop()
        categorized = {notice_type: [] for notice_type in self.NOTICE_ORDER}

        file_paths = list(self.temp_dir.glob("*.xml"))
        tasks = [
            loop.run_in_executor(None, self.get_notice_type, file_path)
            for file_path in file_paths
        ]

        results = await asyncio.gather(*tasks)
        for file_path, notice_type in zip(file_paths, results, strict=False):
            if notice_type in categorized:
                categorized[notice_type].append(file_path)

        return categorized

    def copy_input_files(self) -> None:
        """Copy input files to temporary directory with progress tracking."""
        if not self.temp_dir:
            raise UninitializedError

        files = list(self.input_path.glob("*.xml"))
        with tqdm(files, desc="Copying files") as pbar:
            for xml_file in pbar:
                if xml_file.stat().st_size > self.MAX_FILE_SIZE:
                    logger.warning("File %s exceeds size limit", xml_file)
                    continue

                try:
                    shutil.copy2(xml_file, self.temp_dir)
                    pbar.set_postfix({"file": xml_file.name})
                except OSError:
                    logger.exception("Failed to copy %s", xml_file)

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

    async def process_files_async(self) -> AsyncIterator[Path]:
        """Process files asynchronously."""
        if not self.temp_dir:
            raise UninitializedError

        categorized = await self.categorize_files_async()
        for notice_type in self.NOTICE_ORDER:
            for file_path in sorted(categorized[notice_type]):
                yield file_path
