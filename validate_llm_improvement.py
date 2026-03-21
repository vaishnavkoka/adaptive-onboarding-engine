"""
LLM Skill Extraction Validation
Compare keyword-only vs. Ollama/LLM-based extraction
"""

import subprocess
import sys
import json
from typing import Dict, List, Tuple
from skill_extractor import SkillExtractor
from ollama_skill_extractor import OllamaSkillExtractor


def ensure_ollama_running():
    """Check if Ollama is running, provide instructions if not"""
    extractor = OllamaSkillExtractor()
    if not extractor.is_available:
        print("\n⚠️  OLLAMA IS NOT RUNNING")
        print("=" * 60)
        print("Start Ollama in a new terminal:")
        print("  $ ollama serve")
        print("\nThen ensure model is available:")
        print("  $ ollama pull deepseek-r1:7b")
        print("=" * 60)
        return False
    return True


# Gold standard test cases (same as before)
GOLD_STANDARD_TESTS = [
    {
        "name": "Full-Stack Developer",
        "text": """
        Senior Full Stack Developer with 8+ years experience.
        Frontend: React.js, Angular, Vue.js, HTML5, CSS3, JavaScript, TypeScript
        Backend: Node.js, Python, Django, Flask, Java, Spring Boot
        Databases: MongoDB, PostgreSQL, MySQL, Redis, Elasticsearch
        Cloud: AWS (EC2, S3, Lambda), Azure
        DevOps: Docker, Kubernetes, Jenkins, GitLab CI/CD
        Other: RESTful APIs, Microservices, gRPC, GraphQL, Git
        """,
        "expected_skills": {
            "react", "angular", "vue.js", "html5", "css3", "javascript", "typescript",
            "node.js", "python", "django", "flask", "java", "spring boot",
            "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "aws", "azure", "docker", "kubernetes", "jenkins", "git"
        }
    },
    {
        "name": "Finance Analyst",
        "text": """
        Financial Analyst with 6 years in investment banking.
        Technical Skills: Excel (advanced), VBA, SQL, Tableau, Power BI
        Financial: Corporate Finance, Valuation, M&A, Risk Analysis
        Tools: Bloomberg Terminal, FactSet, SAP, Salesforce
        Programming: Python, R for statistical analysis
        """,
        "expected_skills": {
            "excel", "vba", "sql", "tableau", "power bi",
            "corporate finance", "valuation", "m&a", "risk analysis",
            "python", "r", "bloomberg", "factset", "sap", "salesforce"
        }
    },
    {
        "name": "Sales Executive",
        "text": """
        Senior Sales Executive, B2B Enterprise Solutions.
        CRM: Salesforce, HubSpot, Pipedrive
        Skills: Account Management, Pipeline Management, Negotiation, Presentation
        Soft Skills: Leadership, Communication, Strategic Planning, Client Relations
        Knowledge: SaaS, Cloud Solutions, Enterprise Software
        """,
        "expected_skills": {
            "salesforce", "hubspot", "pipedrive", "account management",
            "pipeline management", "negotiation", "presentation",
            "leadership", "communication", "strategic planning",
            "saas", "cloud solutions", "crm"
        }
    },
    {
        "name": "Embedded Systems Engineer",
        "text": """
        Embedded Systems Engineer specializing in IoT and Microcontrollers.
        Microcontrollers: Arduino, STM32, ESP32, ARM Cortex-M
        Languages: C, C++, Assembly, Python
        Protocols: UART, I2C, SPI, CAN, Bluetooth, WiFi
        Tools: KEIL uVision, GDB Debugger, Logic Analyzer
        Real-time OS: FreeRTOS, RTOS basics
        """,
        "expected_skills": {
            "arduino", "stm32", "esp32", "arm cortex",
            "c", "c++", "assembly", "python",
            "uart", "i2c", "spi", "can", "bluetooth", "wifi",
            "freertos", "rtos", "keil", "gdb"
        }
    },
    {
        "name": "Healthcare IT Professional",
        "text": """
        Healthcare IT Specialist with clinical informatics background.
        EHR Systems: Epic, Cerner, Allscripts, HL7/FHIR
        Clinical: EMR workflows, Clinical Decision Support, Patient Data Management
        Compliance: HIPAA, GDPR, SOC 2 certification
        Technical: SQL Server, BI tools, healthcare analytics
        Skills: Clinical workflows, Data governance, Interoperability
        """,
        "expected_skills": {
            "epic", "cerner", "allscripts", "hl7", "fhir",
            "emr", "ehr", "hipaa", "gdpr",
            "sql server", "healthcare analytics", "data governance",
            "clinical workflows", "patient data", "interoperability"
        }
    },
    {
        "name": "Management Consultant",
        "text": """
        Management Consultant with strategy and operations focus.
        Expertise: Business Strategy, Operational Excellence, Digital Transformation
        Industries: Technology, Financial Services, Healthcare, Manufacturing
        Methodologies: Six Sigma, Lean, Agile, Change Management
        Tools: Tableau, Excel, Python for data analysis
        Soft Skills: Client Engagement, Problem Solving, Presentation, Leadership
        """,
        "expected_skills": {
            "business strategy", "operational excellence", "digital transformation",
            "six sigma", "lean", "agile", "change management",
            "tableau", "excel", "python",
            "client engagement", "problem solving", "presentation", "leadership"
        }
    },
    {
        "name": "Minimalist Resume",
        "text": """
        Skills: Python, Java, SQL, Git, Docker, AWS, Machine Learning
        """,
        "expected_skills": {
            "python", "java", "sql", "git", "docker", "aws", "machine learning"
        }
    }
]


def calculate_metrics(extracted: set, expected: set) -> Dict[str, float]:
    """Calculate precision, recall, F1, and accuracy"""
    true_positives = len(extracted & expected)
    false_positives = len(extracted - expected)
    false_negatives = len(expected - extracted)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Accuracy: how many expected skills we got right
    accuracy = true_positives / len(expected) if len(expected) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": true_positives,
        "fp": false_positives,
        "fn": false_negatives
    }


def test_extractor(extractor_instance, name: str) -> Tuple[float, List[Dict]]:
    """Run all tests and return aggregate accuracy + detailed results"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    
    test_results = []
    total_accuracy = 0
    
    for i, test in enumerate(GOLD_STANDARD_TESTS, 1):
        # Extract skills
        if isinstance(extractor_instance, OllamaSkillExtractor):
            extracted_dict = extractor_instance.extract_skills_semantic(test["text"])
        else:
            extracted_dict = extractor_instance.extract_with_proficiency(test["text"])
        
        extracted = set(extracted_dict.keys())
        expected = {skill.lower() for skill in test["expected_skills"]}
        
        # Normalize extracted for comparison
        extracted_norm = set()
        for skill in extracted:
            norm_skill = skill.lower().strip()
            extracted_norm.add(norm_skill)
        
        metrics = calculate_metrics(extracted_norm, expected)
        metrics["test_name"] = test["name"]
        test_results.append(metrics)
        total_accuracy += metrics["accuracy"]
        
        accuracy_pct = metrics["accuracy"] * 100
        precision_pct = metrics["precision"] * 100
        recall_pct = metrics["recall"] * 100
        f1_pct = metrics["f1"] * 100
        
        status = "✅" if accuracy_pct >= 70 else "⚠️ " if accuracy_pct >= 50 else "❌"
        
        print(f"\n[{i}/7] {test['name']}:")
        print(f"  {status} Accuracy:  {accuracy_pct:6.1f}% | Precision: {precision_pct:6.1f}% | Recall: {recall_pct:6.1f}% | F1: {f1_pct:6.1f}%")
        print(f"      TP: {metrics['tp']:2d} | FP: {metrics['fp']:2d} | FN: {metrics['fn']:2d}")
        
        if metrics['fn'] > 0:
            print(f"      Missed skills: {expected - extracted_norm}")
    
    avg_accuracy = total_accuracy / len(GOLD_STANDARD_TESTS)
    return avg_accuracy, test_results


def main():
    print("\n" + "="*70)
    print("LLM SKILL EXTRACTION - COMPARISON TEST")
    print("="*70)
    
    # Test 1: Keyword-only (baseline)
    print("\n📊 Phase 1: Baseline (Keyword-Only)")
    print("-" * 70)
    keyword_extractor = SkillExtractor()
    keyword_accuracy, keyword_results = test_extractor(keyword_extractor, "Keyword-Only Extractor")
    
    # Test 2: LLM-based
    print("\n\n📊 Phase 2: LLM Enhancement (Deepseek R1 7B)")
    print("-" * 70)
    
    if not ensure_ollama_running():
        print("\n❌ Cannot run LLM tests without Ollama")
        sys.exit(1)
    
    llm_extractor = OllamaSkillExtractor()
    llm_accuracy, llm_results = test_extractor(llm_extractor, "Ollama/LLM Extractor")
    
    # Summary
    print("\n\n" + "="*70)
    print("AGGREGATE RESULTS COMPARISON")
    print("="*70)
    
    improvement = (llm_accuracy - keyword_accuracy) * 100
    improvement_text = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
    improvement_emoji = "🚀" if improvement > 10 else "📈" if improvement > 0 else "⚠️"
    
    print(f"\nKeyword-Only Accuracy:  {keyword_accuracy*100:6.1f}%")
    print(f"LLM-Enhanced Accuracy:  {llm_accuracy*100:6.1f}%")
    print(f"Improvement:            {improvement_emoji} {improvement_text}")
    
    print(f"\n{'Test Case':<30} {'Keyword':<12} {'LLM':<12} {'Improvement':<12}")
    print("-" * 70)
    for kw_result, llm_result in zip(keyword_results, llm_results):
        test_name = kw_result["test_name"][:28]
        kw_acc = kw_result["accuracy"] * 100
        llm_acc = llm_result["accuracy"] * 100
        imp = llm_acc - kw_acc
        print(f"{test_name:<30} {kw_acc:6.1f}%      {llm_acc:6.1f}%      {imp:+6.1f}%")
    
    # Save results
    results_data = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "keyword_accuracy": keyword_accuracy,
        "llm_accuracy": llm_accuracy,
        "improvement": improvement,
        "details": {
            "keyword": keyword_results,
            "llm": llm_results
        }
    }
    
    with open("LLM_VALIDATION_RESULTS.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n✅ Results saved to LLM_VALIDATION_RESULTS.json")
    print("="*70 + "\n")
    
    return llm_accuracy > keyword_accuracy


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
