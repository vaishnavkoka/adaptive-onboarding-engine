"""
Complete Adaptive Onboarding Engine - Integration Layer
Enhanced with LLM-based skill extraction
"""

from typing import Dict, List, Tuple
import json
from datetime import datetime
from adaptive_pathway import SkillGapAnalyzer, AdaptivePathwayGenerator, CourseDatabase

# Try to use Ollama LLM extractor first, then fall back to base if unavailable
try:
    from ollama_skill_extractor import OllamaSkillExtractor
    skill_extractor_instance = OllamaSkillExtractor(model="deepseek-r1:7b")
except ImportError:
    try:
        from lightweight_llm_extractor_v2 import get_llm_extractor
        skill_extractor_instance = get_llm_extractor()
    except ImportError:
        try:
            from lightweight_llm_extractor import get_llm_extractor
            skill_extractor_instance = get_llm_extractor()
        except ImportError:
            from skill_extractor import SkillExtractor
            skill_extractor_instance = SkillExtractor()


class AdaptiveOnboardingEngine:
    """Main orchestrator for the adaptive onboarding system"""
    
    def __init__(self):
        # Use LLM-enhanced or fallback to basic skill extractor
        global skill_extractor_instance
        self.skill_extractor = skill_extractor_instance
        self.gap_analyzer = SkillGapAnalyzer()
        self.pathway_generator = AdaptivePathwayGenerator()
    
    def _extract_skills_with_llm(self, text: str) -> Dict[str, str]:
        """
        Extract skills using LLM if available, else use standard method
        
        Args:
            text: Input text to extract skills from
        
        Returns:
            Dictionary mapping skill names to proficiency levels
        """
        # Try semantic extraction first if available
        if hasattr(self.skill_extractor, 'extract_skills_semantic'):
            try:
                return self.skill_extractor.extract_skills_semantic(text)
            except Exception as e:
                print(f"LLM semantic extraction failed: {e}. Falling back to standard extraction.")
                return self.skill_extractor.extract_with_proficiency(text)
        
        # Fall back to standard extraction
        return self.skill_extractor.extract_with_proficiency(text)
    
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
        
        # Step 1: Extract skills from resume (using LLM if available)
        resume_skills_with_prof = self._extract_skills_with_llm(resume_text)
        resume_technical_skills, resume_soft_skills = self.skill_extractor.extract_skills(resume_text)
        
        analysis_result['resume_analysis'] = {
            'technical_skills': list(resume_technical_skills),
            'soft_skills': list(resume_soft_skills),
            'skills_with_proficiency': resume_skills_with_prof,
            'total_unique_skills': len(resume_technical_skills) + len(resume_soft_skills),
            'skill_score': self.skill_extractor.score_skills(resume_skills_with_prof),
        }
        
        # Step 2: Extract skills from job description (using LLM if available)
        job_tech_skills, job_soft_skills = self.skill_extractor.extract_skills(job_description)
        job_skills_with_prof = self._extract_skills_with_llm(job_description)
        
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
        score_breakdown = self._calculate_score_breakdown(analysis_result, match_score)
        analysis_result['score_breakdown'] = score_breakdown
        
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
            return 50.0  # Default if job skills not detected
        
        # Calculate base match percentage
        matching_skills = resume_skills & job_skills
        base_match = (len(matching_skills) / len(job_skills)) * 100
        
        # Calculate proficiency bonus
        proficiency_bonus = 0
        level_scores = {'expert': 3, 'intermediate': 2, 'beginner': 1, 'mentioned': 0.5}
        
        for skill in matching_skills:
            resume_level = analysis['resume_analysis']['skills_with_proficiency'].get(skill, 'mentioned')
            job_level = analysis['job_description_analysis']['skills_with_proficiency'].get(skill, 'mentioned')
            
            resume_score = level_scores.get(resume_level, 0.5)
            job_score = level_scores.get(job_level, 0.5)
            
            # If resume proficiency meets or exceeds job requirement, add bonus
            if resume_score >= job_score:
                proficiency_bonus += 3
        
        # Final score: base match + proficiency bonus (capped at 100)
        # If they have 0% match, they still get points for any detected skills
        if len(matching_skills) == 0 and len(resume_skills) > 0:
            base_match = min(20, len(resume_skills) * 2)  # Credit for having skills, even if not exact match
        
        final_score = min(100, base_match + proficiency_bonus)
        
        # Ensure minimum 10 points if any resume skills are detected
        if len(resume_skills) > 0 and final_score < 10:
            final_score = 10
        
        return round(final_score, 1)
    
    def _calculate_score_breakdown(self, analysis: Dict, match_score: float) -> Dict:
        """Generate detailed breakdown of how the score was calculated"""
        resume_skills = set(analysis['resume_analysis']['skills_with_proficiency'].keys())
        job_skills = set(analysis['job_description_analysis']['skills_with_proficiency'].keys())
        matching_skills = resume_skills & job_skills
        
        level_scores = {'expert': 3, 'intermediate': 2, 'beginner': 1, 'mentioned': 0.5}
        proficiency_matches = 0
        
        for skill in matching_skills:
            resume_level = analysis['resume_analysis']['skills_with_proficiency'].get(skill, 'mentioned')
            job_level = analysis['job_description_analysis']['skills_with_proficiency'].get(skill, 'mentioned')
            resume_score = level_scores.get(resume_level, 0.5)
            job_score = level_scores.get(job_level, 0.5)
            
            if resume_score >= job_score:
                proficiency_matches += 1
        
        base_percentage = (len(matching_skills) / len(job_skills) * 100) if job_skills else 0
        
        return {
            'description': f'Your matching score based on skill overlap and proficiency levels',
            'your_skills': len(resume_skills),
            'required_skills': len(job_skills),
            'matching_skills': len(matching_skills),
            'matching_percentage': f"{base_percentage:.1f}%",
            'proficiency_matches': proficiency_matches,
            'scoring_factors': [
                f"✓ You have {len(matching_skills)} matching skills out of {len(job_skills)} required ({base_percentage:.0f}%)",
                f"✓ Your proficiency matches job requirement for {proficiency_matches} skills",
                f"✓ You have {len(resume_skills) - len(matching_skills)} additional skills (bonus!)",
                f"→ Score = Base match ({base_percentage:.0f}%) + Proficiency bonus ({proficiency_matches * 3}pts) = Your Score"
            ],
            'interpretation': self._score_interpretation(match_score)
        }
    
    def _score_interpretation(self, score: float) -> str:
        """Provide interpretation of match score"""
        if score >= 80:
            return "🟢 Excellent match! You meet most required skills. Minor learning needed."
        elif score >= 60:
            return "🟡 Strong match! You have relevant experience. Some skill development recommended."
        elif score >= 40:
            return "🟠 Moderate match. You have foundational skills. Structured learning pathway recommended."
        elif score >= 20:
            return "🔴 Entry-level match. Significant skill development needed. Comprehensive training program provided."
        else:
            return "⚠️  Early career match. Career transition possible with dedicated learning. Custom pathway available."
    
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
        
        # Determine extraction method used
        extraction_method = "keyword matching and context analysis"
        if hasattr(self.skill_extractor, 'use_semantic_search'):
            if self.skill_extractor.use_semantic_search:
                extraction_method = "semantic similarity-based extraction using sentence-transformers"
        elif hasattr(self.skill_extractor, 'use_llm'):
            if self.skill_extractor.use_llm:
                extraction_method = "zero-shot classification using transformer models"
        
        traces = {
            'extraction_logic': f"Skills extracted using {extraction_method} with proficiency level inference",
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
