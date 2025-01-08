import requests
import io
import bs4 as bs
import PyPDF2
import pandas as pd
import docx
from pymongo import MongoClient
from dotenv import load_dotenv
import os

def download_file(url):
    """Download file from URL and return as bytes."""
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    raise Exception(f"Failed to download file: {response.status_code}")

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file."""
    pdf_reader = PyPDF2.PdfReader(file_bytes)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_excel(file_bytes):
    """Extract text from Excel file."""
    df = pd.read_excel(file_bytes)
    return df.to_string()

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file."""
    doc = docx.Document(file_bytes)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def save_to_database(seller, file_content):
    """Save the extracted text to MongoDB database."""
    # path = os.path.join('../../../', '.env')
    # load_dotenv(dotenv_path=path)
    
    MONGO_URI = os.getenv("MONGO_URI")
    
    client = MongoClient(MONGO_URI)
    db = client.stock_data
    collection = db.stock_fundamental
    
    document = {
        "_id": seller,  
        "file": file_content,
    }
    
    collection.update_one(
        {"_id": seller},
        {"$set": document},
        upsert=True
    )
    
    client.close()

def process_file(url, seller, file_type):
    """Main function to process the file."""
    try:
        file_bytes = download_file(url)
        
        if file_type == 'pdf':
            text = extract_text_from_pdf(file_bytes)
        elif file_type in ['xls', 'xlsx']:
            text = extract_text_from_excel(file_bytes)
        elif file_type in ['doc', 'docx']:
            text = extract_text_from_docx(file_bytes)
        else:
            raise Exception(f"Unsupported file type: {file_type}")
        
        return text
        
    except Exception as e:
        print(f"Error processing file for {seller}: {str(e)}")
        return False

if __name__ == "__main__":
    sellers = requests.get('http://api-container:8000/stocks').json()
    
    for seller in sellers:
        url = f'https://www.mse.mk/mk/symbol/{seller}'
        response = requests.get(url)
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        li_elements = soup.select('div#seiNetIssuerLatestNews a')
        if not li_elements:
            print(f"No files found for seller {seller}")
            continue
        link = [a['href'] for a in li_elements if 'href' in a.attrs][0]
        id = link.split('/')[-1]
        url_link = f'https://api.seinet.com.mk/public/documents/single/{id}'
        json = requests.get(url_link).json()
        if 'content' in json['data']:
            content = json['data']['content']
            content = bs.BeautifulSoup(content, 'html.parser').get_text()
        if 'attachments' in json['data'] and len(json['data']['attachments']) > 0:
            file = json['data']['attachments'][0]['attachmentId']
            url_file = f'https://api.seinet.com.mk/public/documents/attachment/{file}'
            file_type = json['data']['attachments'][0]['fileName'].split('.')[-1]
            text = process_file(url_file, seller, file_type)
        text_full = content + text if content and text else content or text
        if text_full:
            save_to_database(seller, text_full)
        if text or content:
            print(f"Successfully processed file for seller {seller}")