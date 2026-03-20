"""
Skill Extraction Module
Extracts technical and soft skills from resume and job description texts
"""

import re
from typing import List, Tuple, Set
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Common technical and soft skills database
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'csharp', 'c++', 'go', 'rust', 'php', 'ruby',
    'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'groovy', 'dart', 'julia',
    
    # Frontend
    'react', 'angular', 'vue', 'html', 'css', 'sass', 'bootstrap', 'tailwind', 'webpack',
    'babel', 'nextjs', 'gatsby', 'd3js', 'threejs',
    
    # Backend & Frameworks
    'django', 'flask', 'fastapi', 'spring', 'hibernate', 'rails', 'express', 'nestjs',
    'laravel', 'symfony', 'asp.net', 'nodejs', 'node',
    
    # Databases
    'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'firebase', 'mariadb', 'oracle', 'nosql', 'sqlite',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'jenkins', 'gitlab', 'github',
    'terraform', 'ansible', 'ci/cd', 'devops', 'microservices', 'serverless',
    
    # Data & ML
    'tensorflow', 'keras', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark',
    'hadoop', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
    'airflow', 'dbt', 'etl', 'analytics',
    
    # APIs & Tools
    'rest', 'graphql', 'soap', 'json', 'xml', 'git', 'rest api', 'postman',
    'swagger', 'openapi', 'api design',
    
    # Testing
    'junit', 'pytest', 'karma', 'jest', 'mocha', 'rspec', 'selenium', 'cucumber',
    'unit testing', 'integration testing', 'e2e testing', 'tdd', 'qa',
    
    # Other
    'linux', 'unix', 'windows', 'agile', 'scrum', 'jira', 'confluence', 'git',
    'design patterns', 'oops', 'architecture', 'microservices'
}

SOFT_SKILLS = {
    'communication', 'leadership', 'teamwork', 'problem-solving', 'critical thinking',
    'time management', 'project management', 'stakeholder management', 'presentation',
    'negotiation', 'conflict resolution', 'adaptability', 'creativity', 'analytical',
    'decision making', 'strategic thinking', 'mentoring', 'coaching', 'collaboration',
    'customer service', 'sales', 'marketing', 'business acumen', 'financial management',
    'organizational skills', 'attention to detail', 'multitasking', 'self-motivated',
    'learning agility', 'emotional intelligence', 'empathy', 'reliability', 'integrity'
}

SKILL_KEYWORDS = TECHNICAL_SKILLS.union(SOFT_SKILLS)


class SkillExtractor:
    """Extract skills from resume and job description texts"""
    
    def __init__(self):
        self.technical_skills = TECHNICAL_SKILLS
        self.soft_skills = SOFT_SKILLS
        self.all_skills = SKILL_KEYWORDS
    
    def extract_skills(self, text: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract skills from text
        Returns: (technical_skills, soft_skills)
        """
        if not text:
            return set(), set()
        
        # Clean and normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s/-]', ' ', text)
        words = text.split()
        
        # Extract individual skills
        found_technical = set()
        found_soft = set()
        
        # Check for exact matches
        for skill in self.technical_skills:
            if skill in text or f' {skill} ' in f' {text} ':
                found_technical.add(skill)
        
        for skill in self.soft_skills:
            if skill in text or f' {skill} ' in f' {text} ':
                found_soft.add(skill)
        
        # Check for compound skills (e.g., "machine learning", "deep learning")
        text_for_phrases = ' ' + text + ' '
        compound_skills = {
            'machine learning', 'deep learning', 'natural language processing',
            'computer vision', 'data science', 'artificial intelligence',
            'rest api', 'web development', 'full stack', 'mobile development',
            'software engineering', 'quality assurance', 'devops engineering',
            'cloud computing', 'problem solving', 'time management',
            'project management', 'customer service', 'business analysis'
        }
        
        for compound_skill in compound_skills:
            if compound_skill in text_for_phrases:
                if any(word in compound_skill.split() for word in self.technical_skills):
                    found_technical.add(compound_skill)
                else:
                    found_soft.add(compound_skill)
        
        return found_technical, found_soft
    
    def extract_with_proficiency(self, text: str) -> dict:
        """
        Extract skills with estimated proficiency level
        Returns: {'skill_name': proficiency_level}
        """
        text_lower = text.lower()
        technical, soft = self.extract_skills(text)
        
        proficiency_map = {}
        
        # Define proficiency keywords
        expert_keywords = ['expert', 'advanced', 'master', 'specialist', 'senior', 'lead', 'architect']
        intermediate_keywords = ['experienced', 'proficient', 'intermediate', 'strong']
        beginner_keywords = ['familiar', 'basic', 'beginner', 'learning', 'knowledge of']
        
        for skill in technical.union(soft):
            skill_context = self._get_skill_context(text_lower, skill, window=30)
            
            # Determine proficiency
            if any(kw in skill_context for kw in expert_keywords):
                proficiency_map[skill] = 'expert'
            elif any(kw in skill_context for kw in intermediate_keywords):
                proficiency_map[skill] = 'intermediate'
            elif any(kw in skill_context for kw in beginner_keywords):
                proficiency_map[skill] = 'beginner'
            else:
                proficiency_map[skill] = 'mentioned'
        
        return proficiency_map
    
    def _get_skill_context(self, text: str, skill: str, window: int = 30) -> str:
        """Get context around skill mention"""
        idx = text.find(skill)
        if idx == -1:
            return ""
        start = max(0, idx - window)
        end = min(len(text), idx + len(skill) + window)
        return text[start:end]
    
    def score_skills(self, skills_dict: dict, proficiency_weights: dict = None) -> float:
        """
        Score overall skill level based on skills and proficiency
        Returns: Score between 0 and 100
        """
        if proficiency_weights is None:
            proficiency_weights = {'expert': 3, 'intermediate': 2, 'beginner': 1, 'mentioned': 0.5}
        
        if not skills_dict:
            return 0
        
        total_score = sum(
            proficiency_weights.get(prof, 0.5) 
            for prof in skills_dict.values()
        )
        
        max_score = len(skills_dict) * max(proficiency_weights.values())
        return (total_score / max_score * 100) if max_score > 0 else 0
