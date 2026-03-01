import json
import os
import logging
from typing import Dict, Any, Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProblemStatementGenerator:
    """Generate problem statements using AI for coding challenges"""
    
    def __init__(self, api_key: str = None, provider: str = None):
        """
        Initialize with API key from env or parameter
        """
        self.provider = (provider or os.getenv("AI_PROVIDER", "gemini")).lower()
        
        if self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel("gemini-1.5-pro")
        else:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic not installed. Install with: pip install anthropic")
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_problem(self, difficulty: str, elo_rating: int, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a coding problem statement based on difficulty and domain.
        
        Args:
            difficulty: 'beginner', 'intermediate', or 'advanced'
            elo_rating: Player's ELO rating (used to tune difficulty slightly)
            domain: Specific algorithmic domain (e.g. 'arrays', 'strings', 'dynamic_programming')
            
        Returns:
            Dict containing title, statement, domain, constraints, input_format, output_format
        """
        
        domain_str = f" in the domain of '{domain}'" if domain else ""
        
        prompt = f"""
        Generate a unique, engaging coding challenge.
        Difficulty: {difficulty} (Suitable for a player with ELO rating {elo_rating}){domain_str}
        
        The problem must be completely unique, engaging, and have a clear, unambiguous solution.
        Do NOT include the solution code. ONLY generate the problem specification.
        
        Respond ONLY with a valid JSON object matching this exact format:
        {{
            "title": "Creative Problem Title",
            "statement": "Detailed problem description, story, or scenario.",
            "domain": "arrays/strings/math/etc",
            "constraints": {{
                "input_size": "1 <= N <= 10^5",
                "values": "-10^9 <= A[i] <= 10^9"
            }},
            "input_format": "Description of how the input is formatted",
            "output_format": "Description of the expected output"
        }}
        
        No markdown code block wrappers (like ```json). Just the raw JSON text.
        """
        
        try:
            if self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2000
                    )
                )
                text = response.text.strip()
            else:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text.strip()
            if text.startswith("```"):
                lines = text.split("\\n")
                if len(lines) > 1:
                    text = "\\n".join(lines[1:-1])  # Strip ```json and ```
                text = text.replace("```json", "").replace("```", "").strip()
                
            problem_data = json.loads(text)
            
            # Ensure required fields are present
            required_keys = ["title", "statement", "domain", "constraints", "input_format", "output_format"]
            for k in required_keys:
                if k not in problem_data:
                    problem_data[k] = "Not specified"
                    
            if not isinstance(problem_data.get("constraints"), dict):
                problem_data["constraints"] = {"general": str(problem_data.get("constraints", ""))}
                
            return problem_data
            
        except Exception as e:
            logger.error(f"Failed to generate problem using Gemini: {{e}}")
            # Return a simple fallback if LLM fails here but we are supposed to use it
            return {{
                "title": f"Fallback Challenge ({{difficulty}})",
                "statement": f"Write a function to solve a problem involving {{domain or 'basic programming'}}.",
                "domain": domain or "general",
                "constraints": {{"input_size": "1 <= N <= 100"}},
                "input_format": "Standard input",
                "output_format": "Standard output"
            }}

