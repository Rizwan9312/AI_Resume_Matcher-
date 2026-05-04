from parser import parse_resume
from matcher import match_resume_to_job, display_results

resume_text = parse_resume(r"..\data\sample_resumes\rizwan.pdf")

jd_text = """
Paste any real job description
from LinkedIn or any jobs site here
"""

result = match_resume_to_job(resume_text, jd_text)
display_results(result)