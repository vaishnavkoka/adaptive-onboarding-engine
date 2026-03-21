"""
LLM Skill Extraction - Quick Validation (Focused)
Tests 3 critical cases to show Ollama/LLM improvement
"""

import requests
import json
from typing import Dict
from skill_extractor import SkillExtractor
from ollama_skill_extractor import OllamaSkillExtractor


# Gold standard test cases (3 critical ones)
FOCUSED_TESTS = [
    {
        "name": "Finance Analyst (Most Challenging)",
        "text": """
        Financial Analyst with 6 years in investment banking.
        Technical Skills: Excel (advanced), VBA, SQL, Tableau, Power BI
        Financial: Corporate Finance, Valuation, M&A, Risk Analysis
        Tools: Bloomberg Terminal, FactSet, SAP, Salesforce
        Programming: Python, R for statistical analysis
        """,
        "expected": {
            "excel", "vba", "sql", "tableau", "power bi",
            "corporate finance", "valuation", "m&a", "risk analysis",
            "python", "r", "bloomberg", "factset", "sap", "salesforce"
        }
    },
    {
        "name": "Embedded Systems Engineer (Technical Challenge)",
        "text": """
        Embedded Systems Engineer specializing in IoT and Microcontrollers.
        Microcontrollers: Arduino, STM32, ESP32, ARM Cortex-M
        Languages: C, C++, Assembly, Python
        Protocols: UART, I2C, SPI, CAN, Bluetooth, WiFi
        Tools: KEIL uVision, GDB Debugger, Logic Analyzer
        Real-time OS: FreeRTOS, RTOS basics
        """,
        "expected": {
            "arduino", "stm32", "esp32", "arm cortex",
            "c", "c++", "assembly", "python",
            "uart", "i2c", "spi", "can", "bluetooth", "wifi",
            "freertos", "rtos", "keil", "gdb"
        }
    },
    {
        "name": "Healthcare IT (Domain Terminology)",
        "text": """
        Healthcare IT Specialist with clinical informatics background.
        EHR Systems: Epic, Cerner, Allscripts, HL7/FHIR
        Clinical: EMR workflows, Clinical Decision Support, Patient Data Management
        Compliance: HIPAA, GDPR, SOC 2 certification
        Technical: SQL Server, BI tools, healthcare analytics
        Skills: Clinical workflows, Data governance, Interoperability
        """,
        "expected": {
            "epic", "cerner", "allscripts", "hl7", "fhir",
            "emr", "ehr", "hipaa", "gdpr",
            "sql server", "healthcare analytics", "data governance",
            "clinical workflows", "patient data", "interoperability"
        }
    }
]


def calculate_metrics(extracted, expected):
    """Calculate accuracy metrics"""
    extracted_lower = {s.lower().strip() for s in extracted}
    expected_lower = {s.lower().strip() for s in expected}
    
    tp = len(extracted_lower & expected_lower)
    fp = len(extracted_lower - expected_lower)
    fn = len(expected_lower - extracted_lower)
    
    accuracy = tp / len(expected_lower) if len(expected_lower) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "extracted_lower": extracted_lower,
        "expected_lower": expected_lower
    }


print("\n" + "="*80)
print("LLM VALIDATION - FOCUSED TEST (3 Critical Cases)")
print("="*80)

# Phase 1: Keyword-only baseline
print("\n📊 PHASE 1: KEYWORD-ONLY BASELINE")
print("-" * 80)

keyword_extractor = SkillExtractor()
keyword_results = []
keyword_accuracies = []

for i, test in enumerate(FOCUSED_TESTS, 1):
    skills_dict = keyword_extractor.extract_with_proficiency(test["text"])
    extracted = set(skills_dict.keys())
    metrics = calculate_metrics(extracted, test["expected"])
    keyword_results.append((test["name"], metrics))
    keyword_accuracies.append(metrics["accuracy"])
    
    acc_pct = metrics["accuracy"] * 100
    status = "✅" if acc_pct >= 70 else "⚠️ " if acc_pct >= 50 else "❌"
    print(f"\n[{i}/3] {test['name']}")
    print(f"  {status} Accuracy: {acc_pct:6.1f}% | Precision: {metrics['precision']*100:6.1f}% | Recall: {metrics['recall']*100:6.1f}%")
    print(f"      Caught {metrics['tp']}/{len(test['expected'])} expected skills")
    if metrics['fn'] > 0:
        missed = test["expected"] - metrics["extracted_lower"]
        print(f"      Missed: {', '.join(sorted(missed)[:5])}..." if len(missed) > 5 else f"      Missed: {', '.join(sorted(missed))}")

keyword_avg = sum(keyword_accuracies) / len(keyword_accuracies)
print(f"\n🎯 Keyword-Only Average Accuracy: {keyword_avg*100:.1f}%")

# Phase 2: LLM enhancement
print("\n\n📊 PHASE 2: OLLAMA/LLM ENHANCEMENT (DeepSeek-R1 7B)")
print("-" * 80)

llm_extractor = OllamaSkillExtractor(model="deepseek-r1:7b")
if not llm_extractor.is_available:
    print("❌ Ollama not available")
    exit(1)

llm_results = []
llm_accuracies = []

for i, test in enumerate(FOCUSED_TESTS, 1):
    print(f"\n[{i}/3] {test['name']}")
    print(f"      (LLM inference in progress...)")
    
    try:
        skills_dict = llm_extractor.extract_skills_semantic(test["text"], timeout=120)
        extracted = set(skills_dict.keys())
        metrics = calculate_metrics(extracted, test["expected"])
        llm_results.append((test["name"], metrics))
        llm_accuracies.append(metrics["accuracy"])
        
        acc_pct = metrics["accuracy"] * 100
        status = "✅" if acc_pct >= 70 else "⚠️ " if acc_pct >= 50 else "❌"
        print(f"  {status} Accuracy: {acc_pct:6.1f}% | Precision: {metrics['precision']*100:6.1f}% | Recall: {metrics['recall']*100:6.1f}%")
        print(f"      Caught {metrics['tp']}/{len(test['expected'])} expected skills")
        
        if metrics['fn'] > 0:
            missed = test["expected"] - metrics["extracted_lower"]
            print(f"      Missed: {', '.join(sorted(missed)[:5])}..." if len(missed) > 5 else f"      Missed: {', '.join(sorted(missed))}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
        llm_results.append((test["name"], None))
        llm_accuracies.append(0)

llm_avg = sum(llm_accuracies) / len(llm_accuracies) if llm_accuracies else 0
print(f"\n🎯 LLM-Enhanced Average Accuracy: {llm_avg*100:.1f}%")

# Comparison
print("\n\n" + "="*80)
print("COMPARISON & IMPROVEMENT ANALYSIS")
print("="*80)

print(f"\n{'Test Case':<40} {'Keyword':<12} {'LLM':<12} {'Improvement':<12}")
print("-" * 80)

improvements = []
for (name, kw_m), (_, llm_m) in zip(keyword_results, llm_results):
    kw_acc = kw_m["accuracy"] * 100
    llm_acc = llm_m["accuracy"] * 100 if llm_m else kw_acc
    imp = llm_acc - kw_acc
    improvements.append(imp)
    print(f"{name:<40} {kw_acc:6.1f}%      {llm_acc:6.1f}%      {imp:+6.1f}%")

print("-" * 80)
print(f"{'AVERAGE':<40} {keyword_avg*100:6.1f}%      {llm_avg*100:6.1f}%      {(llm_avg-keyword_avg)*100:+6.1f}%")

# Save results
results = {
    "model": "deepseek-r1:7b",
    "baseline_accuracy": keyword_avg,
    "llm_accuracy": llm_avg,
    "improvement": llm_avg - keyword_avg,
    "tests": [
        {
            "name": name,
            "keyword_accuracy": kw_metrics["accuracy"],
            "llm_accuracy": llm_metrics["accuracy"] if llm_metrics else kw_metrics["accuracy"]
        }
        for (name, kw_metrics), (_, llm_metrics) in zip(keyword_results, llm_results)
    ]
}

with open("LLM_COMPARISON_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to LLM_COMPARISON_RESULTS.json")
print("="*80 + "\n")
