# XML to OCDS Converter for eForms

This project converts XML data from eForms notices to OCDS (Open Contracting Data Standard) JSON format. It focuses on processing organization and address information, following the eForm profile mapping.

## Table of Contents

- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [OCDS eForm Profile Mapping](#ocds-eform-profile-mapping)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The XML to OCDS Converter processes eForms XML data and converts it into the OCDS JSON format. It handles various business terms (BT) and ensures proper mapping according to the OCDS eForm profile.

## File Structure

```
project_root/
│
├── main.py
├── converters/
│   ├── BT_510c_Organization_Company.py
│   ├── BT_76_Lot.py
│   ├── BT_98_Lot.py
│   └── ...
├── tests/
│   ├── test_BT_767_Lot.py
│   ├── test_BT_76_Lot.py
│   └── ...
├── utils/
│   └── date_utils.py
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

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To convert an XML file to OCDS JSON format, run the following command:

```
python main.py path/to/your/input.xml ocid_prefix_value
```

Replace `path/to/your/input.xml` with the path to your input XML file and `ocid_prefix_value` with your desired OCID prefix.

The converted OCDS JSON will be saved in `output.json` in the project root directory.

## Testing

To run the tests, execute the following command in the project root directory:

```
pytest
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
