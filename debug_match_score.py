#!/usr/bin/env python3
"""
Debug tool to understand why your match score is low.
Shows exactly what skills are extracted from resume and job description.
"""

import sys
import json
from onboarding_engine import AdaptiveOnboardingEngine

def debug_match_analysis(resume_text, job_description_text, category="ENGINEERING"):
    """Debug match score calculation"""
    
    engine = AdaptiveOnboardingEngine()
    result = engine.analyze_resume_and_job(resume_text, job_description_text, category, 12)
    
    print("\n" + "="*70)
    print("MATCH SCORE ANALYSIS - DEBUG REPORT")
    print("="*70)
    
    # Extract skills
    resume_skills = set(result['resume_analysis']['skills_with_proficiency'].keys())
    job_skills = set(result['job_description_analysis']['skills_with_proficiency'].keys())
    matching = resume_skills & job_skills
    missing = job_skills - resume_skills
    extra = resume_skills - job_skills
    
    print(f"\n📋 RESUME SKILLS ({len(resume_skills)} detected):")
    for skill, level in sorted(result['resume_analysis']['skills_with_proficiency'].items()):
        status = "✓" if skill in job_skills else " "
        print(f"  [{status}] {skill}: {level}")
    
    print(f"\n🎯 JOB SKILLS ({len(job_skills)} required):")
    for skill, level in sorted(result['job_description_analysis']['skills_with_proficiency'].items()):
        in_resume = skill in resume_skills
        status = "✓" if in_resume else "✗"
        print(f"  [{status}] {skill}: {level}")
    
    print(f"\n📊 SKILL MATCHING SUMMARY:")
    print(f"  Matching skills:  {len(matching)} of {len(job_skills)} ({(len(matching)/len(job_skills)*100):.0f}%)")
    print(f"  Missing from resume: {len(missing)}")
    if missing:
        for skill in sorted(missing):
            print(f"    ✗ {skill}")
    if extra:
        print(f"\n  Extra skills (not required): {len(extra)}")
        for skill in sorted(extra):
            print(f"    + {skill}")
    
    print(f"\n🎯 PROFICIENCY MATCHING:")
    proficiency_matches = 0
    for skill in matching:
        resume_level = result['resume_analysis']['skills_with_proficiency'].get(skill)
        job_level = result['job_description_analysis']['skills_with_proficiency'].get(skill)
        level_scores = {'expert': 3, 'intermediate': 2, 'beginner': 1, 'mentioned': 0.5}
        if level_scores.get(resume_level, 0) >= level_scores.get(job_level, 0):
            print(f"  ✓ {skill}: {resume_level} >= {job_level}")
            proficiency_matches += 1
        else:
            print(f"  ~ {skill}: {resume_level} < {job_level}")
    
    print(f"\n✨ FINAL SCORE: {result['match_score']}/100")
    print(f"   Interpretation: {result['score_breakdown']['interpretation']}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if len(missing) > 0:
        print(f"   Learn these {len(missing)} critical missing skills:")
        for skill in sorted(missing)[:5]:
            print(f"     - {skill}")
        if len(missing) > 5:
            print(f"     ... and {len(missing)-5} more")
    
    print("\n" + "="*70)
    return result

if __name__ == "__main__":
    # Example: replace with your actual resume and job description
    sample_resume = """
    YOUR RESUME TEXT HERE
    (replace with your actual resume content)
    """
    
    sample_job = """
    YOUR JOB DESCRIPTION HERE
    (replace with your actual job description)
    """
    
    if "YOUR RESUME TEXT HERE" in sample_resume:
        print("❌ Please edit this script and replace sample resume/job with your actual content")
        print("\nUsage:")
        print("  python3 debug_match_score.py")
        print("\nOR from Python:")
        print("  from debug_match_score import debug_match_analysis")
        print("  debug_match_analysis(your_resume, your_job_desc)")
        sys.exit(1)
    
    debug_match_analysis(sample_resume, sample_job)
