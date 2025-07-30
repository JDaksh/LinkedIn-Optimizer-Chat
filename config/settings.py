import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Config:
    """Application configuration settings"""
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    DB_PATH = "linkedin_memory.db"
    
    AGENT_DESCRIPTIONS = {
        "profile_analyzer": "Specializes in LinkedIn profile optimization and completeness analysis",
        "job_fit_analyzer": "Expert in career planning and job-profile matching",
        "content_enhancer": "Professional content writer for LinkedIn optimization"
    }
    
    AGENT_DISPLAY_NAMES = {
        "profile_analyzer": "📊 Profile Optimizer",
        "job_fit_analyzer": "🎯 Career Advisor", 
        "content_enhancer": "✍️ Content Writer"
    }
    
    AGENT_CONFIGS = [
        {
            "title": "📊 Profile Optimizer",
            "description": "Specializes in profile optimization",
            "skills": [
                "Profile completeness",
                "Missing sections", 
                "Profile improvement",
                "Optimization tips",
                "Profile gaps"
            ]
        },
        {
            "title": "🎯 Career Advisor", 
            "description": "Expert in job-profile matching",
            "skills": [
                "Job fit analysis",
                "Career alignment",
                "Role matching", 
                "Position requirements",
                "Career planning"
            ]
        },
        {
            "title": "✍️ Content Writer",
            "description": "Professional LinkedIn content creator", 
            "skills": [
                "Headline writing",
                "Summary enhancement",
                "Content creation",
                "Writing improvement", 
                "Description rewriting"
            ]
        }
    ]
    
    @classmethod
    def validate_env_vars(cls):
        """Validate required environment variables"""
        if not cls.GROQ_API_KEY:
            st.error("GROQ_API_KEY missing from .env file")
            st.stop()