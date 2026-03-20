"""
Skill Gap Analysis and Adaptive Learning Pathway Generation
"""

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math


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
    
    CATEGORY_SKILL_PATHS = {
        'ENGINEERING': {
            'Python': ['Python Basics', 'OOP in Python', 'Data Structures', 'Algorithms'],
            'Java': ['Java Fundamentals', 'Spring Boot', 'Microservices'],
            'Database': ['SQL Basics', 'Database Design', 'Query Optimization'],
            'DevOps': ['Docker', 'Kubernetes', 'CI/CD Pipelines'],
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
            'SQL': ['SQL for Finance', 'Data Analysis in Excel'],
            'Financial Modeling': ['Excel Advanced', 'Financial Analysis', 'Valuation'],
            'Risk Management': ['Credit Risk', 'Operational Risk'],
        },
        'IT': {
            'Cloud': ['AWS Fundamentals', 'Cloud Architecture', 'AWS Advanced'],
            'Networking': ['Network Basics', 'Security', 'Infrastructure'],
            'Linux': ['Linux Fundamentals', 'System Administration', 'Scripting'],
            'Cybersecurity': ['Security Fundamentals', 'Threat Analysis', 'Incident Response'],
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
        'Query Optimization': LearningModule('query_opt', 'Query Optimization & Indexing', 'Database',
                                            DifficultyLevel.ADVANCED, 18, ['Database Design']),
        'Docker': LearningModule('docker', 'Docker Containerization', 'DevOps',
                               DifficultyLevel.INTERMEDIATE, 20),
        'Kubernetes': LearningModule('k8s', 'Kubernetes Orchestration', 'DevOps',
                                    DifficultyLevel.ADVANCED, 30, ['Docker']),
        'CI/CD Pipelines': LearningModule('cicd', 'CI/CD Pipelines & Automation', 'DevOps',
                                         DifficultyLevel.INTERMEDIATE, 25),
        
        # Sales paths
        'Effective Communication': LearningModule('comm', 'Effective Communication', 'Communication',
                                                 DifficultyLevel.BEGINNER, 10),
        'Presentation Skills': LearningModule('present', 'Presentation Skills', 'Communication',
                                             DifficultyLevel.INTERMEDIATE, 12, ['Effective Communication']),
        'Negotiation': LearningModule('nego', 'Advanced Negotiation Techniques', 'Communication',
                                     DifficultyLevel.ADVANCED, 15),
        'Salesforce Basics': LearningModule('sf_basics', 'Salesforce Fundamentals', 'CRM Tools',
                                           DifficultyLevel.BEGINNER, 20),
        'CRM Advanced': LearningModule('crm_adv', 'Advanced CRM Strategies', 'CRM Tools',
                                      DifficultyLevel.ADVANCED, 25, ['Salesforce Basics']),
        'Sales Fundamentals': LearningModule('sales_fund', 'Sales Fundamentals', 'Sales Strategy',
                                            DifficultyLevel.BEGINNER, 15),
        'Territory Management': LearningModule('territory', 'Territory Management', 'Sales Strategy',
                                              DifficultyLevel.INTERMEDIATE, 18, ['Sales Fundamentals']),
        'Deal Closing': LearningModule('closing', 'Advanced Deal Closing', 'Sales Strategy',
                                      DifficultyLevel.ADVANCED, 20, ['Territory Management']),
        
        # HR paths
        'Recruitment Strategies': LearningModule('recruit', 'Modern Recruitment Strategies', 'Recruitment',
                                                DifficultyLevel.INTERMEDIATE, 16),
        'Interview Techniques': LearningModule('interview', 'Effective Interview Techniques', 'Recruitment',
                                              DifficultyLevel.INTERMEDIATE, 12),
        'Onboarding': LearningModule('onboard', 'Employee Onboarding Best Practices', 'Recruitment',
                                    DifficultyLevel.BEGINNER, 10),
        'Conflict Resolution': LearningModule('conflict', 'Conflict Resolution & Mediation', 'Employee Relations',
                                             DifficultyLevel.INTERMEDIATE, 14),
        'Performance Management': LearningModule('perf_mgmt', 'Performance Management Systems', 'Employee Relations',
                                                DifficultyLevel.INTERMEDIATE, 16),
        'Labor Laws': LearningModule('labor', 'Labor Laws & Compliance', 'Compliance',
                                    DifficultyLevel.BEGINNER, 12),
        
        # Finance paths
        'Financial Accounting': LearningModule('fin_acct', 'Financial Accounting Principles', 'Accounting',
                                              DifficultyLevel.INTERMEDIATE, 30),
        'Cost Accounting': LearningModule('cost_acct', 'Cost Accounting & Analysis', 'Accounting',
                                         DifficultyLevel.ADVANCED, 25, ['Financial Accounting']),
        'SQL for Finance': LearningModule('sql_finance', 'SQL for Financial Analysis', 'SQL',
                                         DifficultyLevel.INTERMEDIATE, 20),
        'Excel Advanced': LearningModule('excel', 'Advanced Excel for Finance', 'Financial Modeling',
                                        DifficultyLevel.INTERMEDIATE, 18),
        'Financial Analysis': LearningModule('fin_analysis', 'Financial Analysis & Reporting', 'Financial Modeling',
                                            DifficultyLevel.ADVANCED, 25, ['Excel Advanced']),
        'Credit Risk': LearningModule('credit_risk', 'Credit Risk Management', 'Risk Management',
                                     DifficultyLevel.ADVANCED, 20),
        
        # IT paths
        'AWS Fundamentals': LearningModule('aws_fund', 'AWS Fundamentals', 'Cloud',
                                          DifficultyLevel.BEGINNER, 25),
        'Cloud Architecture': LearningModule('cloud_arch', 'Cloud Architecture Design', 'Cloud',
                                            DifficultyLevel.INTERMEDIATE, 30, ['AWS Fundamentals']),
        'AWS Advanced': LearningModule('aws_adv', 'Advanced AWS Services', 'Cloud',
                                      DifficultyLevel.ADVANCED, 35, ['Cloud Architecture']),
        'Network Basics': LearningModule('network', 'Network Fundamentals', 'Networking',
                                        DifficultyLevel.BEGINNER, 20),
        'Security': LearningModule('sec', 'Network Security', 'Networking',
                                  DifficultyLevel.INTERMEDIATE, 25, ['Network Basics']),
        'Linux Fundamentals': LearningModule('linux', 'Linux Fundamentals', 'Linux',
                                            DifficultyLevel.BEGINNER, 20),
        'System Administration': LearningModule('sysadmin', 'Linux System Administration', 'Linux',
                                               DifficultyLevel.INTERMEDIATE, 25, ['Linux Fundamentals']),
        'Security Fundamentals': LearningModule('cyber_fund', 'Cybersecurity Fundamentals', 'Cybersecurity',
                                               DifficultyLevel.BEGINNER, 20),
        'Threat Analysis': LearningModule('threat', 'Threat Analysis & Detection', 'Cybersecurity',
                                         DifficultyLevel.ADVANCED, 30, ['Security Fundamentals']),
    }


class SkillGapAnalyzer:
    """Analyze skill gaps between current state and target role"""
    
    PROFICIENCY_LEVELS = ['none', 'beginner', 'intermediate', 'expert']
    LEVEL_SCORES = {'none': 0, 'beginner': 1, 'intermediate': 2, 'expert': 3}
    
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
        
        for skill in skills_to_cover:
            if skill in skill_paths:
                modules_for_skill = skill_paths[skill]
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
