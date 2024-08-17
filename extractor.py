import os
import requests
import json
import pandas as pd
import pytesseract
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
import base64
import logging

# Load environment variables
load_dotenv()

# Function to upload an image to imgbb and return its URL
def upload_image_to_imgbb(image_path, api_key, expiration=None):
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error reading image file: {e}")
        return None
    
    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'image': image_data,
    }
    
    if expiration:
        payload['expiration'] = expiration
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
        return None
    
    try:
        response_data = response.json()
        if response_data['success']:
            return response_data['data']['url']
        else:
            logging.error(f"Error in response data: {response_data}")
            return None
    except ValueError as e:
        logging.error(f"Error parsing response JSON: {e}")
        return None

# Function to extract text from an image using OCR
def extract_text_from_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(img)
        return text
    except requests.RequestException as e:
        print(f"Failed to download image: {e}")
        return None

# Function to handle the OpenAI API request and response
def analyze_business_cards(extracted_text, image_url):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analyze the business cards in the image and extract the following information: Name, Title, Company, Phone 1:, Phone 2:, Email 1:, Email 2:, Address:, City:, Country:. If detail is not available tell N/A. The following function will assume the response is a python dictionary containing the extracted information, the dictionary should be a Give the output as a simple string. The output should be in the following format no deviation will be accepted. {{'business cards': [{{'name': 'v saravanan', 'title': 'general manager', 'company': 'fasee medicare', 'phone 1': '07806 970775', 'phone 2': 'n/a', 'email 1': 'faseemedcare@gmail.com', 'email 2': 'n/a', 'address': 's3, 2nd floor, 32, galaxy road', 'city': 'ayanambakkam', 'country': 'india'}}, {{'name': 'sathesh shankar', 'title': 'st. manager-sales & marketing', 'company': 'noxair', 'phone 1': '+91 888 811 3572', 'phone 2': '+91-120-4127100', 'email 1': 'rshankar@noxairindia.com', 'email 2': 'n/a', 'address': 'n/a', 'city': 'n/a', 'country': 'n/a'}}, {{'name': 'dr. rizwan', 'title': 'company ceo', 'company': 'echo medical system', 'phone 1': '9370728183', 'phone 2': 'n/a', 'email 1': 'echodemedicalnanded@gmail.com', 'email 2': 'n/a', 'address': 'air port road, asra nagar, nanded-431605', 'city': 'nanded', 'country': 'india'}}]}}. Use the following data extracted using another OCR model to check the accuracy of your response: {extracted_text}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip().lower().replace('```', '').replace('python', '')

# Function to parse the response and save data to CSV
def save_to_csv(data_str, csv_file_path):
    try:
        json_data = "\n".join(data_str.split('\n')[1:-1]).replace("'", '"')
        data_list = json.loads(json_data)
        data_list_extracted = data_list['business cards']
        df = pd.DataFrame(data_list_extracted)

        if os.path.exists(csv_file_path):
            existing_df = pd.read_csv(csv_file_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            combined_df = df

        combined_df.to_csv(csv_file_path, index=False)
        print(f"Data has been written to {csv_file_path}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

if __name__ == "__main__":
    image_path = "img3.jpeg"
    csv_file_path = "business_card10.csv"

    # Get the API key from environment variables
    api_key = os.getenv('IMGBB_API_KEY')
    if not api_key:
        logging.error("API key not found in environment variables.")
        exit(1)
    
    # Optional: Set expiration time in seconds (e.g., 600 for 10 minutes)
    expiration = 600

    # Upload the image and get the URL
    filelink = upload_image_to_imgbb(image_path, api_key, expiration)

    if filelink:
        # Extract text from the uploaded image
        extracted_text = extract_text_from_image(filelink)

        if extracted_text:
            # Analyze business cards using OpenAI API
            response_data = analyze_business_cards(extracted_text, filelink)
            # Save the extracted data to CSV
            save_to_csv(response_data, csv_file_path)
