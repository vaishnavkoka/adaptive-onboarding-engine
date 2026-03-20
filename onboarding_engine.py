"""
Complete Adaptive Onboarding Engine - Integration Layer
"""

from typing import Dict, List, Tuple
import json
from datetime import datetime
from skill_extractor import SkillExtractor
from adaptive_pathway import SkillGapAnalyzer, AdaptivePathwayGenerator, CourseDatabase


class AdaptiveOnboardingEngine:
    """Main orchestrator for the adaptive onboarding system"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.gap_analyzer = SkillGapAnalyzer()
        self.pathway_generator = AdaptivePathwayGenerator()
    
    def analyze_resume_and_job(self, 
                              resume_text: str,
                              job_description: str,
                              job_category: str = 'IT',
                              max_weeks: int = 12) -> Dict:
        """
        Complete end-to-end analysis: resume → skills → gaps → pathway
        
        Args:
            resume_text: Candidate's resume text
            job_description: Target job description
            job_category: Job category (ENGINEERING, SALES, HR, FINANCE, IT, etc.)
            max_weeks: Maximum weeks for training
        
        Returns:
            Comprehensive analysis dictionary with reasoning trace
        """
        
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'job_category': job_category,
            'max_weeks': max_weeks,
        }
        
        # Step 1: Extract skills from resume
        resume_skills_with_prof = self.skill_extractor.extract_with_proficiency(resume_text)
        resume_technical_skills, resume_soft_skills = self.skill_extractor.extract_skills(resume_text)
        
        analysis_result['resume_analysis'] = {
            'technical_skills': list(resume_technical_skills),
            'soft_skills': list(resume_soft_skills),
            'skills_with_proficiency': resume_skills_with_prof,
            'total_unique_skills': len(resume_technical_skills) + len(resume_soft_skills),
            'skill_score': self.skill_extractor.score_skills(resume_skills_with_prof),
        }
        
        # Step 2: Extract skills from job description
        job_tech_skills, job_soft_skills = self.skill_extractor.extract_skills(job_description)
        job_skills_with_prof = self.skill_extractor.extract_with_proficiency(job_description)
        
        analysis_result['job_description_analysis'] = {
            'required_technical_skills': list(job_tech_skills),
            'required_soft_skills': list(job_soft_skills),
            'skills_with_proficiency': job_skills_with_prof,
            'total_required_skills': len(job_tech_skills) + len(job_soft_skills),
        }
        
        # Step 3: Identify skill gaps
        skill_gaps = self.gap_analyzer.identify_gaps(
            resume_skills_with_prof,
            job_skills_with_prof
        )
        
        gap_analysis = {
            'total_gaps': len([g for g in skill_gaps if g.target_level != 'not_required']),
            'critical_gaps': len([g for g in skill_gaps if g.gap_severity > 0.66 and g.target_level != 'not_required']),
            'moderate_gaps': len([g for g in skill_gaps if 0.33 <= g.gap_severity <= 0.66 and g.target_level != 'not_required']),
            'minor_gaps': len([g for g in skill_gaps if 0 < g.gap_severity < 0.33 and g.target_level != 'not_required']),
            'extra_skills': len([g for g in skill_gaps if g.target_level == 'not_required']),
            'gaps_detail': [self._gap_to_dict(g) for g in skill_gaps[:15]],  # Top 15 gaps
        }
        
        analysis_result['skill_gap_analysis'] = gap_analysis
        
        # Step 4: Generate adaptive pathway
        priority_gaps = [g for g in skill_gaps if g.target_level != 'not_required']
        pathway = self.pathway_generator.generate_pathway(
            priority_gaps,
            job_category,
            max_weeks
        )
        
        analysis_result['learning_pathway'] = pathway
        
        # Step 5: Calculate match percentage
        match_score = self._calculate_match_percentage(analysis_result)
        analysis_result['match_score'] = match_score
        
        # Step 6: Generate recommendations and reasoning
        analysis_result['recommendations'] = self._generate_recommendations(analysis_result)
        analysis_result['reasoning_trace'] = self._generate_reasoning_trace(analysis_result)
        
        return analysis_result
    
    def _gap_to_dict(self, gap) -> dict:
        """Convert SkillGap to dictionary"""
        return {
            'skill': gap.skill_name,
            'current_level': gap.current_level,
            'target_level': gap.target_level,
            'gap_severity': round(gap.gap_severity, 2),
            'priority': gap.priority,
        }
    
    def _calculate_match_percentage(self, analysis: Dict) -> float:
        """Calculate overall match percentage between candidate and job"""
        resume_skills = set(analysis['resume_analysis']['skills_with_proficiency'].keys())
        job_skills = set(analysis['job_description_analysis']['skills_with_proficiency'].keys())
        
        if not job_skills:
            return 0.0
        
        matching_skills = resume_skills & job_skills
        match_score = (len(matching_skills) / len(job_skills)) * 100
        
        # Adjust for proficiency levels
        for skill in matching_skills:
            resume_level = analysis['resume_analysis']['skills_with_proficiency'][skill]
            job_level = analysis['job_description_analysis']['skills_with_proficiency'][skill]
            
            level_scores = {'expert': 3, 'intermediate': 2, 'beginner': 1, 'mentioned': 0}
            if level_scores.get(resume_level, 0) >= level_scores.get(job_level, 0):
                match_score += 5  # Bonus for meeting or exceeding requirement
        
        return min(100, match_score)
    
    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate actionable recommendations"""
        recommendations = {
            'immediate_actions': [],
            'strengths_to_leverage': [],
            'areas_to_develop': [],
            'timeline_estimate': '',
        }
        
        gap_analysis = analysis['skill_gap_analysis']
        pathway = analysis['learning_pathway']
        
        # Immediate actions
        if gap_analysis['critical_gaps'] > 0:
            recommendations['immediate_actions'].append(
                f"Focus on {gap_analysis['critical_gaps']} critical skill gaps: "
                f"{', '.join([g['skill'] for g in gap_analysis['gaps_detail'][:3]])}"
            )
        
        # Strengths
        resume_skills = set(analysis['resume_analysis']['technical_skills'] + 
                           analysis['resume_analysis']['soft_skills'])
        if resume_skills:
            recommendations['strengths_to_leverage'].append(
                f"You have {len(resume_skills)} relevant skills. Leverage these as foundation."
            )
        
        # Areas to develop
        if gap_analysis['total_gaps'] > 0:
            recommendations['areas_to_develop'].append(
                f"Develop {gap_analysis['total_gaps']} skill areas through structured learning"
            )
            recommendations['areas_to_develop'].append(
                f"Recommended pathway: {pathway['total_modules']} modules over {pathway['total_weeks']} weeks"
            )
        
        # Timeline
        recommendations['timeline_estimate'] = (
            f"{pathway['total_weeks']} weeks ({pathway['total_hours']} hours) at 40 hours/week"
        )
        
        return recommendations
    
    def _generate_reasoning_trace(self, analysis: Dict) -> Dict:
        """Generate detailed reasoning for the recommendations"""
        traces = {
            'extraction_logic': "Skills extracted using keyword matching and context analysis",
            'gap_identification_logic': "Gaps identified by comparing required vs current proficiency levels",
            'pathway_generation_logic': "Pathway generated using difficulty-based sequencing with prerequisite tracking",
            'key_decisions': [],
        }
        
        gap_analysis = analysis['skill_gap_analysis']
        pathway = analysis['learning_pathway']
        
        # Key decisions
        if gap_analysis['critical_gaps'] > 0:
            traces['key_decisions'].append(
                f"Prioritized {gap_analysis['critical_gaps']} critical gaps (gap_severity > 0.66) for immediate learning"
            )
        
        if gap_analysis['extra_skills'] > 0:
            traces['key_decisions'].append(
                f"Identified {gap_analysis['extra_skills']} extra skills not required for role"
            )
        
        if pathway['total_hours'] > 480:  # 12 weeks * 40 hours
            traces['key_decisions'].append(
                f"Pathway exceeds recommended timeframe - prioritized highest-severity gaps"
            )
        
        traces['key_decisions'].append(
            f"Selected {pathway['total_modules']} learning modules with {pathway['difficulty_progression']} progression"
        )
        
        traces['key_decisions'].append(
            f"Estimated success rate: {pathway['estimated_success_rate']*100:.1f}% based on gap severity and module difficulty"
        )
        
        return traces
    
    def format_report(self, analysis: Dict) -> str:
        """Generate a formatted text report of the analysis"""
        report = []
        report.append("=" * 80)
        report.append("ADAPTIVE ONBOARDING ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append(f"Target Position Category: {analysis['job_category']}")
        report.append("")
        
        # Overall match
        report.append("OVERALL FIT ASSESSMENT")
        report.append("-" * 80)
        report.append(f"Match Score: {analysis['match_score']:.1f}%")
        report.append("")
        
        # Resume skills
        resume_analysis = analysis['resume_analysis']
        report.append("YOUR CURRENT SKILLS")
        report.append("-" * 80)
        report.append(f"Technical Skills: {', '.join(resume_analysis['technical_skills'][:10])}")
        if len(resume_analysis['technical_skills']) > 10:
            report.append(f"  ... and {len(resume_analysis['technical_skills']) - 10} more")
        report.append(f"Soft Skills: {', '.join(resume_analysis['soft_skills'][:5])}")
        if len(resume_analysis['soft_skills']) > 5:
            report.append(f"  ... and {len(resume_analysis['soft_skills']) - 5} more")
        report.append(f"Overall Skill Score: {resume_analysis['skill_score']:.1f}/100")
        report.append("")
        
        # Required skills
        job_analysis = analysis['job_description_analysis']
        report.append("REQUIRED SKILLS FOR POSITION")
        report.append("-" * 80)
        report.append(f"Technical Skills: {', '.join(job_analysis['required_technical_skills'][:10])}")
        if len(job_analysis['required_technical_skills']) > 10:
            report.append(f"  ... and {len(job_analysis['required_technical_skills']) - 10} more")
        report.append(f"Soft Skills: {', '.join(job_analysis['required_soft_skills'][:5])}")
        if len(job_analysis['required_soft_skills']) > 5:
            report.append(f"  ... and {len(job_analysis['required_soft_skills']) - 5} more")
        report.append("")
        
        # Gap analysis
        gap_analysis = analysis['skill_gap_analysis']
        report.append("SKILL GAP ANALYSIS")
        report.append("-" * 80)
        report.append(f"Total Skill Gaps: {gap_analysis['total_gaps']}")
        report.append(f"  - Critical (gap > 67%): {gap_analysis['critical_gaps']}")
        report.append(f"  - Moderate (33-67%): {gap_analysis['moderate_gaps']}")
        report.append(f"  - Minor (< 33%): {gap_analysis['minor_gaps']}")
        report.append(f"Extra Skills (not required): {gap_analysis['extra_skills']}")
        report.append("")
        
        report.append("Top Skill Gaps to Address:")
        for i, gap in enumerate(gap_analysis['gaps_detail'][:5], 1):
            report.append(f"  {i}. {gap['skill']}")
            report.append(f"     Current: {gap['current_level']} → Required: {gap['target_level']}")
            report.append(f"     Gap Severity: {gap['gap_severity']*100:.0f}%")
        report.append("")
        
        # Learning pathway
        pathway = analysis['learning_pathway']
        report.append("PERSONALIZED LEARNING PATHWAY")
        report.append("-" * 80)
        report.append(f"Total Modules: {pathway['total_modules']}")
        report.append(f"Total Hours: {pathway['total_hours']}")
        report.append(f"Estimated Duration: {pathway['total_weeks']} weeks @ 40 hrs/week")
        report.append(f"Difficulty Progression: {pathway['difficulty_progression']}")
        report.append(f"Estimated Success Rate: {pathway['estimated_success_rate']*100:.1f}%")
        report.append("")
        
        report.append("Recommended Learning Modules:")
        for i, module in enumerate(pathway['modules'][:10], 1):
            report.append(f"  {i}. {module['name']}")
            report.append(f"     Duration: {module['duration_hours']} hours ({module['difficulty']})")
            if module['prerequisites']:
                report.append(f"     Prerequisites: {', '.join(module['prerequisites'])}")
        if len(pathway['modules']) > 10:
            report.append(f"  ... and {len(pathway['modules']) - 10} more modules")
        report.append("")
        
        # Recommendations
        recommendations = analysis['recommendations']
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        for action in recommendations['immediate_actions']:
            report.append(f"→ {action}")
        report.append("")
        report.append("Strengths to Leverage:")
        for strength in recommendations['strengths_to_leverage']:
            report.append(f"  ✓ {strength}")
        report.append("")
        report.append("Areas to Develop:")
        for area in recommendations['areas_to_develop']:
            report.append(f"  • {area}")
        report.append("")
        report.append(f"Training Timeline: {recommendations['timeline_estimate']}")
        report.append("")
        
        # Reasoning trace
        traces = analysis['reasoning_trace']
        report.append("REASONING TRACE")
        report.append("-" * 80)
        report.append(f"Extraction Logic: {traces['extraction_logic']}")
        report.append(f"Gap Identification: {traces['gap_identification_logic']}")
        report.append(f"Pathway Generation: {traces['pathway_generation_logic']}")
        report.append("")
        report.append("Key Decisions Made:")
        for decision in traces['key_decisions']:
            report.append(f"  • {decision}")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# Example usage and testing
if __name__ == "__main__":
    # Create test data
    sample_resume = """
    Full Stack Developer with 5 years experience. Expert in Python, Java, and JavaScript.
    Strong background in React and Spring Boot. Intermediate SQL and Docker knowledge.
    Proficient in AWS cloud services. Excellent communication and team leadership skills.
    """
    
    sample_job = """
    Senior Software Engineer - We are looking for an experienced engineer with:
    - Expert level Java and Spring Boot
    - Advanced Kubernetes and Docker experience
    - Intermediate to Advanced Python
    - Microservices architecture experience
    - CI/CD pipeline experience
    - Strong communication and team collaboration skills
    """
    
    # Run analysis
    engine = AdaptiveOnboardingEngine()
    analysis = engine.analyze_resume_and_job(
        sample_resume,
        sample_job,
        job_category='ENGINEERING',
        max_weeks=12
    )
    
    # Print report
    report = engine.format_report(analysis)
    print(report)
    
    # Print JSON for API usage
    print("\n\nJSON OUTPUT FOR API:")
    print(json.dumps(analysis, indent=2, default=str))
