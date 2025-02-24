# XML to OCDS Converter for TED and Doffin eForms

This project converts XML eForm data from TED (Tenders Electronic Daily) and Doffin (Database for offentlige innkjøp) to OCDS (Open Contracting Data Standard) JSON format. It focuses on processing organization and address information, following the eForm profile mapping.

## Table of Contents

- [Project Overview](#project-overview)
- [Importance of OCDS](#importance-of-ocds)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Options](#advanced-options)
  - [File Processing Order](#file-processing-order)
  - [Logging](#logging)
- [Testing](#testing)
- [OCDS eForm Profile Mapping](#ocds-eform-profile-mapping)
- [TED and Doffin Data Processing](#ted-and-doffin-data-processing)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The XML to OCDS Converter processes eForms XML data from TED and Doffin and converts it into the OCDS JSON format. It handles various business terms (BT) and ensures proper mapping according to the OCDS eForm profile, accommodating the specificities of both TED and Doffin data structures.

## Importance of OCDS

The Open Contracting Data Standard (OCDS) is crucial for several reasons:

1. **Transparency**: OCDS promotes transparency in public contracting by providing a standardized format for publishing procurement information, making it easier for citizens, journalists, and civil society organizations to access and analyze procurement data.

2. **Interoperability**: By using a common data standard, OCDS enables different systems and databases to exchange information seamlessly, facilitating data sharing between government agencies, across borders, and with third-party applications.

3. **Data Quality**: The structured format of OCDS encourages better data quality and completeness, as it provides a clear schema for what information should be included and how it should be formatted.

4. **Efficiency**: Standardized data allows for more efficient analysis of procurement trends, performance, and value for money, helping governments and other stakeholders to make better-informed decisions.

5. **Competition**: By making procurement information more accessible and comparable, OCDS can help increase competition among suppliers, potentially leading to better value for money in public contracting.

6. **Innovation**: The availability of standardized, machine-readable procurement data enables the development of innovative tools and applications for data analysis, visualization, and monitoring.

7. **Anti-corruption**: Standardized, open contracting data makes it easier to detect and prevent fraud and corruption in public procurement by enabling better oversight and analysis of contracting patterns.

8. **Economic Development**: OCDS can contribute to economic development by providing businesses, especially small and medium enterprises, with better access to procurement opportunities and market intelligence.

By converting TED and Doffin eForm data to OCDS format, this project contributes to these benefits, making European and Norwegian procurement data more accessible, usable, and valuable for a wide range of stakeholders.

## File Structure

```
project_root/
│
├── main.py
├── converters/
│   ├── bt_510c_Organization_Company.py
│   ├── bt_76_Lot.py
│   ├── bt_98_Lot.py
│   └── ...
├── tests/
│   ├── test_bt_767_Lot.py
│   ├── test_bt_76_Lot.py
│   └── ...
├── utils/
│   └── date_utils.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Installation

1. Ensure you have the required system packages:
   ```bash
   sudo apt update
   sudo apt install python3-full pipx
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/bjornjorgensen/TED-and-Doffin-to-ocds.git
   ```

3. Change to the project directory:
   ```bash
   cd TED-and-Doffin-to-ocds
   ```

4. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Install Poetry using pip:
   ```bash
   pip install poetry
   ```

6. Install the project dependencies:
   ```bash
   poetry install
   ```

## Usage

To convert an XML file to OCDS JSON format, activate the Poetry environment and run the following command:

```bash
poetry run python src/ted_and_doffin_to_ocds/main.py input_path output_folder ocid_prefix [options]
```

Required Arguments:

- `input_path`: Path to your input XML file or folder containing XML files
- `output_folder`: Folder where the output JSON files will be saved
- `ocid_prefix`: Your desired OCID prefix

Example:

```bash
poetry run python src/ted_and_doffin_to_ocds/main.py xmlfile/ outputjsonfiles/ ocds-abcd1234
```

This command will:

- Process all XML files in the `xmlfile/` directory
- Save the resulting JSON files in the `outputjsonfiles/` directory
- Use `ocds-abcd1234` as the OCID prefix

If processing a single file, simply replace the input folder with the path to your XML file:

```
poetry run python src/ted_and_doffin_to_ocds/main.py path/to/your/input.xml outputjsonfiles/ ocds-abcd1234
```

The converter will process the input XML file(s) from either TED or Doffin and generate the corresponding OCDS JSON file(s) in the specified output folder.

### Advanced Options

The converter supports several optional arguments:

```bash
poetry run python src/ted_and_doffin_to_ocds/main.py \
    input_path \
    output_folder \
    ocid_prefix \
    [--scheme SCHEME] \
    [--db DB_PATH] \
    [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] \
    [--clear-db]
```

Optional Arguments:

- `--scheme`: Scheme for related processes (default: eu-oj)
- `--db`: Path to SQLite database file (default: notices.db)
- `--log-level`: Set logging level (default: INFO)
- `--clear-db`: Clear existing database before processing

Example with all options:

```bash
poetry run python src/ted_and_doffin_to_ocds/main.py \
    xmlfile/ \
    outputjsonfiles/ \
    ocds-abcd1234 \
    --scheme test-bj \
    --db custom.db \
    --log-level DEBUG \
    --clear-db
```

### File Processing Order

The converter processes files in a specific order to maintain proper relationships:

1. Prior Information Notices (PIN)
2. Contract Notices (CN)
3. Contract Award Notices (CAN)
4. Contract Award Notice Modifications

This order ensures that:

- References between notices are properly maintained
- OCIDs are correctly assigned and reused
- Related processes are accurately tracked

### Logging

The converter writes detailed logs to `app.log` in the current directory. You can control the log level using the `--log-level` option:

- `DEBUG`: Most detailed logging, useful for development and troubleshooting
- `INFO`: Standard operational logging (default)
- `WARNING`: Only potential issues
- `ERROR`: Only error conditions
- `CRITICAL`: Only critical failures

Example with debug logging:

```bash
poetry run python src/ted_and_doffin_to_ocds/main.py \
    xmlfile/ \
    outputjsonfiles/ \
    ocds-abcd1234 \
    --log-level DEBUG
```

Monitor logs in real-time:

```bash
tail -f app.log
```

## Testing

To run the tests, execute the following command in the project root directory:

```
poetry run pytest
```

## OCDS eForm Profile Mapping

This project follows the OCDS eForm profile mapping as specified in the [OCDS Documentation](https://standard.open-contracting.org/profiles/eforms/latest/en/mapping/).

Key aspects of the mapping include:

1. **Business Terms (BT)**: Each XML element corresponding to a specific business term is mapped to the appropriate OCDS field.
2. **Organization Information**: Handling of organization details, including addresses and identifiers.
3. **Lot Information**: Processing lot-specific data and ensuring proper representation in the OCDS structure.
4. **Date Formatting**: Ensuring all dates are formatted according to the ISO 8601 standard.
5. **Document References**: Mapping document references from XML to OCDS document objects.

For detailed mapping information, please refer to the [official OCDS eForm profile mapping documentation](https://standard.open-contracting.org/profiles/eforms/latest/en/mapping/).

## TED and Doffin Data Processing

This converter is designed to handle XML eForm data from both TED and Doffin:

### TED (Tenders Electronic Daily)

- Processes XML data from the EU's official journal dedicated to European public procurement.
- Handles TED-specific XML structures and element names.
- Ensures compliance with EU-specific procurement rules and regulations.

### Doffin (Database for offentlige innkjøp)

- Processes XML data from Norway's national database for public procurement notices.
- Accommodates Doffin-specific XML schemas and data formats.
- Ensures adherence to Norwegian procurement standards and requirements.

The converter identifies the source of the XML data (TED or Doffin) and applies the appropriate parsing and mapping rules to ensure accurate conversion to OCDS format.

## Contributing

Contributions to this project are welcome. Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.