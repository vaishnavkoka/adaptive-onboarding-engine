#!/usr/bin/env python3
"""Quick test to verify the fixes work"""

import sys
import json
from onboarding_engine import AdaptiveOnboardingEngine

print("Testing AdaptiveOnboardingEngine...")

engine = AdaptiveOnboardingEngine()

# Simple test case
resume = "Python developer with Django and React experience"
job = "Senior Python Engineer needed for backend work"

try:
    result = engine.analyze_resume_and_job(resume, job, "ENGINEERING", 12)
    
    # Check all required fields
    required_fields = ['match_score', 'score_breakdown', 'learning_pathway', 'recommendations']
    
    missing = []
    for field in required_fields:
        if field not in result:
            missing.append(field)
    
    if missing:
        print(f"❌ Missing fields: {missing}")
        sys.exit(1)
    
    print(f"✅ match_score: {result['match_score']}")
    print(f"✅ Interpretation: {result['score_breakdown']['interpretation']}")
    print(f"✅ Learning pathway modules: {result['learning_pathway']['total_modules']}")
    print(f"✅ Test PASSED - All fields present and valid")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Test FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
