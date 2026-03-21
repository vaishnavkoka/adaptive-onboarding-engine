"""
Skill Gap Analysis and Adaptive Learning Pathway Generation
"""

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math
from difflib import SequenceMatcher


class DifficultyLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3


@dataclass
class LearningModule:
    """Represents a single learning module"""
    id: str
    name: str
    skill: str
    difficulty: DifficultyLevel
    duration_hours: float
    prerequisites: List[str] = None
    description: str = ""
    resources_type: str = "online"  # online, course, tutorial, etc.
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class SkillGap:
    """Represents a skill gap between current and target state"""
    skill_name: str
    current_level: str  # 'expert', 'intermediate', 'beginner', 'none'
    target_level: str
    gap_severity: float  # 0-1, where 1 is most severe
    priority: int  # 1-5, where 1 is highest priority


class CourseDatabase:
    """Learning module database based on job categories"""
    
    # Skill aliases for fuzzy matching
    SKILL_ALIASES = {
        'go': 'GoLang',
        'golang': 'GoLang',
        'r': 'R Programming',
        'r programming': 'R Programming',
        'qa': 'Quality Assurance',
        'quality assurance': 'Quality Assurance',
        'qc': 'Quality Assurance',
        'testing': 'Quality Assurance',
        'pytest': 'Quality Assurance',
        'junit': 'Quality Assurance',
        'selenium': 'Quality Assurance',
        'automation': 'Quality Assurance',
        'js': 'JavaScript',
        'javascript': 'JavaScript',
        'ts': 'TypeScript',
        'typescript': 'TypeScript',
        'nodejs': 'Node.js',
        'node.js': 'Node.js',
        'react': 'React',
        'vue': 'Vue.js',
        'angular': 'Angular',
        'c++': 'C++',
        'cplusplus': 'C++',
        'c#': 'C#',
        'csharp': 'C#',
        '.net': '.NET',
        'dotnet': '.NET',
        'sql': 'Database',
        'mysql': 'Database',
        'postgresql': 'Database',
        'mongodb': 'NoSQL Database',
        'nosql': 'NoSQL Database',
        'aws': 'Cloud Computing',
        'azure': 'Cloud Computing',
        'gcp': 'Cloud Computing',
        'docker': 'DevOps',
        'kubernetes': 'DevOps',
        'jenkins': 'DevOps',
        'devops': 'DevOps',
        'ci/cd': 'DevOps',
        'git': 'Version Control',
        'github': 'Version Control',
        'gitlab': 'Version Control',
        'linux': 'Linux',
        'unix': 'Linux',
        'bash': 'Linux',
        'shell': 'Linux',
        'communication': 'Communication',
        'presentation': 'Communication',
        'excel': 'Spreadsheet',
        'spreadsheet': 'Spreadsheet',
        'rest': 'REST API',
        'rest api': 'REST API',
        'soap': 'Web Services',
        'web services': 'Web Services',
        'html': 'Web Development',
        'html5': 'Web Development',
        'css': 'Web Development',
        'css3': 'Web Development',
        'api': 'REST API',
        'api design': 'REST API',
        'architecture': 'Enterprise Architecture',
        'design patterns': 'Design Patterns',
        'mvc': 'Design Patterns',
        'microservices': 'Microservices Architecture',
        'enterprise': 'Enterprise Architecture',
        'enterprise software': 'Enterprise Architecture',
        'iis': 'IIS Administration',
        'microsoft iis': 'IIS Administration',
    }
    
    CATEGORY_SKILL_PATHS = {
        'ENGINEERING': {
            'Python': ['Python Basics', 'OOP in Python', 'Data Structures', 'Algorithms'],
            'Java': ['Java Fundamentals', 'Spring Boot', 'Microservices'],
            'Database': ['SQL Basics', 'Database Design', 'Query Optimization'],
            'DevOps': ['Docker', 'Kubernetes', 'CI/CD Pipelines'],
            'GoLang': ['Go Fundamentals', 'Concurrency in Go', 'Building APIs with Go'],
            'R Programming': ['R Basics', 'Data Analysis with R', 'Statistical Computing'],
            'Quality Assurance': ['Testing Fundamentals', 'Automation Testing', 'Test Design'],
            'JavaScript': ['JavaScript Basics', 'Web Development', 'Async Programming'],
            'TypeScript': ['TypeScript Basics', 'Advanced TypeScript', 'Type Safety'],
            'Node.js': ['Node.js Fundamentals', 'Express Framework', 'Building APIs'],
            'React': ['React Basics', 'Component Design', 'State Management'],
            'Web Development': ['HTML Fundamentals', 'CSS Styling', 'Responsive Design'],
            'C++': ['C++ Fundamentals', 'Advanced C++', 'System Design'],
            '.NET': ['.NET Fundamentals', '.NET Core Development', 'ASP.NET'],
            'C#': ['C# Fundamentals', 'OOP in C#', 'Advanced C#'],
            'REST API': ['API Design Fundamentals', 'REST Architecture', 'API Security'],
            'Web Services': ['SOAP Web Services', 'Service Architecture', 'Web Service Integration'],
            'Design Patterns': ['Creational Patterns', 'Structural Patterns', 'Behavioral Patterns'],
            'Enterprise Architecture': ['Architecture Principles', 'Enterprise Integration', 'System Design'],
            'Microservices Architecture': ['Microservices Fundamentals', 'Service Communication', 'Deployment Patterns'],
            'IIS Administration': ['IIS Basics', 'Site Configuration', 'Performance Tuning'],
            'Cloud Computing': ['Cloud Fundamentals', 'Cloud Architecture', 'Deployment'],
            'Linux': ['Linux Fundamentals', 'System Administration', 'Bash Scripting'],
        },
        'SALES': {
            'Communication': ['Effective Communication', 'Presentation Skills', 'Negotiation'],
            'CRM Tools': ['Salesforce Basics', 'CRM Advanced', 'Data Management'],
            'Sales Strategy': ['Sales Fundamentals', 'Territory Management', 'Deal Closing'],
            'Business Development': ['Market Analysis', 'Customer Relationship Management'],
        },
        'HR': {
            'HRIS': ['HRIS Systems', 'Employee Database Management'],
            'Recruitment': ['Recruitment Strategies', 'Interview Techniques', 'Onboarding'],
            'Employee Relations': ['Conflict Resolution', 'Performance Management'],
            'Compliance': ['Labor Laws', 'Compliance & Safety'],
        },
        'FINANCE': {
            'Accounting': ['Financial Accounting', 'Cost Accounting', 'Consolidation'],
            'Database': ['SQL for Finance', 'Data Analysis in Excel'],
            'Financial Modeling': ['Excel Advanced', 'Financial Analysis', 'Valuation'],
            'Risk Management': ['Credit Risk', 'Operational Risk'],
        },
        'IT': {
            'Cloud Computing': ['AWS Fundamentals', 'Cloud Architecture', 'AWS Advanced'],
            'Networking': ['Network Basics', 'Security', 'Infrastructure'],
            'Linux': ['Linux Fundamentals', 'System Administration', 'Scripting'],
            'Cybersecurity': ['Security Fundamentals', 'Threat Analysis', 'Incident Response'],
            'Database': ['Database Administration', 'Backup & Recovery', 'Performance Tuning'],
            'DevOps': ['Docker Fundamentals', 'Kubernetes', 'CI/CD Implementation'],
        },
        'INFORMATION-TECHNOLOGY': {
            'Cloud Computing': ['AWS Fundamentals', 'Cloud Architecture', 'AWS Advanced'],
            'Networking': ['Network Basics', 'Security', 'Infrastructure'],
            'Linux': ['Linux Fundamentals', 'System Administration', 'Scripting'],
            'Cybersecurity': ['Security Fundamentals', 'Threat Analysis', 'Incident Response'],
            'Database': ['Database Fundamentals', 'Optimization', 'Performance Tuning'],
            'DevOps': ['Docker Fundamentals', 'Kubernetes', 'CI/CD Implementation'],
        }
    }
    
    COURSE_LIBRARY = {
        # Engineering paths
        'Python Basics': LearningModule('py_basics', 'Python Basics', 'Python', 
                                       DifficultyLevel.BEGINNER, 20),
        'OOP in Python': LearningModule('py_oop', 'Object-Oriented Programming', 'Python',
                                       DifficultyLevel.INTERMEDIATE, 15, ['Python Basics']),
        'Data Structures': LearningModule('ds', 'Data Structures', 'Python',
                                         DifficultyLevel.INTERMEDIATE, 25, ['Python Basics']),
        'Algorithms': LearningModule('algo', 'Algorithms & Complexity', 'Python',
                                    DifficultyLevel.ADVANCED, 30, ['Data Structures']),
        'Java Fundamentals': LearningModule('java_fund', 'Java Fundamentals', 'Java',
                                           DifficultyLevel.BEGINNER, 25),
        'Spring Boot': LearningModule('spring', 'Spring Boot Framework', 'Java',
                                     DifficultyLevel.INTERMEDIATE, 30, ['Java Fundamentals']),
        'Microservices': LearningModule('micro', 'Microservices Architecture', 'Java',
                                       DifficultyLevel.ADVANCED, 35, ['Spring Boot']),
        'SQL Basics': LearningModule('sql_basics', 'SQL Fundamentals', 'Database',
                                    DifficultyLevel.BEGINNER, 15),
        'Database Design': LearningModule('db_design', 'Database Design & Normalization', 'Database',
                                         DifficultyLevel.INTERMEDIATE, 20, ['SQL Basics']),
        # New modules for expanded skills
        'Go Fundamentals': LearningModule('go_fund', 'Go Language Fundamentals', 'GoLang',
                                         DifficultyLevel.BEGINNER, 20),
        'Concurrency in Go': LearningModule('go_concurrency', 'Concurrency Patterns in Go', 'GoLang',
                                           DifficultyLevel.INTERMEDIATE, 25, ['Go Fundamentals']),
        'Building APIs with Go': LearningModule('go_api', 'Building REST APIs with Go', 'GoLang',
                                               DifficultyLevel.INTERMEDIATE, 30, ['Go Fundamentals']),
        'R Basics': LearningModule('r_basics', 'R Programming Basics', 'R Programming',
                                  DifficultyLevel.BEGINNER, 18),
        'Data Analysis with R': LearningModule('r_data', 'Data Analysis with R', 'R Programming',
                                              DifficultyLevel.INTERMEDIATE, 25, ['R Basics']),
        'Statistical Computing': LearningModule('r_stats', 'Statistical Computing in R', 'R Programming',
                                               DifficultyLevel.ADVANCED, 30, ['Data Analysis with R']),
        'Testing Fundamentals': LearningModule('qa_fund', 'Testing Fundamentals', 'Quality Assurance',
                                              DifficultyLevel.BEGINNER, 15),
        'Automation Testing': LearningModule('qa_auto', 'Test Automation & Selenium', 'Quality Assurance',
                                            DifficultyLevel.INTERMEDIATE, 25, ['Testing Fundamentals']),
        'Test Design': LearningModule('qa_design', 'Test Case Design & Strategy', 'Quality Assurance',
                                     DifficultyLevel.INTERMEDIATE, 20, ['Testing Fundamentals']),
        'JavaScript Basics': LearningModule('js_basics', 'JavaScript Fundamentals', 'JavaScript',
                                           DifficultyLevel.BEGINNER, 20),
        'Web Development': LearningModule('web_dev', 'Web Development with JavaScript', 'JavaScript',
                                         DifficultyLevel.INTERMEDIATE, 30, ['JavaScript Basics']),
        'Async Programming': LearningModule('async', 'Async & Promises in JavaScript', 'JavaScript',
                                           DifficultyLevel.INTERMEDIATE, 20, ['JavaScript Basics']),
        'Cloud Fundamentals': LearningModule('cloud_fund', 'Cloud Computing Fundamentals', 'Cloud Computing',
                                            DifficultyLevel.BEGINNER, 18),
        'Cloud Architecture': LearningModule('cloud_arch', 'Cloud Architecture Design', 'Cloud Computing',
                                            DifficultyLevel.INTERMEDIATE, 28, ['Cloud Fundamentals']),
        'Linux Fundamentals': LearningModule('linux_fund', 'Linux System Fundamentals', 'Linux',
                                            DifficultyLevel.BEGINNER, 22),
        'System Administration': LearningModule('linux_admin', 'Linux System Administration', 'Linux',
                                               DifficultyLevel.INTERMEDIATE, 25, ['Linux Fundamentals']),
        'Bash Scripting': LearningModule('bash', 'Bash Scripting for Linux', 'Linux',
                                        DifficultyLevel.INTERMEDIATE, 20, ['Linux Fundamentals']),
        'Docker': LearningModule('docker', 'Docker Containerization', 'DevOps',
                                DifficultyLevel.BEGINNER, 20),
        'Kubernetes': LearningModule('k8s', 'Kubernetes Orchestration', 'DevOps',
                                    DifficultyLevel.INTERMEDIATE, 30, ['Docker']),
        'CI/CD Pipelines': LearningModule('cicd', 'CI/CD Pipeline Implementation', 'DevOps',
                                         DifficultyLevel.INTERMEDIATE, 25),
        # Web & API Development
        'HTML Fundamentals': LearningModule('html_basics', 'HTML5 Fundamentals', 'Web Development',
                                           DifficultyLevel.BEGINNER, 15),
        'CSS Styling': LearningModule('css_basics', 'CSS3 Styling & Layout', 'Web Development',
                                     DifficultyLevel.BEGINNER, 18, ['HTML Fundamentals']),
        'Responsive Design': LearningModule('responsive', 'Responsive Web Design', 'Web Development',
                                           DifficultyLevel.INTERMEDIATE, 20, ['CSS Styling']),
        'API Design Fundamentals': LearningModule('api_basics', 'API Design Fundamentals', 'REST API',
                                                DifficultyLevel.BEGINNER, 18),
        'REST Architecture': LearningModule('rest_arch', 'REST API Architecture & Patterns', 'REST API',
                                           DifficultyLevel.INTERMEDIATE, 22, ['API Design Fundamentals']),
        'API Security': LearningModule('api_security', 'API Security & Authentication', 'REST API',
                                      DifficultyLevel.INTERMEDIATE, 20, ['REST Architecture']),
        'SOAP Web Services': LearningModule('soap_ws', 'SOAP Web Services', 'Web Services',
                                           DifficultyLevel.INTERMEDIATE, 25),
        'Service Architecture': LearningModule('service_arch', 'Service-Oriented Architecture', 'Web Services',
                                              DifficultyLevel.INTERMEDIATE, 22, ['SOAP Web Services']),
        'Web Service Integration': LearningModule('ws_integration', 'Web Service Integration Patterns', 'Web Services',
                                                 DifficultyLevel.INTERMEDIATE, 20, ['Service Architecture']),
        # .NET & C#
        '.NET Fundamentals': LearningModule('net_basics', '.NET Framework & Core Fundamentals', '.NET',
                                           DifficultyLevel.BEGINNER, 25),
        '.NET Core Development': LearningModule('net_core', '.NET Core Development', '.NET',
                                               DifficultyLevel.INTERMEDIATE, 28, ['.NET Fundamentals']),
        'ASP.NET': LearningModule('aspnet', 'ASP.NET Web Development', '.NET',
                                 DifficultyLevel.INTERMEDIATE, 30, ['.NET Core Development']),
        'C# Fundamentals': LearningModule('csharp_basics', 'C# Programming Fundamentals', 'C#',
                                         DifficultyLevel.BEGINNER, 20),
        'OOP in C#': LearningModule('csharp_oop', 'Object-Oriented Programming in C#', 'C#',
                                   DifficultyLevel.INTERMEDIATE, 22, ['C# Fundamentals']),
        'Advanced C#': LearningModule('csharp_adv', 'Advanced C# Features & Patterns', 'C#',
                                     DifficultyLevel.ADVANCED, 25, ['OOP in C#']),
        # Enterprise & Architecture
        'Creational Patterns': LearningModule('design_create', 'Creational Design Patterns', 'Design Patterns',
                                             DifficultyLevel.INTERMEDIATE, 18),
        'Structural Patterns': LearningModule('design_struct', 'Structural Design Patterns', 'Design Patterns',
                                             DifficultyLevel.INTERMEDIATE, 18, ['Creational Patterns']),
        'Behavioral Patterns': LearningModule('design_behav', 'Behavioral Design Patterns', 'Design Patterns',
                                             DifficultyLevel.INTERMEDIATE, 18, ['Structural Patterns']),
        'Architecture Principles': LearningModule('arch_principles', 'Software Architecture Principles', 'Enterprise Architecture',
                                                DifficultyLevel.INTERMEDIATE, 22),
        'Enterprise Integration': LearningModule('enterprise_int', 'Enterprise Application Integration', 'Enterprise Architecture',
                                                DifficultyLevel.ADVANCED, 25, ['Architecture Principles']),
        'System Design': LearningModule('system_design', 'System Design & Scalability', 'Enterprise Architecture',
                                       DifficultyLevel.ADVANCED, 28, ['Enterprise Integration']),
        'Microservices Fundamentals': LearningModule('micro_fund', 'Microservices Architecture Fundamentals', 'Microservices Architecture',
                                                    DifficultyLevel.INTERMEDIATE, 24),
        'Service Communication': LearningModule('service_comm', 'Microservices Communication Patterns', 'Microservices Architecture',
                                               DifficultyLevel.INTERMEDIATE, 22, ['Microservices Fundamentals']),
        'Deployment Patterns': LearningModule('deploy_patterns', 'Microservices Deployment & Scaling', 'Microservices Architecture',
                                             DifficultyLevel.ADVANCED, 26, ['Service Communication']),
        'IIS Basics': LearningModule('iis_basics', 'Internet Information Services (IIS) Basics', 'IIS Administration',
                                    DifficultyLevel.BEGINNER, 16),
        'Site Configuration': LearningModule('iis_config', 'IIS Site Configuration & Management', 'IIS Administration',
                                            DifficultyLevel.INTERMEDIATE, 20, ['IIS Basics']),
        'Performance Tuning': LearningModule('iis_perf', 'IIS Performance Tuning & Optimization', 'IIS Administration',
                                            DifficultyLevel.INTERMEDIATE, 22, ['Site Configuration']),
        'Query Optimization': LearningModule('query_opt', 'Database Query Optimization', 'Database',
                                            DifficultyLevel.INTERMEDIATE, 20, ['SQL Basics']),

    }
class SkillGapAnalyzer:
    """Analyze skill gaps between current state and target role"""
    
    PROFICIENCY_LEVELS = ['none', 'mentioned', 'beginner', 'intermediate', 'expert']
    LEVEL_SCORES = {'none': 0, 'mentioned': 0.5, 'beginner': 1, 'intermediate': 2, 'expert': 3}
    
    def identify_gaps(self, current_skills: Dict[str, str], 
                     required_skills: Dict[str, str]) -> List[SkillGap]:
        """
        Identify gaps between current and required skills
        
        Args:
            current_skills: {'skill_name': 'proficiency_level'}
            required_skills: {'skill_name': 'proficiency_level'}
        
        Returns:
            List of SkillGap objects sorted by priority
        """
        gaps = []
        
        for skill, target_level in required_skills.items():
            current_level = current_skills.get(skill, 'none')
            
            target_score = self.LEVEL_SCORES.get(target_level, 0)
            current_score = self.LEVEL_SCORES.get(current_level, 0)
            
            if current_score < target_score:
                gap_severity = (target_score - current_score) / target_score
                gap = SkillGap(
                    skill_name=skill,
                    current_level=current_level,
                    target_level=target_level,
                    gap_severity=gap_severity,
                    priority=1  # Will be set based on importance
                )
                gaps.append(gap)
        
        # Additional gaps: skills candidate has but are not required
        for skill in current_skills:
            if skill not in required_skills:
                gaps.append(SkillGap(
                    skill_name=skill,
                    current_level=current_skills[skill],
                    target_level='not_required',
                    gap_severity=0,
                    priority=5  # Lower priority
                ))
        
        # Sort by gap severity (descending) and required skills first
        gaps.sort(key=lambda x: (-x.gap_severity if x.target_level != 'not_required' else 0, x.priority))
        
        return gaps

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """
        Normalize extracted skill to known skill category
        Uses alias lookup and fuzzy matching
        
        Args:
            skill: Raw skill name from extraction
        
        Returns:
            Normalized skill name or original if no match found
        """
        if not skill:
            return skill
        
        skill_lower = skill.lower().strip()
        
        # Try direct alias lookup first
        if skill_lower in CourseDatabase.SKILL_ALIASES:
            return CourseDatabase.SKILL_ALIASES[skill_lower]
        
        # Try fuzzy matching with known skills
        all_known_skills = set()
        for category_skills in CourseDatabase.CATEGORY_SKILL_PATHS.values():
            all_known_skills.update(category_skills.keys())
        
        best_match = None
        best_ratio = 0.6  # Threshold for match
        
        for known_skill in all_known_skills:
            ratio = SequenceMatcher(None, skill_lower, known_skill.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = known_skill
        
        return best_match if best_match else skill


class AdaptivePathwayGenerator:
    """Generate personalized learning pathways based on skill gaps"""
    
    def __init__(self):
        self.course_db = CourseDatabase()
        self.skill_gap_analyzer = SkillGapAnalyzer()
    
    def generate_pathway(self, skill_gaps: List[SkillGap], 
                        job_category: str, 
                        max_weeks: int = 12) -> Dict:
        """
        Generate an adaptive learning pathway
        
        Args:
            skill_gaps: List of SkillGap objects
            job_category: The target job category
            max_weeks: Maximum weeks available for training
        
        Returns:
            Dictionary with pathway structure and recommendations
        """
        recommended_modules = []
        skills_to_cover = set()
        
        # Identify priority skills from gaps
        for gap in skill_gaps:
            if gap.target_level != 'not_required' and gap.gap_severity > 0:
                skills_to_cover.add(gap.skill_name)
        
        # Get skill learning paths for the category
        if job_category in CourseDatabase.CATEGORY_SKILL_PATHS:
            skill_paths = CourseDatabase.CATEGORY_SKILL_PATHS[job_category]
        else:
            skill_paths = {}
        
        # Build learning sequence
        total_hours = 0
        visited = set()
        
        for raw_skill in skills_to_cover:
            # Normalize the skill to a known category
            normalized_skill = SkillGapAnalyzer.normalize_skill(raw_skill)
            
            if normalized_skill and normalized_skill in skill_paths:
                modules_for_skill = skill_paths[normalized_skill]
                for module_name in modules_for_skill:
                    if module_name not in visited and module_name in CourseDatabase.COURSE_LIBRARY:
                        module = CourseDatabase.COURSE_LIBRARY[module_name]
                        
                        # Check prerequisites
                        if module.prerequisites and not all(p in visited for p in module.prerequisites):
                            continue
                        
                        if total_hours + module.duration_hours <= max_weeks * 40:
                            recommended_modules.append(module)
                            visited.add(module_name)
                            total_hours += module.duration_hours
        
        # Create pathway structure
        pathway = {
            'total_modules': len(recommended_modules),
            'total_hours': total_hours,
            'total_weeks': math.ceil(total_hours / 40),
            'modules': [self._module_to_dict(m) for m in recommended_modules],
            'difficulty_progression': self._calculate_difficulty_progression(recommended_modules),
            'estimated_success_rate': self._estimate_success_rate(recommended_modules, skill_gaps),
        }
        
        return pathway
    
    def _module_to_dict(self, module: LearningModule) -> dict:
        """Convert LearningModule to dictionary"""
        return {
            'id': module.id,
            'name': module.name,
            'skill': module.skill,
            'difficulty': module.difficulty.name,
            'duration_hours': module.duration_hours,
            'prerequisites': module.prerequisites,
            'description': module.description,
            'type': module.resources_type,
        }
    
    def _calculate_difficulty_progression(self, modules: List[LearningModule]) -> str:
        """Analyze difficulty progression of pathway"""
        if not modules:
            return 'no_modules'
        
        difficulties = [m.difficulty.value for m in modules]
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        if avg_difficulty < 1.5:
            return 'beginner_focused'
        elif avg_difficulty < 2.5:
            return 'mixed'
        else:
            return 'advanced_intensive'
    
    def _estimate_success_rate(self, modules: List[LearningModule], 
                              skill_gaps: List[SkillGap]) -> float:
        """Estimate pathway success rate based on gap severity and module difficulty"""
        if not modules or not skill_gaps:
            return 0.75
        
        # Base success rate
        success_rate = 0.85
        
        # Adjust based on gap severity
        avg_gap_severity = sum(g.gap_severity for g in skill_gaps) / len(skill_gaps)
        success_rate -= (avg_gap_severity * 0.15)
        
        # Adjust based on module difficulty
        avg_difficulty = sum(m.difficulty.value for m in modules) / len(modules)
        success_rate -= ((avg_difficulty - 1) * 0.05)
        
        return max(0.5, min(0.95, success_rate))
