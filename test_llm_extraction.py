#!/usr/bin/env python3
"""
Quick test script to verify LLM skill extraction is working
Run this to test the semantic skill extractor
"""

import sys
from onboarding_engine import AdaptiveOnboardingEngine

def test_llm_extraction():
    """Test the LLM-enhanced skill extraction"""
    
    print("=" * 70)
    print("ADAPTIVE ONBOARDING ENGINE - LLM EXTRACTION TEST")
    print("=" * 70)
    
    # Initialize engine
    print("\n1. Initializing engine...")
    engine = AdaptiveOnboardingEngine()
    extractor_type = type(engine.skill_extractor).__name__
    print(f"   ✓ Engine initialized")
    print(f"   ✓ Using extractor: {extractor_type}")
    
    # Check if LLM is available
    has_semantic = hasattr(engine.skill_extractor, 'use_semantic_search')
    if has_semantic:
        semantic_enabled = engine.skill_extractor.use_semantic_search
        print(f"   ✓ Semantic search available: {semantic_enabled}")
    
    # Sample test data
    sample_resume = """
    Senior Full-Stack Developer with 8 years of experience.
    
    Technical Skills:
    - Expert in Python, JavaScript, and TypeScript
    - Advanced knowledge of React and Node.js
    - Experienced with Docker, Kubernetes, and AWS
    - Proficient in PostgreSQL, MongoDB, Redis
    - Strong understanding of microservices architecture
    - Familiar with machine learning concepts and TensorFlow
    
    Soft Skills:
    - Team leadership and mentoring
    - Excellent communication skills
    - Project management experience
    - Agile/Scrum methodology
    """
    
    sample_job = """
    Full-Stack Software Engineer
    
    Requirements:
    - 5+ years of Python and JavaScript experience
    - Deep knowledge of React.js and Node.js
    - Experience with cloud platforms (AWS, GCP)
    - Kubernetes and Docker proficiency
    - Database design skills
    - Strong problem-solving abilities
    - Team player with communication skills
    
    Nice to have:
    - Machine learning background
    - GraphQL experience
    - DevOps knowledge
    """
    
    # Run analysis
    print("\n2. Running skill analysis...")
    try:
        analysis = engine.analyze_resume_and_job(
            resume_text=sample_resume,
            job_description=sample_job,
            job_category="ENGINEERING",
            max_weeks=8
        )
        print("   ✓ Analysis completed successfully")
    except Exception as e:
        print(f"   ✗ Analysis failed: {e}")
        return False
    
    # Display results
    print("\n3. RESULTS:")
    print(f"\n   Overall Match Score: {analysis['match_score']:.1f}%")
    
    resume_analysis = analysis['resume_analysis']
    print(f"\n   Your Skills ({resume_analysis['total_unique_skills']} found):")
    for skill, level in list(resume_analysis['skills_with_proficiency'].items())[:10]:
        print(f"      - {skill}: {level}")
    
    gap_analysis = analysis['skill_gap_analysis']
    print(f"\n   Skill Gaps:")
    print(f"      - Critical gaps: {gap_analysis['critical_gaps']}")
    print(f"      - Moderate gaps: {gap_analysis['moderate_gaps']}")
    print(f"      - Minor gaps: {gap_analysis['minor_gaps']}")
    print(f"      - Extra skills: {gap_analysis['extra_skills']}")
    
    # Check reasoning trace
    reasoning = analysis['reasoning_trace']
    print(f"\n   Extraction Method Used:")
    print(f"      {reasoning['extraction_logic']}")
    
    if "semantic" in reasoning['extraction_logic'].lower():
        print("\n   ✓ LLM SEMANTIC EXTRACTION ACTIVE")
    else:
        print("\n   ℹ Using keyword-based extraction")
    
    # Pathway
    pathway = analysis['learning_pathway']
    print(f"\n   Recommended Learning Pathway:")
    print(f"      - Total modules: {pathway['total_modules']}")
    print(f"      - Total hours: {pathway['total_hours']}")
    print(f"      - Difficulty progression: {pathway['difficulty_progression']}")
    
    # Test extraction method
    print("\n4. Testing skill extraction method...")
    
    if has_semantic and semantic_enabled:
        print("   ✓ Semantic LLM extraction is ACTIVE")
        print(f"   ✓ Model: {getattr(engine.skill_extractor, 'model_name', 'N/A')}")
        
        # Test with confidence scores
        if hasattr(engine.skill_extractor, 'extract_with_confidence_scores'):
            skills_dict, metrics = engine.skill_extractor.extract_with_confidence_scores(sample_resume)
            print(f"\n   Extraction Metrics:")
            print(f"      - Total skills: {metrics['total_skills']}")
            print(f"      - Confidence estimate: {metrics['confidence_estimate']:.0%}")
            print(f"      - Method: {metrics['extraction_method']}")
    else:
        print("   ℹ Using keyword-based extraction")
        print("   Note: Install sentence-transformers for LLM support:")
        print("     pip install sentence-transformers")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_llm_extraction()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
