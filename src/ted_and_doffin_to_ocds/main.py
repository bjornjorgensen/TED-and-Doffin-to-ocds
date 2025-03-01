import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Final

from tqdm import tqdm

from ted_and_doffin_to_ocds.processors.bt_processors import process_bt_sections
from ted_and_doffin_to_ocds.utils.common_operations import (
    NoticeProcessor,
    remove_empty_dicts,
    remove_empty_elements,
)
from ted_and_doffin_to_ocds.utils.config import Config
from ted_and_doffin_to_ocds.utils.file_processor import NoticeFileProcessor


class NoticeConverter:
    """Handles XML notice conversion to OCDS JSON."""

    MAX_WORKERS: Final[int] = 4
    CHUNK_SIZE: Final[int] = 10  # Reduced chunk size for better progress updates

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processor = NoticeProcessor(
            ocid_prefix=config.ocid_prefix,
            scheme=config.scheme,
            db_path=str(config.db_path),
        )
        # Initialize database
        self.processor.tracker.init_db()
        self.processor.tracker.verify_schema()  # Changed to public method

    def _validate_input_file(self, input_path: Path) -> None:
        """Validate input file exists and has correct extension."""
        if not input_path.exists():
            msg = f"Input file not found: {input_path}"
            raise FileNotFoundError(msg)
        if input_path.suffix.lower() != ".xml":
            msg = f"Expected XML file, got: {input_path}"
            raise ValueError(msg)

    def process_file(self, input_path: Path, output_folder: Path) -> None:
        """Process a single XML file."""
        try:
            self.logger.info("Processing file: %s", input_path)
            self._validate_input_file(input_path)

            # First try to read the file
            try:
                xml_content = self._read_xml(input_path)
            except Exception:
                self.logger.exception("Failed to read XML file %s", input_path)
                raise

            # Then try to process it
            releases = self._process_input_file(xml_content)
            if not releases:
                self.logger.warning("No releases generated for file: %s", input_path)
                return

            # Finally try to write the output
            self._write_releases(input_path, output_folder, releases)
            self.logger.info("Successfully processed file: %s", input_path)

        except Exception as e:
            self._handle_process_error(input_path, e)
            self.logger.exception("Error processing file %s", input_path)
            raise

    def process_files_parallel(self, files: list[Path]) -> None:
        """Process files in parallel with improved error handling and progress tracking."""
        self.logger.info("Starting parallel processing of %d files", len(files))

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            # Submit all files individually
            futures = {
                executor.submit(self.process_file, f, self.config.output_folder): f
                for f in files
            }

            # Track progress and handle errors
            failed_files = []
            with tqdm(total=len(files), desc="Processing files", unit="file") as pbar:
                for future in as_completed(futures):
                    try:
                        future.result()
                        pbar.update(1)
                    except Exception as e:
                        file_path = futures[future]
                        failed_files.append((file_path, str(e)))
                        self.logger.exception("Failed to process file: %s", file_path)
                        pbar.set_postfix({"failed": len(failed_files)}, refresh=True)
                        pbar.update(1)

            if failed_files:
                self.logger.error("Failed to process %d files:", len(failed_files))
                for file_path, error in failed_files:
                    self.logger.error("  %s: %s", file_path.name, error)
                error_msg = f"Failed to process {len(failed_files)} files. Check the log for details."
                raise RuntimeError(error_msg)

    def _handle_process_error(self, file_path: Path, error: Exception) -> None:
        """Handle processing errors for specific files."""
        error_file = self.config.output_folder / f"{file_path.stem}_error.log"
        with error_file.open("w") as f:
            f.write(f"Error processing {file_path}:\n{error!s}")
        self.logger.error("Failed to process %s: %s", file_path, error)

    def _process_input_file(self, xml_content: bytes) -> list[dict[str, Any]]:
        """Process input file and return list of releases."""
        releases = []

        try:
            for release_json_str in self.processor.process_notice(xml_content):
                try:
                    release_json = json.loads(release_json_str)
                    process_bt_sections(release_json, xml_content)
                    releases.append(self._clean_release(release_json))
                except json.JSONDecodeError:
                    self.logger.exception("Invalid JSON in release")
                    raise
                except Exception:
                    self.logger.exception("Error processing release")
                    raise

            self.logger.debug("Generated %d releases", len(releases))
        except Exception:
            self.logger.exception("Failed to process notice")
            raise
        else:
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
            json.dump(data, f, ensure_ascii=False)
        self.logger.debug("Successfully wrote release to file")


# json.dump(data, f, ensure_ascii=False, indent=2)


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

    # Add only file handler
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
    logger = logging.getLogger(__name__)

    try:
        config = parse_arguments(
            input_path, output_folder, ocid_prefix, scheme, db_path
        )
        configure_logging(config.log_level)

        logger.info("Starting conversion with config: %s", vars(config))

        converter = NoticeConverter(config)
        process_files(converter, config)

        logger.info("Conversion completed successfully")
    except Exception:
        logger.exception("Fatal error during conversion")
        raise


def process_files(converter: NoticeConverter, config: Config) -> None:
    """Process all input files."""
    logger = logging.getLogger(__name__)

    try:
        config.output_folder.mkdir(parents=True, exist_ok=True)

        # Verify database connection and schema
        try:
            converter.processor.tracker.verify_schema()  # Changed to public method
            logger.info("Database schema verified successfully")
        except Exception:
            logger.exception("Database initialization failed")
            raise

        input_path = config.input_path
        logger.info("Processing input: %s", input_path)

        if input_path.is_file():
            # Process single file directly
            converter.process_file(input_path, config.output_folder)
            return

        # Process multiple files
        with NoticeFileProcessor(input_path, config.output_folder) as processor:
            processor.copy_input_files()
            files = processor.get_sorted_files()

            if not files:
                logger.warning("No XML files found to process")
                return

            converter.process_files_parallel(files)

    except Exception:
        logger.exception("Failed to process files")
        raise


if __name__ == "__main__":
    main()
