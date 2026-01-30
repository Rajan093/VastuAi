from typing import List, Dict


class PromptBuilder:
    """Build prompts for Gemini LLM."""
    
    @staticmethod
    def build_summary_prompt(
        rules: List[Dict],
        chart: Dict[str, int],
        aspects: List[str]
    ) -> str:
        
        # Build rules text
        rules_text = "RETRIEVED ASTROLOGICAL RULES:\n\n"
        for i, rule in enumerate(rules, 1):
            rules_text += f"Rule {i}: {rule['heading']}\n"
            rules_text += f"{rule['content']}\n\n"
        
        # Build chart text
        chart_text = "USER'S HOROSCOPE CHART:\n"
        for planet, house in sorted(chart.items()):
            chart_text += f"- {planet} in House {house}\n"
        
        # Build aspects text
        aspects_text = ", ".join(aspects)
        
        # Complete prompt
        prompt = f"""You are an expert astrologer. Below are the specific astrological rules that apply to this user's chart.

{rules_text}

{chart_text}

TASK:
Provide a comprehensive summary for the following life aspects: {aspects_text}

For each aspect, analyze the relevant rules and provide:
1. A clear summary of what the rules indicate
2. Specific predictions or characteristics
3. Any remedies mentioned (if applicable)

IMPORTANT:
- Use ONLY the information provided in the rules above
- If an aspect is not covered in the rules, say "Not mentioned in the provided rules"
- Be specific and reference which planet-house combination you're discussing
- Keep each aspect summary to 3-4 sentences

Format your response as:

**Health:**
[Your summary here]

**Education:**
[Your summary here]

**Wealth:**
[Your summary here]

**Marriage:**
[Your summary here]
"""
        
        return prompt
    
    @staticmethod
    def parse_summary_response(response: str, aspects: List[str]) -> Dict[str, str]:
        """
        Parse Gemini's response into structured summaries.
        
        Args:
            response: Raw text response from Gemini
            aspects: List of aspects to extract
            
        Returns:
            Dictionary mapping aspect names to their summaries
        """
        summaries = {}
        
        # Try to extract each aspect
        for aspect in aspects:
            # Look for the aspect header (case-insensitive)
            import re
            pattern = rf"\*\*{aspect}:?\*\*\s*(.+?)(?=\*\*[A-Z]|$)"
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            
            if match:
                summary = match.group(1).strip()
                summaries[aspect] = summary
            else:
                summaries[aspect] = f"No information found for {aspect}"
        
        return summaries
    
    @staticmethod
    def build_question_prompt(
        rules: List[Dict],
        chart: Dict[str, int],
        question: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Build a prompt for answering a specific user question.
        
        Args:
            rules: Retrieved astrological rules (filtered by relevance)
            chart: User's horoscope chart
            question: User's question
            conversation_history: Previous messages for context (optional)
            
        Returns:
            Complete prompt for Gemini
        """
        # Build rules text
        rules_text = "RELEVANT ASTROLOGICAL RULES:\n\n"
        for i, rule in enumerate(rules, 1):
            rules_text += f"Rule {i}: {rule['heading']} (Relevance: {rule['score']:.2f})\n"
            rules_text += f"{rule['content']}\n\n"
        
        # Build chart text
        chart_text = "USER'S HOROSCOPE CHART:\n"
        for planet, house in sorted(chart.items()):
            chart_text += f"- {planet} in House {house}\n"
        
        # Build conversation history text
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            history_text = "\n\nPREVIOUS CONVERSATION:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n\n"
            history_text += "Use this conversation history to understand context and answer follow-up questions.\n"
        
        prompt = f"""You are an expert astrologer. Your ONLY purpose is to answer questions about astrology based on the user's birth chart.

{rules_text}

{chart_text}
{history_text}

USER'S QUESTION:
{question}

CRITICAL INSTRUCTIONS:
1. FIRST, determine if this question is related to astrology or the user's birth chart
2. If the question is NOT about astrology, IMMEDIATELY respond with:
   "I am an astrology assistant and can only answer questions related to your birth chart and astrological predictions. Please ask me about topics like health, career, relationships, wealth, education, or other life aspects based on your horoscope."

3. REJECT and DO NOT ANSWER questions about:
   - General knowledge (e.g., "What is the capital of France?")
   - Current events or news
   - Technical topics (e.g., "How to code in Python?")
   - Medical advice beyond astrological insights
   - Legal advice
   - Financial investment advice
   - Any topic unrelated to astrology or the birth chart

4. ONLY ANSWER if the question is clearly about:
   - The user's birth chart or planetary positions
   - Astrological predictions for health, career, wealth, marriage, education
   - Astrological remedies
   - Planetary effects and influences
   - Life aspects based on astrology

5. USE THE CONVERSATION HISTORY to:
   - Understand what "it", "that", "this" refers to
   - Answer follow-up questions like "tell me more", "what about remedies?", "why?"
   - Provide context-aware responses

TASK (only if question is astrology-related):
Provide a clear, specific answer based on the rules above.
- Reference specific planet-house combinations
- Explain the reasoning from astrological principles
- Mention any remedies if applicable
- Be honest if the rules don't fully address the question
- If this is a follow-up question, build on previous answers

Keep your answer concise (3-5 sentences).

EXAMPLES OF QUESTIONS TO REJECT:
- "What's the weather today?"
- "How do I bake a cake?"
- "Who won the cricket match?"
- "Explain quantum physics"
- "What stocks should I buy?"

EXAMPLES OF QUESTIONS TO ANSWER:
- "Why am I facing health problems?"
- "When will I get married?"
- "What does my chart say about my career?"
- "Are there remedies for financial struggles?"
- "Tell me more about that" (follow-up)
- "What remedies can I do?" (follow-up)
"""
        
        return prompt

