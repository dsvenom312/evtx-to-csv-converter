# EVTX to CSV Converter

A simple Python tool to convert multiple `.evtx` (Windows Event Log) files into `.csv` format for easier analysis.

This tool scans a folder containing `.evtx` files and converts each file into a CSV file automatically.

## Features

- Converts multiple `.evtx` files at once
- Outputs CSV files for easy analysis
- Simple execution
- Useful for DFIR, SOC analysis, and log investigation

## Folder Structure

Place the script in the parent directory and the EVTX files inside a folder.

Example structure:

Example structure:


<details>
<summary>Click to expand folder structure</summary>

```
parent-folder/
│
├── converter2.py
│
└── evtx-folder/
    ├── Security.evtx
    ├── System.evtx
    ├── Application.evtx
    └── other_logs.evtx
```

</details>

## Requirements

Python 3

Required library:

python-evtx

Install it using:

pip install python-evtx

## Usage

Navigate to the parent folder where the script is located.

Run the following command:

python converter2.py

The script will automatically:

1. Read all `.evtx` files inside the EVTX folder
2. Convert each log into CSV format
3. Save the CSV files in the output directory or the same folder

## Example

Input:

evtx-folder/Security.evtx

Output:

evtx-folder/Security.csv

## Use Cases

This tool is useful for:

- Digital forensics investigations
- SOC log analysis
- Incident response
- Security log parsing
- Converting Windows event logs into searchable format

## Notes

Windows Event Logs (`.evtx`) contain structured system and security events such as:

- login attempts
- process creation
- system activity
- security alerts

Converting them to CSV allows analysts to examine them with tools like:

- Excel
- Python pandas
- SIEM platforms

## License

Free to use for educational and research purposes.
