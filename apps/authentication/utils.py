import os
from PyPDF2 import PdfReader
from docx import Document
import re
from bs4 import BeautifulSoup
import requests
def extract_text_from_cv(file_path):
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension.lower() == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    text = ""
    doc = Document(docx_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_keywords(text):
    spoken_language_list = ["english", "french", "arabic", "spanish", "german", "chinese", "italian", "russian", "portuguese", "japanese","korean" , "dutch","Dutch" , "Korean"]
    skills = re.findall(r'Skills?:\s*([\s\S]*?)(?=\n[A-Z].*|Experience:|Education:|Languages:)', text, re.IGNORECASE)
    experience = re.findall(r'Experience:\s*([\s\S]*?)(?=\n[A-Z].*|Skills:|Education:|Languages:)', text, re.IGNORECASE)
    education = re.findall(r'(Education|Courses):\s*([\s\S]*?)(?=\n[A-Z].*|Skills:|Experience:|Languages:)', text, re.IGNORECASE)
    languages = re.findall(r'Languages?:\s*([\s\S]*?)(?=\n[A-Z].*|Skills:|Experience:|Education:)', text, re.IGNORECASE)
    spoken_languages = []
    for language in spoken_language_list:
        # Use regular expressions to find exact matches for each language
        if re.search(rf'\b{language}\b', text, re.IGNORECASE):
            spoken_languages.append(language.capitalize())
    return {
        'skills': skills[0].strip() if skills else None,
        'experience': experience[0].strip() if experience else None,
        'education': education[0] if education else None,
        'languages' :spoken_languages if spoken_languages else None,
    }




def get_coursera_courses(skill):
    url = f'https://www.coursera.org/search?query={skill}'
    response = requests.get(url)
    
    # Check for a successful request
    if response.status_code != 200:
        print(f"Failed to retrieve courses for skill '{skill}': {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    courses = []
    for item in soup.find_all('div', class_='css-16m4c33'):
        title_tag = item.find('h3', class_='cds-CommonCard-title css-6ecy9b')
        image_tag = item.find('img')  # Course image
        partner_name_tag = item.find('p', class_='cds-ProductCard-partnerNames css-vac8rf')
        
        rating_tag = item.find('p', class_='css-2xargn')  # Update class based on current structure
        subscribers_tag = item.find('p', class_='css-vac8rf')  
        if title_tag:
            title = title_tag.get_text().strip()
            link = 'https://www.coursera.org' + item.find('a')['href']
            image_url = image_tag['src'] if image_tag else None
            partner_name = partner_name_tag.get_text().strip() if partner_name_tag else "Unknown Partner"
            rating = rating_tag.get_text().strip() if rating_tag else "No rating"
            subscribers = subscribers_tag.get_text().strip() if subscribers_tag else "No subscribers"
            
            courses.append({
                'title': title,
                'link': link,
                'image': image_url,
                'partner_name': partner_name,
                'rating' : rating,
                'subscribers' : subscribers,
                
            })

            # Limit to 5 courses
            if len(courses) >= 4:
                break

    if not courses:
        print(f"No courses found for skill '{skill}'.")
    
    return courses
