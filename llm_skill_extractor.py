"""
LLM-Based Skill Extractor using Pre-trained Models
Uses Hugging Face transformers for better skill extraction
"""

from typing import Dict, Set, Tuple
import re
from skill_extractor import SkillExtractor as BaseSkillExtractor


class LLMSkillExtractor(BaseSkillExtractor):
    """
    Enhanced skill extractor using LLM prompting and NER
    Inherits from base extractor and adds LLM capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.use_llm = self._check_llm_available()
        self.llm_model_name = None
        
        if self.use_llm:
            try:
                # Try to load a smaller, efficient model
                from transformers import pipeline
                # Using zero-shot classification for skill detection
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # CPU mode
                )
                self.llm_model_name = "facebook/bart-large-mnli"
            except Exception as e:
                print(f"Warning: Could not load LLM model: {e}")
                self.use_llm = False
    
    def _check_llm_available(self) -> bool:
        """Check if transformers library is available"""
        try:
            import transformers
            return True
        except ImportError:
            return False
    
    def extract_skills_with_llm(self, text: str) -> Dict[str, str]:
        """
        Extract skills using LLM-based approach complemented by keyword matching
        
        Args:
            text: Input text (resume or job description)
        
        Returns:
            Dictionary mapping skill names to proficiency levels
        """
        # First, do standard extraction
        skills_dict = self.extract_with_proficiency(text)
        
        # If LLM available, enhance with LLM-based detection
        if self.use_llm and self.classifier:
            enhanced_skills = self._enhance_with_llm(text, skills_dict)
            return enhanced_skills
        
        return skills_dict
    
    def _enhance_with_llm(self, text: str, base_skills: Dict[str, str]) -> Dict[str, str]:
        """
        Enhance skill extraction using LLM zero-shot classification
        
        Args:
            text: Input text
            base_skills: Base skills already extracted
        
        Returns:
            Enhanced skills dictionary
        """
        try:
            # Split text into sentences for more focused analysis
            sentences = self._split_into_sentences(text)
            enhanced_skills = base_skills.copy()
            
            # Sample key sentences (limit for performance)
            sample_sentences = sentences[:20] if len(sentences) > 20 else sentences
            
            for sentence in sample_sentences:
                if len(sentence.strip()) < 10:
                    continue
                
                # Use classifier to identify skill-related sentences
                try:
                    result = self.classifier(
                        sentence,
                        ["technical skill", "soft skill", "tool", "framework", "general information"],
                        multi_class=False,
                        hypothesis_template="This sentence mentions {}."
                    )
                    
                    # If high confidence skill mention, extract potential skills
                    if result['scores'][0] > 0.7 and result['labels'][0] != "general information":
                        potential_skills = self._extract_potential_skills(sentence)
                        for skill in potential_skills:
                            if skill not in enhanced_skills:
                                # Determine proficiency from context
                                proficiency = self._infer_proficiency_llm(sentence, skill)
                                enhanced_skills[skill] = proficiency
                except Exception as e:
                    # Continue even if individual classification fails
                    continue
            
            return enhanced_skills
        
        except Exception as e:
            print(f"LLM enhancement failed: {e}. Falling back to base extraction.")
            return base_skills
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_potential_skills(self, text: str) -> Set[str]:
        """Extract potential skill names from text"""
        skills = set()
        
        # Look for capitalized words and technical terms
        words = text.split()
        for i, word in enumerate(words):
            # Check for compound terms (2-3 words)
            compound = ' '.join(words[max(0, i-1):min(len(words), i+3)])
            
            # Normalize and check against knowledge base
            normalized = compound.lower().strip('.,;:')
            if normalized in self.SKILL_KEYWORDS:
                skills.add(normalized)
        
        return skills
    
    def _infer_proficiency_llm(self, sentence: str, skill: str) -> str:
        """Infer proficiency level using context"""
        lower_sentence = sentence.lower()
        
        # Expert indicators
        expert_keywords = ['expert', 'master', 'architect', 'lead', 'advanced', 'proficient']
        # Intermediate indicators
        intermediate_keywords = ['experienced', 'skilled', 'proficient', 'strong', 'solid']
        # Beginner indicators
        beginner_keywords = ['basic', 'familiar', 'beginner', 'learning', 'started']
        
        if any(keyword in lower_sentence for keyword in expert_keywords):
            return 'expert'
        elif any(keyword in lower_sentence for keyword in intermediate_keywords):
            return 'intermediate'
        elif any(keyword in lower_sentence for keyword in beginner_keywords):
            return 'beginner'
        else:
            return 'mentioned'
    
    def score_skills_with_confidence(self, skills_dict: Dict[str, str]) -> Tuple[float, Dict]:
        """
        Score skills with confidence metrics
        
        Returns:
            Tuple of (overall_score, detailed_metrics)
        """
        overall_score = self.score_skills(skills_dict)
        
        # Calculate detailed metrics
        metrics = {
            'overall_score': overall_score,
            'extraction_method': 'LLM-enhanced' if self.use_llm else 'keyword-based',
            'model': self.llm_model_name,
            'total_skills': len(skills_dict),
            'proficiency_distribution': self._calculate_proficiency_distribution(skills_dict),
            'confidence': self._calculate_extraction_confidence(skills_dict)
        }
        
        return overall_score, metrics
    
    def _calculate_proficiency_distribution(self, skills_dict: Dict[str, str]) -> Dict[str, int]:
        """Calculate distribution of proficiency levels"""
        distribution = {
            'expert': 0,
            'intermediate': 0,
            'beginner': 0,
            'mentioned': 0
        }
        
        for proficiency in skills_dict.values():
            if proficiency in distribution:
                distribution[proficiency] += 1
        
        return distribution
    
    def _calculate_extraction_confidence(self, skills_dict: Dict[str, str]) -> float:
        """
        Calculate confidence in skill extraction
        Higher confidence = more skills with higher proficiency levels
        """
        if not skills_dict:
            return 0.0
        
        confidence_score = 0.0
        proficiency_weights = {'expert': 1.0, 'intermediate': 0.8, 'beginner': 0.6, 'mentioned': 0.3}
        
        for proficiency in skills_dict.values():
            confidence_score += proficiency_weights.get(proficiency, 0.3)
        
        # Normalize to 0-1 range
        return min(1.0, confidence_score / len(skills_dict))


# Fallback to standard extractor if transformers not available
def get_skill_extractor():
    """
    Factory function to get appropriate skill extractor
    Automatically falls back to base extractor if LLM unavailable
    """
    try:
        extractor = LLMSkillExtractor()
        if extractor.use_llm:
            print("✓ Using LLM-enhanced skill extraction")
            return extractor
        else:
            print("⚠ LLM unavailable, using keyword-based extraction")
            return BaseSkillExtractor()
    except Exception as e:
        print(f"⚠ LLM extractor initialization failed: {e}. Using keyword-based extraction.")
        return BaseSkillExtractor()
