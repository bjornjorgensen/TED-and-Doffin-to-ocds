import json
import logging
from pathlib import Path
import argparse
from typing import Any

from ted_and_doffin_to_ocds.utils.common_operations import (
    NoticeProcessor,
    remove_empty_elements,
    remove_empty_dicts,
)
from ted_and_doffin_to_ocds.utils.file_processor import NoticeFileProcessor
from ted_and_doffin_to_ocds.processors.bt_processors import process_bt_sections
from ted_and_doffin_to_ocds.utils.config import Config


class NoticeConverter:
    """Handles XML notice conversion to OCDS JSON."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processor = NoticeProcessor(
            ocid_prefix=config.ocid_prefix,
            scheme=config.scheme,
            db_path=str(config.db_path),
        )

    def process_file(self, input_path: Path, output_folder: Path) -> None:
        """Process a single XML file."""
        self.logger.info("Processing file: %s", input_path)

        try:
            releases = self._process_input_file(input_path)
            self._write_releases(input_path, output_folder, releases)
        except Exception:
            self.logger.exception("Error processing file %s", input_path)
            raise

    def _process_input_file(self, input_path: Path) -> list[dict[str, Any]]:
        """Process input file and return list of releases."""
        xml_content = self._read_xml(input_path)
        releases = []

        for release_json_str in self.processor.process_notice(xml_content):
            release_json = json.loads(release_json_str)
            process_bt_sections(release_json, xml_content)
            releases.append(self._clean_release(release_json))

        return releases

    def _clean_release(self, release: dict[str, Any]) -> dict[str, Any]:
        """Clean up release data."""
        release = remove_empty_elements(release)
        return remove_empty_dicts(release)

    def _write_releases(
        self, input_path: Path, output_folder: Path, releases: list[dict[str, Any]]
    ) -> None:
        """Write releases to output files."""
        for i, release in enumerate(releases):
            output_file = output_folder / f"{input_path.stem}_release_{i}.json"
            self._write_json(output_file, release)

    def _read_xml(self, input_path: Path) -> bytes:
        """Read XML content from file."""
        with input_path.open("rb") as xml_file:
            content = xml_file.read()
            self.logger.debug(
                "Read XML file: %s, size: %d bytes", input_path, len(content)
            )
            return content

    def _write_json(self, output_file: Path, data: dict[str, Any]) -> None:
        """Write JSON data to file."""
        self.logger.debug("Writing to output file: %s", output_file)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.debug("Successfully wrote release to file")


def configure_logging(level: str = "INFO") -> None:
    """Configure logging system."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add file handler
    log_file = Path("app.log")
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments(
    input_path: str | None = None,
    output_folder: str | None = None,
    ocid_prefix: str | None = None,
    scheme: str | None = None,
    db_path: str | None = None,
) -> Config:
    """Parse command line arguments or use provided values."""
    if all(arg is not None for arg in [input_path, output_folder, ocid_prefix]):
        return Config(
            input_path=Path(input_path),
            output_folder=Path(output_folder),
            ocid_prefix=ocid_prefix,
            scheme=scheme or "eu-oj",
            db_path=Path(db_path or "notices.db"),
            clear_db=False,
            log_level="INFO",
        )

    parser = argparse.ArgumentParser(description="Convert XML eForms to OCDS JSON")
    parser.add_argument("input", help="Input XML file or folder")
    parser.add_argument("output", help="Output folder for JSON files")
    parser.add_argument("ocid_prefix", help="Prefix for OCID")
    parser.add_argument(
        "--scheme",
        default="eu-oj",
        help="Scheme for related processes (default: eu-oj)",
    )
    parser.add_argument(
        "--db",
        help="Path to SQLite database file (default: notices.db)",
        default="notices.db",
    )
    parser.add_argument(
        "--clear-db",
        action="store_true",
        help="Clear existing database before processing",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    args = parser.parse_args()

    return Config(
        input_path=Path(args.input),
        output_folder=Path(args.output),
        ocid_prefix=args.ocid_prefix,
        scheme=args.scheme,
        db_path=Path(args.db),
        clear_db=args.clear_db,
        log_level=args.log_level,
    )


def main(
    input_path: str | None = None,
    output_folder: str | None = None,
    ocid_prefix: str | None = None,
    scheme: str | None = None,
    db_path: str | None = None,
) -> None:
    """Main entry point for notice conversion."""
    config = parse_arguments(input_path, output_folder, ocid_prefix, scheme, db_path)
    configure_logging(config.log_level)

    try:
        converter = NoticeConverter(config)
        process_files(converter, config)
    except Exception:
        logging.getLogger(__name__).exception("Fatal error")
        raise


def process_files(converter: NoticeConverter, config: Config) -> None:
    """Process all input files."""
    config.output_folder.mkdir(parents=True, exist_ok=True)

    with NoticeFileProcessor(config.input_path, config.output_folder) as processor:
        processor.copy_input_files()
        files = processor.get_sorted_files()

        if not files:
            logging.warning("No XML files found to process")
            return

        for xml_file in files:
            converter.process_file(xml_file, config.output_folder)


if __name__ == "__main__":
    main()
