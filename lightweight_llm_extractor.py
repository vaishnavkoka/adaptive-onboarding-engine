"""
Lightweight LLM-Enhanced Skill Extractor using Sentence Transformers
Provides semantic similarity-based skill detection without large model requirements
"""

from typing import Dict, Set, Tuple, List
import re
from skill_extractor import SkillExtractor as BaseSkillExtractor


class LightweightLLMExtractor(BaseSkillExtractor):
    """
    Lightweight LLM skill extractor using sentence embeddings
    Uses sentence-transformers for semantic similarity matching
    Minimal memory footprint, fast inference
    """
    
    def __init__(self):
        super().__init__()
        self.use_semantic_search = self._initialize_semantic_model()
        self.model = None
        self.model_name = None
        
    def _initialize_semantic_model(self) -> bool:
        """Initialize sentence transformer if available"""
        try:
            from sentence_transformers import SentenceTransformer
            # Using lightweight model suitable for production
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_name = 'all-MiniLM-L6-v2'
            
            # Pre-compute embeddings for all known skills
            self._cache_skill_embeddings()
            return True
        except ImportError:
            print("⚠ sentence-transformers not installed. Using keyword-based extraction.")
            return False
        except Exception as e:
            print(f"⚠ Semantic model initialization failed: {e}")
            return False
    
    def _cache_skill_embeddings(self):
        """Pre-compute embeddings for all skills in knowledge base"""
        try:
            if not self.model:
                return
            
            # Get all unique skills from knowledge base
            all_skills = list(set(
                list(self.TECHNICAL_SKILLS.keys()) +
                list(self.SOFT_SKILLS.keys())
            ))
            
            # Compute embeddings
            self.skill_embeddings = {}
            for skill in all_skills:
                self.skill_embeddings[skill] = self.model.encode(skill)
        except Exception as e:
            print(f"Skill embedding cache failed: {e}")
            self.use_semantic_search = False
    
    def extract_skills_semantic(self, text: str) -> Dict[str, str]:
        """
        Extract skills using semantic similarity
        Combines keyword matching with semantic search
        
        Args:
            text: Input text (resume or job description)
        
        Returns:
            Dictionary mapping skill names to proficiency levels
        """
        # Get base skills from keyword extraction
        base_skills = self.extract_with_proficiency(text)
        
        if not self.use_semantic_search or not self.model:
            return base_skills
        
        try:
            # Find semantically similar skills
            similar_skills = self._find_semantically_similar_skills(text)
            
            # Merge with base skills, with deduplication
            enhanced_skills = base_skills.copy()
            for skill, proficiency in similar_skills.items():
                if skill not in enhanced_skills:
                    enhanced_skills[skill] = proficiency
            
            return enhanced_skills
        except Exception as e:
            print(f"Semantic extraction failed: {e}. Returning base skills.")
            return base_skills
    
    def _find_semantically_similar_skills(self, text: str) -> Dict[str, str]:
        """Find skills that appear semantically in the text"""
        if not self.model:
            return {}
        
        similar_skills = {}
        
        try:
            # Split text into chunks for semantic analysis
            chunks = self._extract_meaningful_chunks(text)
            
            # Encode text chunks
            chunk_embeddings = self.model.encode(chunks)
            
            # Compare with skill embeddings
            for chunk, chunk_embedding in zip(chunks, chunk_embeddings):
                matches = self._find_similar_skills_for_chunk(chunk, chunk_embedding)
                for skill, proficiency, similarity_score in matches:
                    if skill not in similar_skills:
                        similar_skills[skill] = proficiency
            
            return similar_skills
        except Exception as e:
            return {}
    
    def _extract_meaningful_chunks(self, text: str) -> List[str]:
        """Extract meaningful phrases from text for semantic analysis"""
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Filter short sentences
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        # Limit to top 15 sentences for performance
        return meaningful[:15]
    
    def _find_similar_skills_for_chunk(self, chunk: str, chunk_embedding) -> List[Tuple[str, str, float]]:
        """Find skills similar to the chunk"""
        from scipy.spatial.distance import cosine
        
        matches = []
        
        try:
            # Compute cosine similarity with all skills
            for skill, skill_embedding in self.skill_embeddings.items():
                similarity = 1 - cosine(chunk_embedding, skill_embedding)
                
                # Threshold for match (0.6 = 60% semantic similarity)
                if similarity > 0.6:
                    proficiency = self._determine_proficiency_from_chunk(chunk, skill)
                    matches.append((skill, proficiency, similarity))
            
            # Sort by similarity and return top matches
            matches.sort(key=lambda x: x[2], reverse=True)
            return matches[:3]  # Return top 3 matches per chunk
        except Exception as e:
            return []
    
    def _determine_proficiency_from_chunk(self, chunk: str, skill: str) -> str:
        """Determine proficiency level based on context"""
        lower_chunk = chunk.lower()
        
        # Define proficiency indicators
        indicators = {
            'expert': ['expert', 'master', 'architect', 'lead', 'principal', 'expert-level', 
                      'advanced proficiency', 'deep expertise'],
            'intermediate': ['experienced', 'skilled at', 'strong experience', 'proficient', 
                           'solid knowledge', 'strong understanding', 'working knowledge'],
            'beginner': ['basic', 'familiar with', 'learning', 'beginner', 'introductory',
                        'basic knowledge', 'starting to learn']
        }
        
        # Check indicators
        for level, keywords in indicators.items():
            if any(keyword in lower_chunk for keyword in keywords):
                return level
        
        return 'mentioned'
    
    def extract_with_confidence_scores(self, text: str) -> Tuple[Dict[str, str], Dict]:
        """
        Extract skills with confidence metrics
        
        Returns:
            Tuple of (skills_dict, metrics)
        """
        skills_dict = self.extract_skills_semantic(text)
        
        metrics = {
            'total_skills': len(skills_dict),
            'extraction_method': 'semantic' if self.use_semantic_search else 'keyword',
            'model': self.model_name,
            'proficiency_distribution': self._calculate_proficiency_distribution(skills_dict),
            'semantic_search_enabled': self.use_semantic_search,
            'overall_score': self.score_skills(skills_dict),
            'confidence_estimate': self._estimate_confidence(skills_dict)
        }
        
        return skills_dict, metrics
    
    def _calculate_proficiency_distribution(self, skills_dict: Dict[str, str]) -> Dict[str, int]:
        """Calculate distribution of proficiency levels"""
        distribution = {
            'expert': 0,
            'intermediate': 0,
            'beginner': 0,
            'mentioned': 0
        }
        
        for level in skills_dict.values():
            if level in distribution:
                distribution[level] += 1
        
        return distribution
    
    def _estimate_confidence(self, skills_dict: Dict[str, str]) -> float:
        """
        Estimate overall extraction confidence
        Based on skill count and proficiency distribution
        """
        if not skills_dict:
            return 0.0
        
        # Weight by proficiency levels
        weights = {'expert': 1.0, 'intermediate': 0.8, 'beginner': 0.6, 'mentioned': 0.3}
        
        total_weight = sum(weights.get(level, 0.3) for level in skills_dict.values())
        max_possible_weight = len(skills_dict) * 1.0
        
        confidence = total_weight / max_possible_weight if max_possible_weight > 0 else 0.0
        return min(1.0, confidence)


def get_llm_extractor(use_semantic: bool = True):
    """
    Factory function to get LLM-enhanced extractor
    
    Args:
        use_semantic: If True, uses semantic similarity. If False, uses zero-shot classification
    
    Returns:
        Appropriate extractor instance
    """
    try:
        extractor = LightweightLLMExtractor()
        if extractor.use_semantic_search:
            print("✓ Using semantic similarity-based skill extraction (sentence-transformers)")
            return extractor
        else:
            print("⚠ Semantic model unavailable, using keyword-based extraction")
            return BaseSkillExtractor()
    except Exception as e:
        print(f"⚠ LLM extractor initialization failed: {e}. Using base extractor.")
        return BaseSkillExtractor()
