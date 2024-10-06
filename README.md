# XML to OCDS Converter for TED and Doffin eForms

This project converts XML eForm data from TED (Tenders Electronic Daily) and Doffin (Database for offentlige innkjøp) to OCDS (Open Contracting Data Standard) JSON format. It focuses on processing organization and address information, following the eForm profile mapping.

## Table of Contents

- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [OCDS eForm Profile Mapping](#ocds-eform-profile-mapping)
- [TED and Doffin Data Processing](#ted-and-doffin-data-processing)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The XML to OCDS Converter processes eForms XML data from TED and Doffin and converts it into the OCDS JSON format. It handles various business terms (BT) and ensures proper mapping according to the OCDS eForm profile, accommodating the specificities of both TED and Doffin data structures.

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

1. Clone the repository:
   ```
   git clone https://github.com/bjornjorgensen/TED-and-Doffin-to-ocds.git
   ```

2. Change to the project directory:
   ```
   cd TED-and-Doffin-to-ocds
   ```

3. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```

4. Install the project dependencies:
   ```
   poetry install
   ```

## Usage

To convert an XML file to OCDS JSON format, activate the Poetry environment and run the following command:

```
poetry run python src/ted_and_doffin_to_ocds/main.py input_path output_folder ocid_prefix [--scheme scheme_value]
```

Arguments:
- `input_path`: Path to your input XML file or folder containing XML files
- `output_folder`: Folder where the output JSON files will be saved
- `ocid_prefix`: Your desired OCID prefix
- `--scheme`: (Optional) Scheme for related processes (default: eu-oj)

Example:
```
poetry run python src/ted_and_doffin_to_ocds/main.py xmlfile/ outputjsonfiles/ ocds-abcd1234 --scheme test-bj
```
This command will:
- Process all XML files in the `xmlfile/` directory
- Save the resulting JSON files in the `outputjsonfiles/` directory
- Use `ocds-abcd1234` as the OCID prefix
- Use `test-bj` as the scheme for related processes

If processing a single file, simply replace the input folder with the path to your XML file:
```
poetry run python src/ted_and_doffin_to_ocds/main.py path/to/your/input.xml outputjsonfiles/ ocds-abcd1234
```
The converter will process the input XML file(s) from either TED or Doffin and generate the corresponding OCDS JSON file(s) in the specified output folder.

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