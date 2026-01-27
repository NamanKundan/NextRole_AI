from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
import tempfile
import requests
from bs4 import BeautifulSoup
from advanced_tools import CompanyResearcher, JobMatcher, InterviewPrep, ResumeAnalyzer
import pdfplumber
import time
import streamlit as st

# Load environment variables
load_dotenv()

def get_api_key(key_name: str) -> str:
    """Get API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
        # Fall back to environment variables (for local development)
        return os.getenv(key_name, '')
    except:
        return os.getenv(key_name, '')

# HTML cleaning function
def clean_html_tags(text: str) -> str:
    """Remove HTML tags and clean formatting from text"""
    if not isinstance(text, str):
        return str(text)
    
    # Remove common HTML tags including those with attributes
    import re
    
    # Aggressive div tag removal
    text = re.sub(r'<div[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
    
    # Remove any remaining div-like patterns with any attributes
    text = re.sub(r'<div\s*class\s*=\s*["\'][^"\'>]*["\'][^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?div[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Remove literal div text that might appear
    text = re.sub(r'&lt;div[^&]*&gt;', '', text)
    text = re.sub(r'&lt;/div&gt;', '', text)
    
    # Remove other HTML tags
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    text = text.replace('<p>', '').replace('</p>', '\n')
    text = re.sub(r'</?p[^>]*>', '\n', text)
    text = re.sub(r'<span[^>]*>', '', text)
    text = text.replace('</span>', '')
    text = text.replace('<strong>', '**').replace('</strong>', '**')
    text = text.replace('<b>', '**').replace('</b>', '**')
    text = text.replace('<em>', '*').replace('</em>', '*')
    text = text.replace('<i>', '*').replace('</i>', '*')
    
    # Remove any remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # Remove any leftover HTML-like patterns
    text = re.sub(r'\s*<[^>]*>\s*', ' ', text)
    
    # Clean up common problematic patterns that might slip through
    text = re.sub(r'class\s*=\s*["\'][^"\'>]*["\']', '', text)
    text = re.sub(r'id\s*=\s*["\'][^"\'>]*["\']', '', text)
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Clean up extra whitespace
    text = re.sub(r'\n+', '\n\n', text)  # Replace multiple newlines with double newlines
    text = re.sub(r' +', ' ', text)      # Replace multiple spaces with single space
    
    return text.strip()

# Initialize Gemini model with error handling
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=get_api_key("GOOGLE_API_KEY"),
        temperature=0.3
    )
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    llm = None

# Simplified Career Assistant Class with all interconnected features
class CareerAssistant:
    def __init__(self):
        self.llm = llm
        self.company_researcher = CompanyResearcher()
        self.job_matcher = JobMatcher()
        self.interview_prep = InterviewPrep()
        self.resume_analyzer = ResumeAnalyzer()
        
    def analyze_resume(self, resume_text: str) -> Dict:
        """Comprehensive resume analysis with all advanced features"""
        if not self.llm:
            return {"error": "AI model not available"}
            
        if not resume_text:
            return {"error": "No resume text provided"}
        
        try:
            # Use advanced resume analyzer
            ats_analysis = self.resume_analyzer.calculate_ats_score(resume_text)
            skills = self.job_matcher.extract_skills_from_text(resume_text)
            
            prompt = f"""
            Analyze this resume with comprehensive detail:
            
            Resume Text: {resume_text[:2000]}...
            
            ATS Analysis Data:
            - ATS Score: {ats_analysis['score']}/100
            - Issues Found: {', '.join(ats_analysis['issues']) if ats_analysis['issues'] else 'None'}
            
            Extracted Skills: {', '.join(skills)}
            
            Provide detailed analysis:
            
            ## 📊 Resume Analysis Report
            
            ### Skills Assessment
            - Technical skills identified and proficiency levels
            - Soft skills and leadership qualities
            - Industry-specific competencies
            
            ### Experience Evaluation
            - Career level assessment (Junior/Mid/Senior)
            - Years of experience estimation
            - Career progression analysis
            
            ### ATS Optimization
            - Current ATS compatibility score: {ats_analysis['score']}/100
            - Specific formatting improvements needed
            - Missing keywords for better visibility
            
            ### Content Quality Review
            - Strengths and standout achievements
            - Areas requiring improvement
            - Missing critical sections
            
            ### Market Competitiveness
            - Overall market readiness score (1-10)
            - Comparison to industry standards
            - Competitive advantages identified
            
            ### Action Plan
            - Top 5 specific improvements to implement
            - Keywords to add for better ATS performance
            - Recommended next steps
            
            Format with clear sections, bullet points, and specific recommendations.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "success": True,
                "analysis": clean_html_tags(response.content),
                "ats_score": ats_analysis['score'],
                "extracted_skills": skills,
                "issues": ats_analysis['issues']
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def match_jobs(self, resume_text: str, job_description: str = "") -> Dict:
        """Advanced job matching with role compatibility analysis"""
        if not self.llm:
            return {"error": "AI model not available"}
            
        try:
            # Extract skills from resume
            resume_skills = self.job_matcher.extract_skills_from_text(resume_text)
            job_skills = self.job_matcher.extract_skills_from_text(job_description) if job_description else []
            
            # Calculate compatibility
            compatibility = self.job_matcher.calculate_job_compatibility(resume_text, job_description) if job_description else {"score": 0}
            
            prompt = f"""
            Perform advanced job matching analysis:
            
            Resume Skills: {', '.join(resume_skills)}
            Job Requirements: {', '.join(job_skills) if job_skills else 'General market analysis'}
            Compatibility Score: {compatibility.get('score', 0)}/100
            
            Resume Text: {resume_text[:1500]}...
            {f'Job Description: {job_description[:1000]}...' if job_description else ''}
            
            Provide comprehensive job matching analysis:
            
            ## 🎯 Job Matching Report
            
            ### Skills Alignment
            - Matching skills and proficiency levels
            - Gap analysis for missing requirements
            - Transferable skills identification
            
            ### Role Compatibility
            - Overall fit score: {compatibility.get('score', 'N/A')}/100
            - Experience level match
            - Industry alignment assessment
            
            ### Market Opportunities
            - Recommended job titles and roles
            - Growth industries for your skillset
            - Salary expectations and ranges
            
            ### Skill Development Plan
            - Priority skills to develop
            - Recommended certifications
            - Learning resources and timeline
            
            ### Application Strategy
            - How to position yourself for target roles
            - Keywords to emphasize
            - Portfolio/project recommendations
            
            Provide specific, actionable recommendations.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "success": True,
                "analysis": response.content,
                "resume_skills": resume_skills,
                "job_skills": job_skills,
                "compatibility_score": compatibility.get('score', 0)
            }
            
        except Exception as e:
            return {"error": f"Job matching failed: {str(e)}"}
    
    def research_company(self, company_name: str, resume_text: str = "") -> Dict:
        """Advanced company research with market intelligence"""
        if not self.llm:
            return {"error": "AI model not available"}
            
        try:
            # Use advanced company researcher
            company_data = self.company_researcher.get_company_info(company_name)
            
            prompt = f"""
            Comprehensive Company Research for Interview Preparation:
            
            COMPANY: {company_name}
            
            RECENT NEWS & DEVELOPMENTS:
            {chr(10).join([f"• {news['title']}: {news['description']}" for news in company_data['recent_news']])}
            
            MARKET INTELLIGENCE:
            {company_data['research_summary']}
            
            {f'CANDIDATE PROFILE: {resume_text[:1000]}...' if resume_text else ''}
            
            Provide detailed interview preparation guide:
            
            ## 🏢 Company Intelligence Report
            
            ### Company Overview
            - Mission, vision, and core values
            - Business model and key products/services
            - Market position and competitive advantages
            - Leadership team and organizational structure
            
            ### Recent Developments
            - Latest news and announcements
            - Growth initiatives and strategic moves
            - Financial performance and market trends
            - Industry challenges and opportunities
            
            ### Culture & Work Environment
            - Company culture and values assessment
            - Work-life balance and employee benefits
            - Diversity and inclusion initiatives
            - Employee satisfaction and retention
            
            ### Interview Intelligence
            - Typical interview process and timeline
            - Common interview questions for this company
            - Assessment criteria and what they value
            - Decision-making factors and priorities
            
            ### Strategic Talking Points
            - How to align your experience with their needs
            - Key achievements to highlight
            - Questions to ask your interviewer
            - Value proposition positioning
            
            ### Salary & Benefits Analysis
            - Market rate expectations for roles
            - Benefits and perks typically offered
            - Negotiation strategies and timing
            - Total compensation benchmarks
            
            ### Risk Assessment
            - Company challenges or potential concerns
            - Industry headwinds and market risks
            - Growth sustainability analysis
            
            Make it comprehensive and interview-focused with specific, actionable insights.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "success": True,
                "analysis": clean_html_tags(response.content),
                "recent_news": company_data['recent_news'],
                "company_summary": company_data['research_summary']
            }
            
        except Exception as e:
            return {"error": f"Company research failed: {str(e)}"}
    
    def prepare_interview(self, job_description: str, company_name: str = "", resume_text: str = "") -> Dict:
        """Advanced interview preparation with role-specific questions"""
        if not self.llm:
            return {"error": "AI model not available"}
            
        try:
            # Use advanced interview prep
            role_questions = self.interview_prep.generate_questions_by_role(job_description)
            
            prompt = f"""
            Advanced Interview Preparation Guide:
            
            JOB ROLE: {job_description[:1000]}...
            COMPANY: {company_name}
            
            ROLE-SPECIFIC QUESTIONS BANK:
            Technical Questions: {', '.join(role_questions.get('technical', []))}
            Behavioral Questions: {', '.join(role_questions.get('behavioral', []))}
            
            {f'CANDIDATE PROFILE: {resume_text[:1000]}...' if resume_text else ''}
            
            Create comprehensive interview preparation:
            
            ## 🎯 Interview Preparation Masterplan
            
            ### Technical Interview Questions (15+ questions)
            - Role-specific technical questions with difficulty levels
            - Problem-solving scenarios and case studies
            - System design questions (if applicable)
            - Code challenges and algorithmic thinking
            - Industry-specific technical assessments
            
            ### Behavioral Interview Questions (12+ questions)
            - Leadership and teamwork scenarios
            - Conflict resolution and problem-solving
            - Achievement stories and failure recovery
            - Motivation, career goals, and culture fit
            - Situational judgment and decision-making
            
            ### Company-Specific Questions (8+ questions)
            - Why this company and role specifically?
            - How do you align with company values?
            - Knowledge about products, services, and market
            - Understanding of company challenges and opportunities
            
            ### STAR Method Frameworks
            - Complete templates for behavioral answers
            - Example responses for common scenarios
            - How to structure compelling, memorable stories
            - Quantifiable achievement examples
            
            ### Strategic Questions to Ask Interviewer
            - About the role, team dynamics, and expectations
            - About company culture, growth, and challenges
            - About career development and advancement paths
            - About success metrics and performance evaluation
            
            ### Salary Negotiation Masterclass
            - Market research and salary ranges analysis
            - Total compensation package negotiation
            - When and how to discuss compensation
            - Counter-offer strategies and alternatives
            
            ### Interview Day Excellence
            - Professional presentation and logistics
            - Confidence-building techniques and mindset
            - Follow-up strategies and timeline
            - Thank you note templates and best practices
            
            ### Mock Interview Practice Plan
            - Key scenarios to practice repeatedly
            - Common mistakes to avoid at all costs
            - Recording and self-assessment techniques
            - Peer practice and feedback incorporation
            
            Make it detailed, practical, and specifically tailored to this role and company.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "success": True,
                "analysis": response.content,
                "technical_questions": role_questions.get('technical', []),
                "behavioral_questions": role_questions.get('behavioral', [])
            }
            
        except Exception as e:
            return {"error": f"Interview preparation failed: {str(e)}"}
    
    def comprehensive_career_analysis(self, resume_text: str, job_description: str = "", company_name: str = "") -> Dict:
        """Complete end-to-end career analysis combining all tools"""
        if not self.llm:
            return {"error": "AI model not available"}
            
        try:
            results = {}
            
            # Step 1: Resume Analysis
            resume_result = self.analyze_resume(resume_text)
            if resume_result.get("success"):
                results["resume_analysis"] = resume_result
            
            # Step 2: Job Matching (if job provided)
            if job_description:
                job_result = self.match_jobs(resume_text, job_description)
                if job_result.get("success"):
                    results["job_matching"] = job_result
            
            # Step 3: Company Research (if company provided)
            if company_name:
                company_result = self.research_company(company_name, resume_text)
                if company_result.get("success"):
                    results["company_research"] = company_result
            
            # Step 4: Interview Preparation (if job and/or company provided)
            if job_description or company_name:
                interview_result = self.prepare_interview(job_description, company_name, resume_text)
                if interview_result.get("success"):
                    results["interview_prep"] = interview_result
            
            # Step 5: Comprehensive Summary
            summary_prompt = f"""
            Create a comprehensive career strategy summary based on all analysis:
            
            ## 🚀 Complete Career Strategy Report
            
            ### Executive Summary
            - Overall career readiness assessment
            - Key strengths and competitive advantages
            - Priority areas for improvement
            - Strategic career positioning
            
            ### Integrated Action Plan
            - Immediate actions (next 1-2 weeks)
            - Short-term goals (next 1-3 months)
            - Long-term career strategy (6-12 months)
            - Success metrics and milestones
            
            ### Market Positioning Strategy
            - How to position yourself in the current market
            - Industry trends and opportunities alignment
            - Personal brand development recommendations
            - Networking and visibility strategies
            
            ### Next Steps Prioritization
            1. Top priority actions with deadlines
            2. Resource requirements and investments
            3. Success tracking and measurement
            4. Contingency planning and alternatives
            
            Provide a cohesive, strategic overview that connects all analyses.
            """
            
            summary_response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            results["comprehensive_summary"] = {
                "success": True,
                "analysis": summary_response.content
            }
            
            return {
                "success": True,
                "results": results,
                "total_components": len(results)
            }
            
        except Exception as e:
            return {"error": f"Comprehensive analysis failed: {str(e)}"}

# Utility functions for PDF extraction
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF using multiple robust methods"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Method 1: Try pdfplumber first (most reliable)
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        # Method 2: Fallback to PyPDF2
        try:
            import PyPDF2
            uploaded_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if text.strip():
                return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
        
        # Method 3: LangChain PyPDFLoader as last resort
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                uploaded_file.seek(0)
                tmp_file.write(uploaded_file.read())
                tmp_file.flush()
                
                loader = PyPDFLoader(tmp_file.name)
                docs = loader.load()
                text = "\n".join([doc.page_content for doc in docs])
                
                os.unlink(tmp_file.name)
                return text
        except Exception as e:
            print(f"PyPDFLoader failed: {e}")
        
        return "Could not extract text from PDF. Please try a different file or check if the PDF contains selectable text."
        
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

# Initialize the career assistant
career_assistant = CareerAssistant()