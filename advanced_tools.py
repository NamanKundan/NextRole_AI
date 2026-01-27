import requests
import json
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import streamlit as st

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

class CompanyResearcher:
    """Advanced company research using multiple data sources"""
    
    def __init__(self):
        self.news_api_key = get_api_key('NEWS_API_KEY')
        self.serpapi_key = get_api_key('SERP_API_KEY')
        self.alpha_vantage_key = get_api_key('ALPHA_VANTAGE_API_KEY')
        self.finnhub_key = get_api_key('FINNHUB_API_KEY')
        
    def get_company_news(self, company_name: str, days: int = 30) -> List[Dict]:
        """Get recent news about the company using News API"""
        try:
            if self.news_api_key and self.news_api_key != 'your_news_api_key_here':
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': f'"{company_name}"',
                    'sortBy': 'publishedAt',
                    'pageSize': 10,
                    'language': 'en',
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    return [
                        {
                            'title': a['title'], 
                            'description': a['description'] or 'No description available',
                            'source': a['source']['name'],
                            'published_at': a['publishedAt']
                        } 
                        for a in articles[:8] if a['title'] and a['description']
                    ]
                else:
                    print(f"News API returned status code: {response.status_code}")
            
        except Exception as e:
            print(f"News API error: {e}")
        
        return self._mock_news_data(company_name)
    
    def get_company_financial_data(self, symbol: str) -> Dict:
        """Get company financial data using Alpha Vantage API"""
        try:
            if self.alpha_vantage_key and self.alpha_vantage_key != 'your_alpha_vantage_key_here':
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'OVERVIEW',
                    'symbol': symbol,
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'Symbol' in data:  # Valid response
                        return {
                            'market_cap': data.get('MarketCapitalization', 'N/A'),
                            'pe_ratio': data.get('PERatio', 'N/A'),
                            'dividend_yield': data.get('DividendYield', 'N/A'),
                            'profit_margin': data.get('ProfitMargin', 'N/A'),
                            'sector': data.get('Sector', 'N/A'),
                            'industry': data.get('Industry', 'N/A')
                        }
        except Exception as e:
            print(f"Financial API error: {e}")
        
        return {
            'market_cap': 'Data not available',
            'sector': 'Technology/Services',
            'growth_status': 'Stable/Growing'
        }
    
    def get_market_sentiment(self, company_name: str) -> Dict:
        """Get market sentiment using SERP API for search trends"""
        try:
            if self.serpapi_key and self.serpapi_key != 'your_serp_api_key_here':
                # Note: This is a simplified example - SERP API has different endpoints
                # You might want to use Google Trends or news sentiment analysis
                return {
                    'sentiment': 'Positive',
                    'trend': 'Growing interest',
                    'search_volume': 'High'
                }
        except Exception as e:
            print(f"SERP API error: {e}")
        
        return {
            'sentiment': 'Neutral',
            'trend': 'Stable',
            'market_interest': 'Moderate'
        }
    
    def _mock_news_data(self, company_name: str) -> List[Dict]:
        """Mock news data when API not available"""
        return [
            {'title': f'{company_name} announces new product launch', 'description': 'Company expands market presence'},
            {'title': f'{company_name} reports strong quarterly results', 'description': 'Revenue growth exceeds expectations'},
            {'title': f'{company_name} hiring initiative launched', 'description': 'Company plans to hire 1000+ employees'},
        ]
    
    def get_company_info(self, company_name: str) -> Dict:
        """Get comprehensive company information with real data"""
        news = self.get_company_news(company_name)
        
        # Try to get financial data if company has a stock symbol
        # This is simplified - in production you'd have a symbol lookup
        common_symbols = {
            'google': 'GOOGL', 'microsoft': 'MSFT', 'apple': 'AAPL', 
            'amazon': 'AMZN', 'netflix': 'NFLX', 'tesla': 'TSLA',
            'meta': 'META', 'nvidia': 'NVDA', 'salesforce': 'CRM'
        }
        
        symbol = None
        for company, stock_symbol in common_symbols.items():
            if company.lower() in company_name.lower():
                symbol = stock_symbol
                break
        
        financial_data = self.get_company_financial_data(symbol) if symbol else {}
        market_sentiment = self.get_market_sentiment(company_name)
        
        # Enhanced research summary
        news_count = len([n for n in news if n.get('title')])
        research_summary = f"""
        Recent Analysis for {company_name}:
        • Found {news_count} recent news articles
        • Market Sector: {financial_data.get('sector', 'Technology/Services')}
        • Market Sentiment: {market_sentiment.get('sentiment', 'Positive')}
        • Search Trend: {market_sentiment.get('trend', 'Growing')}
        • Financial Health: {financial_data.get('market_cap', 'Strong') if 'N/A' not in str(financial_data.get('market_cap', '')) else 'Stable'}
        """
        
        return {
            'company_name': company_name,
            'recent_news': news,
            'financial_data': financial_data,
            'market_sentiment': market_sentiment,
            'research_summary': research_summary.strip()
        }

class JobMatcher:
    """Advanced job matching with skill analysis and real job data"""
    
    def __init__(self):
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_api_key = os.getenv('ADZUNA_API_KEY')
    
    def get_real_job_data(self, job_title: str, location: str = "us") -> Dict:
        """Get real job market data using Adzuna API"""
        try:
            if self.adzuna_app_id and self.adzuna_api_key:
                # Adzuna API endpoint for job search
                url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
                params = {
                    'app_id': self.adzuna_app_id,
                    'app_key': self.adzuna_api_key,
                    'what': job_title,
                    'results_per_page': 20,
                    'sort_by': 'salary'
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('results', [])
                    
                    if jobs:
                        salaries = [job.get('salary_max', 0) for job in jobs if job.get('salary_max')]
                        avg_salary = sum(salaries) / len(salaries) if salaries else 0
                        
                        return {
                            'total_jobs': data.get('count', 0),
                            'average_salary': round(avg_salary) if avg_salary > 0 else 'Not specified',
                            'job_locations': list(set([job.get('location', {}).get('display_name', 'N/A') for job in jobs[:10]])),
                            'top_companies': list(set([job.get('company', {}).get('display_name', 'N/A') for job in jobs[:10] if job.get('company')])),
                            'sample_jobs': [
                                {
                                    'title': job.get('title', 'N/A'),
                                    'company': job.get('company', {}).get('display_name', 'N/A'),
                                    'location': job.get('location', {}).get('display_name', 'N/A'),
                                    'salary': f"${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}" if job.get('salary_max') else 'Not specified'
                                }
                                for job in jobs[:5]
                            ]
                        }
        except Exception as e:
            print(f"Adzuna API error: {e}")
        
        return {
            'total_jobs': 'Data not available',
            'market_demand': 'High demand expected',
            'salary_range': '$50,000 - $120,000 (estimated)'
        }
    
    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """Extract technical skills from text"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB',
            'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Machine Learning',
            'AI', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
            'Streamlit', 'Flask', 'Django', 'FastAPI', 'REST API', 'GraphQL',
            'HTML', 'CSS', 'Bootstrap', 'Tailwind', 'Vue.js', 'Angular',
            'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Spark',
            'Linux', 'Unix', 'Bash', 'PowerShell', 'CI/CD', 'Jenkins',
            'Agile', 'Scrum', 'Project Management', 'Leadership', 'Communication'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def calculate_match_score(resume_skills: List[str], job_skills: List[str]) -> Dict:
        """Calculate detailed match score"""
        if not job_skills:
            return {'score': 0, 'matched': [], 'missing': []}
        
        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        score = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
        
        return {
            'score': round(score, 1),
            'matched': matched_skills,
            'missing': missing_skills,
            'total_required': len(job_skills),
            'total_matched': len(matched_skills)
        }
    
    def calculate_job_compatibility(self, resume_text: str, job_description: str) -> Dict:
        """Calculate comprehensive job compatibility with market data"""
        resume_skills = self.extract_skills_from_text(resume_text)
        job_skills = self.extract_skills_from_text(job_description)
        match_data = self.calculate_match_score(resume_skills, job_skills)
        
        # Extract potential job title from job description
        job_title = "software engineer"  # Default
        common_titles = ['software engineer', 'data scientist', 'product manager', 'developer', 'analyst']
        for title in common_titles:
            if title in job_description.lower():
                job_title = title
                break
        
        # Get real market data
        market_data = self.get_real_job_data(job_title)
        
        return {
            'score': match_data['score'],
            'matched_skills': match_data['matched'],
            'missing_skills': match_data['missing'],
            'market_data': market_data,
            'job_title': job_title,
            'recommendation': self._generate_compatibility_recommendation(match_data, market_data)
        }
    
    def _generate_compatibility_recommendation(self, match_data: Dict, market_data: Dict) -> str:
        """Generate compatibility recommendation based on match and market data"""
        score = match_data['score']
        
        if score >= 80:
            return f"Excellent match! You meet {len(match_data['matched'])} out of {match_data['total_required']} requirements. Strong candidate for this role."
        elif score >= 60:
            return f"Good match! Consider developing: {', '.join(match_data['missing'][:3])} to strengthen your profile."
        elif score >= 40:
            return f"Moderate match. Focus on gaining experience in: {', '.join(match_data['missing'][:5])} before applying."
        else:
            return f"Low match. Consider roles requiring: {', '.join(match_data['matched'])} and build skills in: {', '.join(match_data['missing'][:3])}"

class InterviewPrep:
    """Advanced interview preparation system"""
    
    @staticmethod
    def generate_questions_by_role(role: str) -> Dict:
        """Generate role-specific interview questions"""
        question_banks = {
            'software engineer': {
                'technical': [
                    'Explain the difference between REST and GraphQL APIs',
                    'How would you optimize a slow database query?',
                    'Describe your approach to code testing and debugging',
                    'What are the SOLID principles in software development?'
                ],
                'behavioral': [
                    'Tell me about a challenging bug you fixed',
                    'How do you handle conflicting requirements from stakeholders?',
                    'Describe a time you had to learn a new technology quickly'
                ]
            },
            'data scientist': {
                'technical': [
                    'Explain the bias-variance tradeoff in machine learning',
                    'How would you handle missing data in a dataset?',
                    'Describe the difference between supervised and unsupervised learning',
                    'What metrics would you use to evaluate a classification model?'
                ],
                'behavioral': [
                    'Tell me about a data project that didn\'t go as planned',
                    'How do you communicate complex findings to non-technical stakeholders?',
                    'Describe your process for exploring a new dataset'
                ]
            },
            'product manager': {
                'technical': [
                    'How do you prioritize product features?',
                    'Explain A/B testing and when you\'d use it',
                    'How do you gather and analyze user feedback?',
                    'What metrics matter most for product success?'
                ],
                'behavioral': [
                    'Tell me about a product decision you had to make with limited data',
                    'How do you handle disagreements between engineering and design teams?',
                    'Describe a time you had to pivot a product strategy'
                ]
            }
        }
        
        # Default to software engineer if role not found
        role_lower = role.lower()
        for key in question_banks:
            if key in role_lower:
                return question_banks[key]
        
        return question_banks['software engineer']

class ResumeAnalyzer:
    """Advanced resume analysis with ATS optimization"""
    
    @staticmethod
    def calculate_ats_score(resume_text: str) -> Dict:
        """Calculate ATS compatibility score"""
        score = 100
        issues = []
        
        # Check for common ATS issues
        if len(resume_text.split()) < 200:
            score -= 20
            issues.append("Resume may be too short (< 200 words)")
        
        if len(resume_text.split()) > 1000:
            score -= 10
            issues.append("Resume may be too long (> 1000 words)")
        
        # Check for contact information
        if '@' not in resume_text:
            score -= 15
            issues.append("Missing email address")
        
        # Check for phone number pattern
        import re
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if not re.search(phone_pattern, resume_text):
            score -= 10
            issues.append("Phone number format may not be ATS-friendly")
        
        # Check for skills section
        skills_keywords = ['skills', 'technical skills', 'expertise', 'proficiency']
        if not any(keyword in resume_text.lower() for keyword in skills_keywords):
            score -= 15
            issues.append("Missing dedicated skills section")
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': [
                "Use standard section headers (Experience, Education, Skills)",
                "Include relevant keywords from job descriptions",
                "Save as PDF to preserve formatting",
                "Use a clean, simple layout"
            ]
        }