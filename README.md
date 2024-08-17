# Business Card Information Extractor

This Python script automates the process of extracting and analyzing information from business cards using OCR (Optical Character Recognition) and 4o vision model. The extracted data is then saved into a CSV file for easy access and further use.



## Requirements

- Python 3.7+
- An imgbb API key
- An OpenAI API key
- The following Python packages:
  - `requests`
  - `pandas`
  - `pytesseract`
  - `Pillow`
  - `python-dotenv`
  - `openai`

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/business-card-extractor.git
   cd business-card-extractor

Create a .env file in the root of your project directory and add your OpenAI & IMGBB API key in the following format:

OPENAI_API_KEY = "Input_your_key_here"

IMGBB_API_KEY=Input_your_key_here
