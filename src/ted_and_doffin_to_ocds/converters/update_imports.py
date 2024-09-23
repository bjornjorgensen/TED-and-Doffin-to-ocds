import os
import re


def update_imports(directory):
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    content = f.read()

                # Update import statements
                updated_content = re.sub(
                    r"from ted_and_doffin_to_ocds\.converters\.((?:bt|BT|OPP|OPT)_?\d*[a-z]?(?:_[A-Za-z0-9]+)*)",
                    lambda m: f"from ted_and_doffin_to_ocds.converters.{m.group(1).lower()}",
                    content,
                )

                # Update function names
                function_patterns = [
                    r"(parse|merge|map)_([a-z0-9_]+)",
                    r"(parse|merge|map)_([a-z]+)_([a-z_]+)",
                    r"(parse|merge|map)_([a-z]+)_([a-z]+)_([a-z_]+)",
                    r"(parse|merge|map)_([a-z]+)_([a-z]+)_([a-z]+)_([a-z_]+)",
                ]

                for pattern in function_patterns:
                    updated_content = re.sub(
                        pattern, lambda m: "_".join(m.groups()).lower(), updated_content
                    )

                # Handle special cases
                special_cases = [
                    "lotsgroup",
                    "lotsGroup",
                    "lotResult",
                    "Company",
                    "TouchPoint",
                    "Buyer",
                    "SProvider",
                    "Notice",
                    "Organization",
                    "UBO",
                    "Part",
                    "Procedure",
                ]
                for case in special_cases:
                    updated_content = re.sub(
                        f"({case})", lambda m: m.group(1).lower(), updated_content
                    )

                # Handle specific suffixes
                suffixes = ["company", "touchpoint", "ubo"]
                for suffix in suffixes:
                    updated_content = re.sub(
                        f"_(bt_\d+[a-z]?_organization)_{suffix}",
                        lambda m, s=suffix: f"_{m.group(1)}_{s.lower()}",
                        updated_content,
                        flags=re.IGNORECASE,
                    )

                if content != updated_content:
                    with open(file_path, "w") as f:
                        f.write(updated_content)
                    print(f"Updated imports in {file_path}")


# Usage
update_imports("/home/bjorn/github/TED-and-Doffin-to-ocds")
