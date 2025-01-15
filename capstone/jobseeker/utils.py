import spacy
from django.conf import settings
import pandas as pd

from core import *
from .models import Education, Employment, JobseekerProfile, ResumeDocument
import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np
from pyresparser import ResumeParser

import re
import os

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from rapidfuzz import process as rapid_process

from spacy.lang.en import English
from django.contrib.staticfiles.finders import find

nlp = spacy.load("en_core_web_sm")

def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to binarize the image
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Optional: Resize image to enhance smaller text
    scale_percent = 150
    width = int(binary_image.shape[1] * scale_percent / 100)
    height = int(binary_image.shape[0] * scale_percent / 100)
    resized_image = cv2.resize(binary_image, (width, height), interpolation=cv2.INTER_CUBIC)

    # Denoising (optional, may vary in effect)
    denoised_image = cv2.fastNlMeansDenoising(resized_image, None, 30, 7, 21)

    return denoised_image

def extract_text_from_resume(file_path):
    pages = convert_from_path(file_path) if file_path.endswith('.pdf') else [file_path]
    text = ""
    for page in pages:
        if isinstance(page, str):
            image = cv2.imread(page)
        else:
            image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        # Preprocess image before OCR
        preprocessed_image = preprocess_image(image)
        text += pytesseract.image_to_string(preprocessed_image)
    return text

def extract_data_with_pyresparser(file_path):
    try:
        # Ensure the file exists before processing
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Use Pyresparser to extract data
        data = ResumeParser(file_path).get_extracted_data()
        return data
    except Exception as e:
        # Handle errors gracefully and log them
        print(f"Error while using Pyresparser: {e}")
        return {}
#
# def extract_resume_text_or_data(file_path):
#     """
#     Determines whether to use OCR (for images) or pyresparser (for text-based files).
#     """
#     if file_path.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
#         # Use OCR for image-based resumes
#         return {"raw_text": extract_text_from_resume(file_path)}
#     elif file_path.endswith('.pdf'):
#         try:
#             # Attempt pyresparser for text-based PDFs
#             pyresparser_data = extract_data_with_pyresparser(file_path)
#             return {"pyresparser_data": pyresparser_data}
#         except Exception as e:
#             # Fallback to OCR if pyresparser fails
#             print(f"Pyresparser failed: {e}, falling back to OCR.")
#             return {"raw_text": extract_text_from_resume(file_path)}
#     else:
#         raise ValueError("Unsupported file format. Only PDF and image files are allowed.")

def load_skills_from_csv():
    """
    Loads skills from a CSV file in the static folder into a set for fast lookups.
    """
    # Define the path to your skills.csv file in the static directory
    skills_file_path = os.path.join(settings.BASE_DIR, 'core/static/jobseeker/skill.csv')

    # Load the CSV file using pandas
    df = pd.read_csv(skills_file_path)

    # Extract the skills into a set (assuming the column name is 'Skill')
    skills_set = {str(skill).strip() for skill in df['Skills'].values if str(skill).strip()}

    print(f"Total rows read: {len(df)}")
    return skills_set

def load_degrees_from_csv():
    """
    Loads skills from a CSV file in the static folder into a set for fast lookups.
    """
    # Define the path to your degrees.csv file in the static directory
    degrees_file_path = os.path.join(settings.BASE_DIR, 'core/static/jobseeker/degrees.csv')

    # Load the CSV file using pandas
    df = pd.read_csv(degrees_file_path)

    # Extract the degrees into a set (assuming the column name is 'Degrees')
    degrees_set = {str(degree).strip() for degree in df['Degrees'].values if str(degree).strip()}

    print(f"Total rows read: {len(df)}")
    return degrees_set

def load_titles_from_csv():
    """
    Loads skills from a CSV file in the static folder into a set for fast lookups.
    """
    # Define the path to your skills.csv file in the static directory
    titles_file_path = os.path.join(settings.BASE_DIR, 'core/static/jobseeker/titles.csv')

    # Load the CSV file using pandas
    df = pd.read_csv(titles_file_path)

    # Extract the skills into a set (assuming the column name is 'Titles')
    titles_set = {str(title).strip() for title in df['Titles'].values if str(title).strip()}

    print(f"Total rows read: {len(df)}")
    return titles_set

def fuzzy_match(title, title_set, threshold=90):
    """
    Matches the input title to the closest title in the set using fuzzy matching.
    Skips matching titles that contain time, date, days, or months keywords.
    Includes detailed debug output to visualize the matching process.
    """
    # Define keywords related to time, date, days, and months
    time_related_keywords = {
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may", "june", "july", "august",
        "september", "october", "november", "december",
        "am", "pm", "morning", "afternoon", "evening", "night", "week", "month",
        "year", "today", "yesterday", "tomorrow", "date"
    }

    # Lowercase title for case-insensitive comparison
    title_lower = title.lower()

    # Check if the title contains any time-related keywords
    if any(keyword in title_lower for keyword in time_related_keywords):
        print(f"Title '{title}' skipped (contains time-related keywords).\n")
        return None

    print(f"Input Title: '{title}'")
    # print(f"Comparing against Title Set: {title_set}")
    # print(f"Threshold: {threshold}\n")

    # Perform fuzzy matching and extract all matches with scores
    all_matches = process.extract(title, title_set, scorer=fuzz.token_sort_ratio)

    # Debug: Print all matches and their scores
    print("All Matches (Title: Score):")
    for matched_title, score in all_matches:
        print(f"  - {matched_title}: {score}")

    # Select the best match above the threshold
    match = process.extractOne(title, title_set, scorer=fuzz.token_sort_ratio)
    if match:
        print(f"\nBest Match: '{match[0]}' with Score: {match[1]}")
        if match[1] >= threshold:
            print("Result: Match accepted.\n")
            return match[0]
        else:
            print("Result: No match exceeds the threshold.\n")
            return None

    print("Result: No matches found.\n")
    return None

def parse_resume_text(text):
    doc = nlp(text)

    name = extract_name(doc)
    phone = extract_phone(doc)
    skills = extract_skills(doc, skills_set=load_skills_from_csv(), threshold=78)
    education = extract_education(doc, degrees_set=load_degrees_from_csv(), threshold=97, max_tokens=6)
    employment = extract_employment(doc, titles_set=load_titles_from_csv(), threshold=97, max_tokens=3)

    return {
        "name": name,
        "phone": phone,
        "skills": skills,
        "education": education,
        "employment": employment,
    }

def extract_name(doc):
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_phone(doc):
    phone_pattern = r'\+?[1-9]\d{1,14}'
    phones = re.findall(phone_pattern, doc.text)
    return phones[0] if phones else None

def extract_skills(doc, skills_set, threshold=78, max_tokens=6):
    """
    Extracts skills from the document using fuzzy matching.
    Limits substring generation to improve efficiency.
    """
    extracted_skills = set()
    doc_text_tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    doc_text = " ".join(doc_text_tokens)  # Reconstruct document without punctuation or extra spaces

    # Preprocess skills set
    skills_set = {skill.lower() for skill in skills_set}

    # Generate substrings with a limited length (max_tokens)
    n = len(doc_text_tokens)
    substrings = set(
        " ".join(doc_text_tokens[i:j + 1])
        for i in range(n)
        for j in range(i, min(i + max_tokens, n))
    )

    # Match substrings against skills set
    for substring in substrings:
        if substring in skills_set:  # Exact match first
            extracted_skills.add(substring)
        else:
            matched_skill = fuzzy_match(substring, skills_set, threshold)
            if matched_skill:
                extracted_skills.add(matched_skill)

    return list(extracted_skills)
# ----------------------------------
# def extract_skills(doc): without csv file matching
#     skills_list = ["Electrical", "Team Leader", "JavaScript", "Machine Learning", "Logistics", "Engineer"]
#     return [token.text for token in doc if token.text in skills_list]
#-----------------------------------

# ----------------------------------
# def extract_skills(doc, skills_set): single-word skills extraction only
#     """
#     Extracts skills from the document using a preloaded skills set.
#     """
#     # Use a set comprehension to ensure uniqueness
#     extracted_skills = {token.text for token in doc if token.text in skills_set}
#
#     # Convert back to a list if needed
#     return list(extracted_skills)
#------------------------------------
# def extract_skills(doc, skills_set, threshold=78):
#     ### Working, showing optimal results but haven't tried using diff test resume :)
#     """
#     Extracts skills from the document using fuzzy matching.
#     Ensures that all substrings or phrases in the document are considered.
#     """
#     extracted_skills = set()
#     doc_text_tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
#     doc_text = " ".join(doc_text_tokens)  # Reconstruct document without punctuation or extra spaces
#
#     # Debug: Show document tokens
#     print(f"Document Tokens: {doc_text_tokens}")
#
#     # Generate all possible substrings of tokens
#     n = len(doc_text_tokens)
#     substrings = set(" ".join(doc_text_tokens[i:j + 1]) for i in range(n) for j in range(i, n))
#
#     # Debug: Show all substrings generated
#     print(f"Generated Substrings (Count: {len(substrings)}): {substrings}")
#
#     # Match each substring against the skills_set
#     for substring in substrings:
#         matched_skill = fuzzy_match(substring, skills_set, threshold)
#         if matched_skill:
#             extracted_skills.add(matched_skill)
#
#     return list(extracted_skills)

def extract_education(doc, degrees_set, threshold=97, max_tokens=6):
    """
    Extracts education details (degrees) from the document using fuzzy matching.
    Ensures substrings are limited in length for efficiency and matches each degree only once.
    """
    education_data = []
    # Preprocess document tokens
    doc_text_tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    doc_text = " ".join(doc_text_tokens)  # Reconstruct document without punctuation or extra spaces

    # Debug: Show document tokens
    print(f"Document Tokens: {doc_text_tokens}")

    # Preprocess degrees set
    degrees_set = {degree.lower() for degree in degrees_set}
    remaining_degrees = degrees_set.copy()  # Track unmatched degrees

    # Generate substrings with a limited length
    n = len(doc_text_tokens)
    substrings = set(
        " ".join(doc_text_tokens[i:j + 1])
        for i in range(n)
        for j in range(i, min(i + max_tokens, n))
    )

    # Debug: Show substring count
    print(f"Generated Substrings (Count: {len(substrings)}): {list(substrings)[:10]}")  # Show first 10 substrings

    # Match substrings against degrees set
    for substring in substrings:
        match = rapid_process.extractOne(substring, remaining_degrees, score_cutoff=threshold)
        if match:
            matched_degree, score = match[0], match[1]
            education_data.append({
                "degree": matched_degree,
                # "match_score": score, Debug and checking purposes
            })
            remaining_degrees.remove(matched_degree)  # Remove matched degree to prevent duplicate matches

    return education_data
# def extract_education(doc, degrees_set, threshold=95):
#     ### Working best but takes time
#     """
#     Extracts education details (degrees) from the document using fuzzy matching.
#     Ensures that all substrings or phrases in the document are considered.
#     Restricts matching of each degree in degrees_set to only once.
#     """
#     education_data = []
#     doc_text_tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
#     doc_text = " ".join(doc_text_tokens)
#
#     # Generate all possible substrings of tokens
#     n = len(doc_text_tokens)
#     substrings = set(" ".join(doc_text_tokens[i:j + 1]) for i in range(n) for j in range(i, n))
#
#     remaining_degrees = set(degrees_set)  # Create a copy of degrees_set to track remaining degrees
#
#     for substring in substrings:
#         matched_degree = fuzzy_match(substring, remaining_degrees, threshold)
#         if matched_degree:
#             education_data.append({
#                 "degree": matched_degree,
#                 # "context": substring, checking where does the result being matched
#             })
#             remaining_degrees.remove(matched_degree)  # Remove matched degree from remaining_degrees
#
#     return education_data
def extract_employment(doc, titles_set, threshold=97, max_tokens=3):
    """
    Extracts employment data (job titles) from the document using fuzzy matching.
    Limits substring generation for efficiency.
    """
    employment_data = []
    # Preprocess document tokens
    doc_text_tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    doc_text = " ".join(doc_text_tokens)  # Reconstruct document without punctuation or extra spaces

    # Debug: Show document tokens
    # print(f"Document Tokens: {doc_text_tokens}")

    # Preprocess titles set
    titles_set = {title.lower() for title in titles_set}

    # Generate substrings with a limited length
    n = len(doc_text_tokens)
    substrings = set(
        " ".join(doc_text_tokens[i:j + 1])
        for i in range(n)
        for j in range(i, min(i + max_tokens, n))
    )

    # Debug: Show substring count
    print(f"Generated Substrings (Count: {len(substrings)}): {list(substrings)[:10]}")  # Show first 10 substrings

    # Match substrings against titles set
    for substring in substrings:
        match = rapid_process.extractOne(substring, titles_set, score_cutoff=threshold)
        if match:
            matched_title, score = match[0], match[1]
            employment_data.append({
                "position": matched_title,
                # "match_score": score, Debug and checking purposes
            })

    return employment_data

def update_user_resume(user, parsed_data):
    from jobseeker.models import Education, Employment  # Import your models

    try:
        resume = ResumeDocument.objects.get(user=user)
    except ResumeDocument.DoesNotExist:
        return False  # Handle the case where the resume doesn't exist

    # Update phone
    resume.phone = parsed_data.get("phone", resume.phone)

    # Update skills
    if "skills" in parsed_data:
        resume.skills = ", ".join(parsed_data["skills"])

    resume.save()  # Save updated phone and skills
    # Update education
    if "education" in parsed_data:
        education_data = parsed_data["education"]

        # Delete existing education data for the resume
        Education.objects.filter(resume=resume).delete()

        # Create new education objects
        for edu in education_data:
            Education.objects.create(
                resume=resume,
                program=edu.get("degree", ""),
                school=edu.get("school", ""),
                started=edu.get("started"),
                finished=edu.get("finished"),
                user=user,
            )

    # Update employment
    if "employment" in parsed_data:
        employment_data = parsed_data["employment"]

        # Delete existing employment data for the resume
        Employment.objects.filter(resume=resume).delete()

        # Create new employment objects
        for emp in employment_data:
            Employment.objects.create(
                resume=resume,
                role=emp.get("position", ""),
                company=emp.get("company", ""),
                hired=emp.get("hired"),
                resigned=emp.get("resigned"),
                user=user,
            )
    return True

def handle_new_entry(change, resume, user):
    """
    Handles creating a new Education or Employment entry based on the 'change' data.
    """
    if change["field"] in ["school", "degree", "started", "finished"]:
        # Handle Education
        Education.objects.create(
            resume=resume,
            school=change.get("school", ""),
            program=change.get("degree", ""),
            started=change.get("started"),
            finished=change.get("finished"),
            user=user,
        )
    elif change["field"] in ["company", "position", "hired", "resigned"]:
        # Handle Employment
        Employment.objects.create(
            resume=resume,
            company=change.get("company", ""),
            role=change.get("position", ""),
            hired=change.get("hired"),
            resigned=change.get("resigned"),
            user=user,
        )

# def extract_employment(doc, titles_set, threshold=85):
#     ### Working, extraction of job titles but takes too long
#     """
#     Extracts employment data (job titles) from the document using fuzzy matching.
#     Ensures that all substrings or phrases in the document are considered.
#     """
#     employment_data = []
#     doc_text_tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
#     doc_text = " ".join(doc_text_tokens)  # Reconstruct document without punctuation or extra spaces
#
#     # Debug: Show document tokens
#     print(f"Document Tokens: {doc_text_tokens}")
#
#     # Generate all possible substrings of tokens
#     n = len(doc_text_tokens)
#     substrings = set(" ".join(doc_text_tokens[i:j + 1]) for i in range(n) for j in range(i, n))
#
#     # Debug: Show all substrings generated
#     print(f"Generated Substrings (Count: {len(substrings)}): {substrings}")
#
#     # Match each substring against the titles_set
#     for substring in substrings:
#         matched_title = fuzzy_match(substring, titles_set, threshold)
#         if matched_title:
#             employment_data.append({
#                 "position": matched_title,
#                 # "context": substring,  # Provide context of the match
#             })
#
#     return employment_data

def update_resume_document(resume_document):
    # Extract and parse text
    raw_text = extract_text_from_resume(resume_document.resume.path)
    parsed_data = parse_resume_text(raw_text)

    # Save raw text and parsed data to ResumeDocument
    resume_document.raw_text = raw_text
    resume_document.parsed_data = parsed_data
    resume_document.processed = True  # Mark as processed
    resume_document.status = "Completed"  # Set status to Completed
    resume_document.save()

    # Optionally, log confirmation or send notification (if using email or alerts)
    print(f"Resume for {resume_document.user.username} has been successfully parsed and processed.")
    # You could also update the JobseekerProfile or trigger other workflows here
    # update_user_resume(resume_document.user, parsed_data)

    # You can add more confirmation steps, like sending a confirmation email:
    # send_confirmation_email(resume_document.user)
