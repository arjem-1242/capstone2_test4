import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def match_resume_to_jobs(resume, job_postings):
    matches = []

    # Extract and normalize skills from the jobseeker's profile
    resume_skills = set(skill.strip().lower() for skill in resume.get('skills', []))
    logger.debug(f"Extracted skills from jobseeker: {resume_skills}")

    # Extract and normalize location from the jobseeker's profile
    resume_location = resume.get('location', '').strip().lower()
    logger.debug(f"Extracted location from jobseeker: {resume_location}")

    # Extract and normalize education history
    resume_education = set(edu.strip().lower() for edu in
    resume.get('requirements', []))  # Assuming 'requirements' contains education details
    logger.debug(f"Extracted education from jobseeker: {resume_education}")

    # Extract and normalize employment history
    resume_employment = set(
    work.strip().lower() for work in resume.get('position', []))  # Assuming 'position' contains job roles
    logger.debug(f"Extracted employment history from jobseeker: {resume_employment}")

    for job in job_postings:
        logger.debug(f"Processing job: {job.position} at {job.location}")

        # Normalize job skills by splitting, stripping, and converting to lowercase
        job_skills = set(skill.strip().lower() for skill in job.skills.replace("\r\n", ", ").split(", "))
        logger.debug(f"Required skills for job '{job.position}': {job_skills}")

        # Normalize job location
        job_location = job.location.strip().lower()
        logger.debug(f"Location for job '{job.position}': {job_location}")

        # Normalize job education requirements (assuming it's stored as a comma-separated string)
        job_education = set(edu.strip().lower() for edu in
                            job.requirements.replace("\r\n", ", ").split(", ")) if job.requirements else set()
        logger.debug(f"Education requirements for job '{job.position}': {job_education}")

        # Normalize job preferred employment experience (assuming it's stored as a comma-separated string)
        job_experience = set(
            exp.strip().lower() for exp in job.position.replace("\r\n", ", ").split(", ")) if job.position else set()
        logger.debug(f"Preferred employment experience for job '{job.position}': {job_experience}")

        # Compare location and skills
        location_match = resume_location == job_location
        skills_match = not resume_skills.isdisjoint(job_skills)
        education_match = not resume_education.isdisjoint(
            job_education) if job_education else True  # True if no education requirement
        employment_match = not resume_employment.isdisjoint(
            job_experience) if job_experience else True  # True if no experience requirement

        logger.debug(f"Location match: {location_match}")
        logger.debug(f"Skills match: {skills_match}")
        logger.debug(f"Education match: {education_match}")
        logger.debug(f"Employment match: {employment_match}")

        # Calculate match score
        match_score = 0
        if location_match:
            match_score += 25
            logger.debug(f"Added 25 points for location match.")
        if skills_match:
            match_score += 25
            logger.debug(f"Added 25 points for skills match.")
        if education_match:
            match_score += 25  # Education is important but not always a hard requirement
            logger.debug(f"Added 25 points for education match.")
        if employment_match:
            match_score += 25  # Experience adds value but isn't always mandatory
            logger.debug(f"Added 25 points for employment match.")

        # Add to matches if there's a score
        if match_score >= 25:
            logger.debug(f"Match found for job '{job.position}' with score {match_score}")
            matches.append({
                'id': job.id,  # ✅ Include job ID
                'position': job.position,
                'job_description': job.job_description,
                'location': job.location,
                'match_score': match_score,
                'skills': job.skills,  # Include skills if used in matching
                'requirements': job.requirements,  # Include requirements if used in matching
            })
        else:
            logger.debug(f"No match for job '{job.position}'.")

        logger.debug(f"Total matches found: {len(matches)}")
    return matches
