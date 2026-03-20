"""
Lightweight LLM-Enhanced Skill Extractor using Sentence Transformers
Provides semantic similarity-based skill detection without large model requirements
Gracefully falls back to keyword matching if LLM unavailable
"""

from typing import Dict, Tuple, List
import re
from skill_extractor import SkillExtractor as BaseSkillExtractor


class LightweightLLMExtractor(BaseSkillExtractor):
    """
    Lightweight LLM skill extractor using sentence embeddings
    Uses sentence-transformers for semantic similarity matching
    Lazy loads model only when needed
    """
    
    def __init__(self):
        super().__init__()
        self.use_semantic_search = False
        self.model = None
        self.model_name = None
        self.skill_embeddings = {}
        # Don't load model immediately - do it on first use
        self._model_loaded = False
        self._model_load_attempted = False
        
    def _initialize_semantic_model(self) -> bool:
        """Initialize sentence transformer if available (lazy loading)"""
        if self._model_load_attempted:
            return self.use_semantic_search
        
        self._model_load_attempted = True
        
        try:
            from sentence_transformers import SentenceTransformer
            print("  Loading sentence-transformers model (first time only)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            self.model_name = 'all-MiniLM-L6-v2'
            
            # Pre-compute embeddings for all known skills
            self._cache_skill_embeddings()
            self.use_semantic_search = True
            self._model_loaded = True
            print("  ✓ Semantic model loaded successfully")
            return True
        except ImportError:
            print("  ⚠ sentence-transformers not available - using keyword extraction")
            self.use_semantic_search = False
            return False
        except Exception as e:
            print(f"  ⚠ Model initialization failed: {e}")
            print("  Using keyword extraction as fallback")
            self.use_semantic_search = False
            return False
    
    def _cache_skill_embeddings(self):
        """Pre-compute embeddings for all skills in knowledge base"""
        try:
            if not self.model:
                return
            
            all_skills = list(set(
                list(self.TECHNICAL_SKILLS.keys()) +
                list(self.SOFT_SKILLS.keys())
            ))
            
            print(f"  Caching embeddings for {len(all_skills)} skills...")
            self.skill_embeddings = {}
            batch_size = 32
            for i in range(0, len(all_skills), batch_size):
                batch = all_skills[i:i+batch_size]
                try:
                    embeddings = self.model.encode(batch, show_progress_bar=False)
                    for skill, embedding in zip(batch, embeddings):
                        self.skill_embeddings[skill] = embedding
                except:
                    continue
            print(f"  ✓ Cached {len(self.skill_embeddings)} skill embeddings")
        except Exception as e:
            print(f"  Skill embedding cache failed: {e}")
            self.use_semantic_search = False
    
    def extract_skills_semantic(self, text: str) -> Dict[str, str]:
        """Extract skills using semantic similarity with lazy model loading"""
        # Initialize model on first use
        if not self._model_loaded and not self._model_load_attempted:
            self._initialize_semantic_model()
        
        # Get base skills from keyword extraction
        base_skills = self.extract_with_proficiency(text)
        
        if not self.use_semantic_search or not self.model:
            return base_skills
        
        try:
            # Find semantically similar skills
            similar_skills = self._find_semantically_similar_skills(text)
            
            # Merge with base skills
            enhanced_skills = base_skills.copy()
            for skill, proficiency in similar_skills.items():
                if skill not in enhanced_skills:
                    enhanced_skills[skill] = proficiency
            
            return enhanced_skills
        except Exception:
            return base_skills
    
    def _find_semantically_similar_skills(self, text: str) -> Dict[str, str]:
        """Find skills that appear semantically in the text"""
        if not self.model or not self.skill_embeddings:
            return {}
        
        try:
            chunks = self._extract_meaningful_chunks(text)
            if not chunks:
                return {}
            
            chunk_embeddings = self.model.encode(chunks, show_progress_bar=False)
            
            similar_skills = {}
            for chunk, chunk_embedding in zip(chunks, chunk_embeddings):
                matches = self._find_similar_skills_for_chunk(chunk, chunk_embedding)
                for skill, proficiency, _ in matches:
                    if skill not in similar_skills:
                        similar_skills[skill] = proficiency
            
            return similar_skills
        except Exception:
            return {}
    
    def _extract_meaningful_chunks(self, text: str) -> List[str]:
        """Extract meaningful phrases from text"""
        sentences = re.split(r'[.!?]+', text)
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 15]
        return meaningful[:15]
    
    def _find_similar_skills_for_chunk(self, chunk: str, chunk_embedding) -> List[Tuple[str, str, float]]:
        """Find skills similar to the chunk"""
        try:
            from scipy.spatial.distance import cosine
        except ImportError:
            return []
        
        matches = []
        
        try:
            for skill, skill_embedding in self.skill_embeddings.items():
                try:
                    similarity = 1 - cosine(chunk_embedding, skill_embedding)
                    if similarity > 0.6:
                        proficiency = self._determine_proficiency_from_chunk(chunk, skill)
                        matches.append((skill, proficiency, similarity))
                except:
                    continue
            
            matches.sort(key=lambda x: x[2], reverse=True)
            return matches[:3]
        except Exception:
            return []
    
    def _determine_proficiency_from_chunk(self, chunk: str, skill: str) -> str:
        """Determine proficiency level based on context"""
        lower_chunk = chunk.lower()
        
        indicators = {
            'expert': ['expert', 'master', 'architect', 'lead', 'principal'],
            'intermediate': ['experienced', 'skilled', 'proficient', 'strong'],
            'beginner': ['basic', 'learning', 'familiar', 'beginner', 'starting'],
        }
        
        for level, keywords in indicators.items():
            if any(kw in lower_chunk for kw in keywords):
                return level
        
        return 'mentioned'
    
    def extract_with_confidence_scores(self, text: str) -> Tuple[Dict[str, str], Dict]:
        """Extract skills with confidence metrics"""
        if not self._model_loaded:
            self._initialize_semantic_model()
        
        skills_dict = self.extract_skills_semantic(text)
        
        return skills_dict, {
            'total_skills': len(skills_dict),
            'extraction_method': 'semantic' if self.use_semantic_search else 'keyword',
            'model': self.model_name,
            'proficiency_distribution': self._calc_distribution(skills_dict),
            'semantic_search_enabled': self.use_semantic_search,
            'overall_score': self.score_skills(skills_dict),
            'confidence_estimate': self._estimate_confidence(skills_dict)
        }
    
    def _calc_distribution(self, skills_dict: Dict[str, str]) -> Dict[str, int]:
        """Calculate distribution of proficiency levels"""
        dist = {'expert': 0, 'intermediate': 0, 'beginner': 0, 'mentioned': 0}
        for level in skills_dict.values():
            if level in dist:
                dist[level] += 1
        return dist
    
    def _estimate_confidence(self, skills_dict: Dict[str, str]) -> float:
        """Estimate extraction confidence"""
        if not skills_dict:
            return 0.0
        weights = {'expert': 1.0, 'intermediate': 0.8, 'beginner': 0.6, 'mentioned': 0.3}
        total = sum(weights.get(level, 0.3) for level in skills_dict.values())
        return min(1.0, total / len(skills_dict))


def get_llm_extractor(use_semantic: bool = True):
    """Factory function to get LLM-enhanced extractor with graceful fallback"""
    try:
        extractor = LightweightLLMExtractor()
        return extractor
    except Exception as e:
        print(f"LLM extractor initialization failed: {e}. Using base extractor.")
        return BaseSkillExtractor()
