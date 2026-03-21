#!/usr/bin/env python3
"""
Validation: Measure actual skill extraction performance against gold standard
"""

import sys
import json

sys.path.insert(0, '/home/vaishnavkoka/RE4BDD/AI-Adaptive Onboarding Engine')

from skill_extractor import SkillExtractor

# ============================================================================
# GOLD STANDARD TEST CASES (Manually Verified)
# ============================================================================

TEST_CASES = [
    {
        'id': 'test_1_fullstack',
        'resume': """Senior Full-Stack Developer with 8 years of experience.
Expert in Python and JavaScript. Advanced React knowledge.
Strong AWS and Docker experience. Familiar with Kubernetes.
SQL and MongoDB expertise. Good communication and leadership skills.
Experience with Node.js, REST APIs, and microservices architecture.
Proficient in Git, CI/CD pipelines, and agile methodologies.""",
        'expected': {'python', 'javascript', 'react', 'aws', 'docker', 'kubernetes', 
                    'sql', 'mongodb', 'node.js', 'rest', 'git', 'communication', 'leadership'}
    },
    {
        'id': 'test_2_finance',
        'resume': """Financial Analyst with 5 years in investment banking.
Expert Excel user with advanced VBA skills.
Strong SQL and Python for data analysis.
Experience with Tableau and Power BI for financial reporting.
Excellent attention to detail and analytical mindset.
Knowledge of financial modeling, forecasting, and budgeting.
Familiar with SAP and Bloomberg terminals.""",
        'expected': {'excel', 'vba', 'sql', 'python', 'tableau', 'power bi', 
                    'data analysis', 'attention to detail', 'analytical'}
    },
    {
        'id': 'test_3_sales',
        'resume': """Sales Executive with 10 years B2B sales experience.
Proficient in Salesforce CRM platform and lead management.
Strong presentation and negotiation skills.
Excellent communication and leadership abilities.
Built and managed sales teams of 20+ people.
Experience with pipeline forecasting and revenue targets.
Track record of exceeding quotas and closing multi-million dollar deals.""",
        'expected': {'salesforce', 'crm', 'negotiation', 'communication', 'leadership', 
                    'presentation', 'sales', 'teamwork'}
    },
    {
        'id': 'test_4_engineer',
        'resume': """Software Engineer specialized in embedded systems.
Expert in C++ and Java programming languages.
Strong MATLAB and Simulink experience for signal processing.
Proficient in Linux kernel development and drivers.
Experience with microcontroller programming (ARM, AVR).
Working knowledge of hardware-software integration.
Excellent problem-solving and debugging skills.
Familiar with testing, documentation, and Git version control.""",
        'expected': {'c++', 'java', 'matlab', 'linux', 'microcontroller', 
                    'problem-solving', 'testing', 'git'}
    },
    {
        'id': 'test_5_healthcare',
        'resume': """Registered Nurse (RN) with 7 years clinical experience.
Expertise in patient care, assessment, and care planning.
Proficient with EHR systems and electronic medical records.
Strong empathy and excellent communication with patients and families.
Experience in ICU, emergency care, and surgical settings.
Skilled in vital monitoring, medications, and patient education.
Knowledge of infection control and patient safety protocols.
Strong teamwork and collaboration with multidisciplinary healthcare teams.""",
        'expected': {'nursing', 'patient care', 'ehr', 'clinical', 'empathy', 
                    'communication', 'teamwork', 'assessment'}
    },
    {
        'id': 'test_6_consultant',
        'resume': """Management Consultant with 6 years strategy experience.
Strong data analysis and Excel skills for business intelligence.
Experience with SQL databases and data visualization.
Proficient in PowerPoint for executive presentations.
Excellent analytical and problem-solving capabilities.
Background in business strategy, process improvement, and digital transformation.
Research skills and industry analysis expertise.
Strong communication with C-level executives.""",
        'expected': {'data analysis', 'excel', 'sql', 'powerpoint', 'analytical',
                    'problem-solving', 'business', 'research', 'communication'}
    },
    {
        'id': 'test_7_minimalist',
        'resume': """Developer. Python. JavaScript. React. AWS. Docker. 5 years experience.""",
        'expected': {'python', 'javascript', 'react', 'aws', 'docker'}
    }
]

# Skill normalization
SKILL_ALIASES = {
    'nodejs': 'node.js',
    'node js': 'node.js',
    'express': 'node.js',
    'reactjs': 'react',
    'react js': 'react',
    'angularjs': 'angular',
    'docker': 'docker',
    'kubernetes': 'kubernetes',
    'k8s': 'kubernetes',
    'ml': 'machine learning',
    'ai': 'artificial intelligence',
    'dl': 'deep learning',
    'crm': 'crm',
    'powerbi': 'power bi',
    'sap': 'sap',
}

def normalize_skill(skill):
    """Normalize skill for comparison"""
    s = skill.lower().strip()
    return SKILL_ALIASES.get(s, s)

def calculate_metrics(predicted, expected):
    """Calculate precision, recall, F1, accuracy"""
    predicted = {normalize_skill(s) for s in predicted}
    expected = {normalize_skill(s) for s in expected}
    
    tp = len(predicted & expected)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = tp / len(expected) if len(expected) > 0 else 0.0
    
    return {
        'tp': tp, 'fp': fp, 'fn': fn,
        'precision': precision, 'recall': recall, 
        'f1': f1, 'accuracy': accuracy,
        'predicted': predicted, 'expected': expected,
        'missed': expected - predicted,
        'extra': predicted - expected
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*90)
    print("ADAPTIVE ONBOARDING ENGINE - METRICS VALIDATION WITH GOLD STANDARD")
    print("="*90)
    
    print(f"\n✓ Testing with {len(TEST_CASES)} gold standard test cases")
    
    extractor = SkillExtractor()
    
    results = []
    keyword_metrics_list = []
    
    print("\n" + "-"*90)
    print("EXTRACTING SKILLS (KEYWORD-ONLY METHOD)")
    print("-"*90)
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['id']}")
        
        tech_skills, soft_skills = extractor.extract_skills(test['resume'])
        extracted = tech_skills.union(soft_skills)
        
        metrics = calculate_metrics(extracted, test['expected'])
        keyword_metrics_list.append(metrics)
        
        print(f"  Expected: {sorted(test['expected'])}")
        print(f"  Extracted: {sorted(metrics['predicted'])}")
        print(f"  ✓ Accuracy: {metrics['accuracy']:.1%}, Precision: {metrics['precision']:.1%}, "
              f"Recall: {metrics['recall']:.1%}, F1: {metrics['f1']:.1%}")
        
        if metrics['missed']:
            print(f"  ⚠ Missed: {sorted(metrics['missed'])}")
        if metrics['extra']:
            print(f"  ℹ Extra: {sorted(metrics['extra'])}")
        
        results.append({
            'test_id': test['id'],
            'expected_count': len(test['expected']),
            'extracted_count': len(extracted),
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1']
        })
    
    # ========================================================================
    # AGGREGATE RESULTS
    # ========================================================================
    
    print("\n" + "="*90)
    print("AGGREGATE METRICS - KEYWORD-ONLY METHOD")
    print("="*90)
    
    avg_accuracy = sum(m['accuracy'] for m in keyword_metrics_list) / len(keyword_metrics_list)
    avg_precision = sum(m['precision'] for m in keyword_metrics_list) / len(keyword_metrics_list)
    avg_recall = sum(m['recall'] for m in keyword_metrics_list) / len(keyword_metrics_list)
    avg_f1 = sum(m['f1'] for m in keyword_metrics_list) / len(keyword_metrics_list)
    
    print(f"\nKeyword-Only Performance (averaged over {len(TEST_CASES)} tests):")
    print(f"  📊 Accuracy:  {avg_accuracy:.1%}")
    print(f"  📊 Precision: {avg_precision:.1%}")
    print(f"  📊 Recall:    {avg_recall:.1%}")
    print(f"  📊 F1-Score:  {avg_f1:.1%}")
    
    # ========================================================================
    # TEST SEMANTIC LLM (if available)
    # ========================================================================
    
    print("\n" + "-"*90)
    print("TESTING SEMANTIC LLM EXTRACTION")
    print("-"*90)
    
    try:
        from lightweight_llm_extractor_v2 import LightweightLLMExtractor
        
        llm_extractor = LightweightLLMExtractor()
        llm_metrics_list = []
        
        print("\n✓ LLM extractor available - testing semantic method...\n")
        
        for i, test in enumerate(TEST_CASES, 1):
            print(f"[{i}/{len(TEST_CASES)}] {test['id']} (LLM)")
            
            try:
                skills_dict, metrics_dict = llm_extractor.extract_with_confidence_scores(test['resume'])
                extracted = set(skills_dict.keys())
                
                metrics = calculate_metrics(extracted, test['expected'])
                llm_metrics_list.append(metrics)
                
                print(f"  Extracted: {sorted(metrics['predicted'])}")
                print(f"  ✓ Accuracy: {metrics['accuracy']:.1%}, Precision: {metrics['precision']:.1%}, "
                      f"Recall: {metrics['recall']:.1%}, F1: {metrics['f1']:.1%}")
                
                if metrics['missed']:
                    print(f"  ⚠ Missed: {sorted(metrics['missed'])}")
                
            except Exception as e:
                print(f"  ✗ LLM extraction failed: {e}")
        
        if llm_metrics_list:
            print("\n" + "="*90)
            print("AGGREGATE METRICS - SEMANTIC LLM METHOD")
            print("="*90)
            
            llm_accuracy = sum(m['accuracy'] for m in llm_metrics_list) / len(llm_metrics_list)
            llm_precision = sum(m['precision'] for m in llm_metrics_list) / len(llm_metrics_list)
            llm_recall = sum(m['recall'] for m in llm_metrics_list) / len(llm_metrics_list)
            llm_f1 = sum(m['f1'] for m in llm_metrics_list) / len(llm_metrics_list)
            
            print(f"\nSemantic LLM Performance (averaged over {len(TEST_CASES)} tests):")
            print(f"  📊 Accuracy:  {llm_accuracy:.1%}")
            print(f"  📊 Precision: {llm_precision:.1%}")
            print(f"  📊 Recall:    {llm_recall:.1%}")
            print(f"  📊 F1-Score:  {llm_f1:.1%}")
            
            # ========================================================================
            # COMPARISON
            # ========================================================================
            
            print("\n" + "="*90)
            print("COMPARISON: SEMANTIC LLM vs KEYWORD-ONLY")
            print("="*90)
            
            print(f"\n{'Metric':<15} {'Keyword-Only':<20} {'Semantic LLM':<20} {'Improvement':<20}")
            print("-" * 75)
            
            metrics_comparison = [
                ('Accuracy', avg_accuracy, llm_accuracy),
                ('Precision', avg_precision, llm_precision),
                ('Recall', avg_recall, llm_recall),
                ('F1-Score', avg_f1, llm_f1),
            ]
            
            for metric_name, keyword_val, llm_val in metrics_comparison:
                improvement_pct = ((llm_val - keyword_val) / keyword_val * 100) if keyword_val > 0 else 0
                improvement_pts = (llm_val - keyword_val) * 100
                print(f"{metric_name:<15} {keyword_val:>6.1%}           {llm_val:>6.1%}           "
                      f"{improvement_pct:+.1f}% ({improvement_pts:+.1f} pts)")
    
    except ImportError:
        print("\n⚠ LLM extractor not available - install sentence-transformers to test:")
        print("  pip install sentence-transformers")
    
    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    
    output_file = "/home/vaishnavkoka/RE4BDD/AI-Adaptive Onboarding Engine/VALIDATION_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump({
            'test_count': len(TEST_CASES),
            'keyword_only': {
                'average_accuracy': avg_accuracy,
                'average_precision': avg_precision,
                'average_recall': avg_recall,
                'average_f1': avg_f1
            },
            'test_results': results
        }, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    
    print("\n" + "="*90)
    print("✓ VALIDATION COMPLETE")
    print("="*90 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
