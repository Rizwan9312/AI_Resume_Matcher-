"""JobRecommendation model — stores live job postings fetched from JSearch."""

from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class JobRecommendation(Base):
    __tablename__ = "job_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    match_result_id = Column(UUID(as_uuid=True), ForeignKey("match_results.id"), nullable=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)

    # Job data from JSearch API
    job_id = Column(String, unique=True, nullable=False)
    job_title = Column(String, nullable=False)
    employer_name = Column(String)
    employer_logo = Column(String)
    job_publisher = Column(String)       # "LinkedIn", "Indeed", etc.
    job_employment_type = Column(String)
    job_location = Column(String)
    job_description = Column(String)
    job_apply_link = Column(String)
    job_posted_at = Column(DateTime, nullable=True)
    job_salary_min = Column(Float, nullable=True)
    job_salary_max = Column(Float, nullable=True)
    job_salary_currency = Column(String, nullable=True)

    # TF-IDF cosine similarity against resume (0-100)
    relevance_score = Column(Float, default=0.0)

    # Full raw API response kept for future use
    raw_data = Column(JSON)

    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)        # 6 hours from creation
