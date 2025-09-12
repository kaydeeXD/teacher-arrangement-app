# Teacher Arrangement System

## Overview
The Teacher Arrangement System is a web application designed to facilitate the management of teacher arrangements based on their availability and timetable. The application allows users to upload a timetable, specify absent teachers, and generate substitute arrangements efficiently.

## Features
- Upload and parse timetable Excel files.
- Manage teacher absences and generate arrangements.
- Store and retrieve weekly logs from Google Sheets.
- User-friendly interface built with Streamlit.

## Project Structure
```
teacher-arrangement-system
├── src
│   ├── app.py               # Main entry point of the application
│   ├── parser.py            # Functions for parsing timetable Excel files
│   ├── arranger.py          # Logic for generating teacher arrangements
│   ├── gsheet.py            # Interactions with Google Sheets
│   ├── persistence.py       # Manages application state and logs
│   ├── utils.py             # Utility functions
│   └── constants.py         # Constants used throughout the application
├── tests
│   └── test_arranger.py     # Unit tests for arrangement generation
├── .streamlit
│   └── config.toml          # Configuration settings for Streamlit
├── requirements.txt          # Project dependencies
├── .gitignore                # Files and directories to ignore by Git
├── credentials.json.sample   # Sample configuration for Google Sheets API credentials
└── README.md                 # Documentation for the project
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd teacher-arrangement-system
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   streamlit run src/app.py
   ```
2. Upload the timetable Excel file when prompted.
3. Select absent teachers and generate arrangements.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.