"""
Ollama-Based LLM Skill Extractor
Uses open-source LLMs (Deepseek R1, Llama 2, etc.) for advanced skill extraction
"""

import requests
import json
import re
from typing import Dict, Set, Tuple, List
from skill_extractor import SkillExtractor as BaseSkillExtractor
import time


class OllamaSkillExtractor(BaseSkillExtractor):
    """
    Advanced skill extractor using Ollama with open-source LLMs
    Provides context-aware skill detection with semantic understanding
    """
    
    def __init__(self, model: str = "deepseek-r1:7b", ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama-based skill extractor
        
        Args:
            model: Ollama model name (deepseek-r1:7b, llama2, etc.)
            ollama_url: Base URL for Ollama API
        """
        super().__init__()
        self.model = model
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"
        self.is_available = self._check_ollama_available()
        
        if not self.is_available:
            print(f"⚠️  Ollama not available at {ollama_url}")
            print("   Run: ollama serve")
            print("   Then pull model: ollama pull deepseek-r1:7b")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def extract_skills_semantic(self, text: str, timeout: int = 30) -> Dict[str, str]:
        """
        Extract skills using LLM semantic understanding
        Combines keyword extraction with context-aware LLM analysis
        
        Args:
            text: Resume or job description text
            timeout: Request timeout in seconds
        
        Returns:
            Dictionary of skills with confidence scores
        """
        # Start with keyword-based extraction
        base_skills = self.extract_with_proficiency(text)
        
        if not self.is_available:
            return base_skills
        
        # Enhance with LLM semantic understanding
        try:
            llm_skills = self._extract_with_llm(text, timeout)
            # Merge results: LLM-identified skills + keyword skills
            merged = self._merge_skills(base_skills, llm_skills)
            return merged
        except Exception as e:
            print(f"⚠️  LLM extraction error: {e}")
            return base_skills
    
    def _extract_with_llm(self, text: str, timeout: int = 30) -> Dict[str, str]:
        """
        Use LLM to identify skills in context
        
        Args:
            text: Input text
            timeout: API timeout
        
        Returns:
            Dictionary of LLM-identified skills
        """
        # Prepare concise prompt for efficiency
        prompt = f"""Analyze this resume/profile and extract ALL technical and professional skills.
        
Resume/Profile:
{text[:2000]}  # Limit to 2000 chars for performance

Return ONLY a JSON object like this - no explanations:
{{"skills": ["skill1", "skill2", ...], "confidence": 0.85}}

Skills should be concrete (Java, AWS, Project Management, etc.)
Include both technical and professional skills."""

        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temp for consistency
                },
                timeout=timeout
            )
            
            if response.status_code != 200:
                return {}
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Parse JSON from response
            skills = self._parse_llm_response(response_text)
            
            skill_dict = {}
            for skill in skills:
                # Normalize skill names
                normalized = self._normalize_skill_name(skill)
                if normalized:
                    skill_dict[normalized] = "expert"  # LLM-identified skills marked as expert
            
            return skill_dict
        
        except requests.Timeout:
            print(f"⚠️  Ollama request timed out after {timeout}s")
            return {}
        except Exception as e:
            print(f"⚠️  LLM error: {e}")
            return {}
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse skills from LLM JSON response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data.get("skills", [])
        except json.JSONDecodeError:
            # Fallback: extract quoted items
            matches = re.findall(r'"([^"]+)"', response)
            return [m.lower() for m in matches if len(m) > 2]
        return []
    
    def _normalize_skill_name(self, skill: str) -> str:
        """Normalize skill name to match database"""
        if not skill:
            return ""
        
        skill = skill.lower().strip()
        
        # Handle common variations
        normalizations = {
            'nodejs': 'node.js',
            'node js': 'node.js',
            'django': 'django',
            'flask': 'flask',
            'react.js': 'react',
            'react js': 'react',
            'angular.js': 'angular',
            'angular js': 'angular',
            'aws': 'aws',
            'azure': 'azure',
            'gcp': 'gcp',
            'google cloud': 'gcp',
            'docker': 'docker',
            'kubernetes': 'kubernetes',
            'k8s': 'kubernetes',
            'sql': 'sql',
            'nosql': 'nosql',
            'mongodb': 'mongodb',
            'postgres': 'postgresql',
            'postgresql': 'postgresql',
            'mysql': 'mysql',
            'machine learning': 'machine learning',
            'ml': 'machine learning',
            'deep learning': 'deep learning',
            'tensorflow': 'tensorflow',
            'pytorch': 'pytorch',
            'scikit learn': 'scikit-learn',
            'scikit-learn': 'scikit-learn',
            'nlp': 'nlp',
            'natural language processing': 'nlp',
            'computer vision': 'computer vision',
        }
        
        return normalizations.get(skill, skill)
    
    def _merge_skills(self, base_skills: Dict[str, str], llm_skills: Dict[str, str]) -> Dict[str, str]:
        """
        Merge base keyword skills with LLM-identified skills
        
        Args:
            base_skills: Skills from keyword extraction
            llm_skills: Skills from LLM
        
        Returns:
            Merged skills dictionary
        """
        merged = base_skills.copy()
        
        # Add LLM-identified skills (prefer existing if already found)
        for skill, confidence in llm_skills.items():
            if skill not in merged:
                merged[skill] = confidence
        
        return merged
    
    def batch_extract(self, texts: List[str], show_progress: bool = True) -> List[Dict[str, str]]:
        """
        Extract skills from multiple texts efficiently
        
        Args:
            texts: List of resume/profile texts
            show_progress: Show progress indicator
        
        Returns:
            List of skill dictionaries
        """
        results = []
        for i, text in enumerate(texts):
            if show_progress:
                print(f"  Processing {i+1}/{len(texts)}...", end='\r')
            skills = self.extract_skills_semantic(text)
            results.append(skills)
        
        if show_progress:
            print(f"  ✓ Processed {len(texts)} texts                  ")
        
        return results
