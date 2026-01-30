"""
AstroChat - Conversational Astrology AI
ChatGPT-like interface for astrological readings.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import tempfile
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.calculation.horoscope import HoroscopeCalculator
from src.retrieval.pinecone_client import PineconeClient
from src.generation.gemini_client import GeminiClient
from src.ingestion.pdf_loader import TextLoader
from src.ingestion.chunker import LalKitabChunker
from src.ingestion.embeddings import EmbeddingsGenerator


# Page config
st.set_page_config(
    page_title="AstroChat - AI Astrologer",
    page_icon="🔮",
    layout="centered",
)

# Custom CSS - Refined Light Theme
st.markdown("""
<style>
    /* =========================================================
       AstroChat – Clean Light Theme (Refined)
       ========================================================= */

    /* ---------- CSS VARIABLES ---------- */
    :root {
        --bg-main: #ffffff;
        --bg-soft: #f7f7f8;
        --border-light: #e5e5e5;
        --border-mid: #d1d1d1;
        --text-main: #000000;
        --text-muted: #666666;
        --accent: #10a37f;
        --accent-hover: #0e8c6d;
        --radius-lg: 14px;
        --radius-md: 10px;
    }

    /* ---------- APP LAYOUT ---------- */
    .stApp {
        background-color: var(--bg-main);
    }

    .main .block-container {
        max-width: 720px;
        padding: 3rem 1.25rem 6rem;
        margin: auto;
    }

    /* ---------- HEADER ---------- */
    .chat-header {
        text-align: center;
        padding-bottom: 1.75rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-light);
    }

    .chat-header h1 {
        font-size: 2rem;
        font-weight: 600;
        color: var(--text-main);
        margin-bottom: 0.25rem;
    }

    .chat-header p {
        font-size: 0.9rem;
        color: var(--text-muted);
    }

    /* ---------- CHAT MESSAGES ---------- */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
        margin: 0.75rem 0 !important;
    }

    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: var(--bg-soft) !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: var(--radius-lg);
    }

    .stChatMessage[data-testid="chat-message-user"] {
        background-color: var(--bg-main) !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
    }

    .stChatMessage .stMarkdown {
        color: var(--text-main);
        font-size: 1rem;
        line-height: 1.6;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background-color: var(--bg-soft);
        border-right: 1px solid var(--border-light);
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-main);
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p {
        font-size: 0.9rem;
        color: var(--text-main);
    }

    [data-testid="stSidebar"] .stCaption {
        color: var(--text-muted) !important;
    }

    /* ---------- CHAT INPUT ---------- */
    .stChatInputContainer {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 720px;
        background: var(--bg-main);
        border-top: 1px solid var(--border-light);
        padding: 1rem;
        z-index: 100;
    }

    .stChatInput textarea {
        background-color: var(--bg-main) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem !important;
        min-height: 48px;
    }

    .stChatInput textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    .stChatInput textarea::placeholder {
        color: #999999;
    }

    /* ---------- BUTTONS ---------- */
    .stButton button {
        background-color: var(--accent);
        color: #ffffff;
        border-radius: var(--radius-md);
        padding: 0.6rem 1rem;
        font-weight: 500;
        border: none;
        transition: background-color 0.2s ease;
    }

    .stButton button:hover {
        background-color: var(--accent-hover);
    }

    /* ---------- EXPANDERS ---------- */
    .streamlit-expanderHeader {
        background-color: var(--bg-soft);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        color: var(--text-main) !important;
    }

    .streamlit-expanderHeader:hover {
        background-color: #ececec;
    }

    /* ---------- FILE UPLOADER ---------- */
    .stFileUploader label {
        font-weight: 500;
        color: var(--text-main) !important;
    }

    .stFileUploader [data-testid="stFileUploadDropzone"] {
        background-color: var(--bg-soft);
        border: 1px dashed var(--border-mid);
        border-radius: var(--radius-md);
    }

    .stFileUploader [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--accent);
    }

    /* ---------- SCROLLBAR ---------- */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-soft);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-mid);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }

    /* ---------- MISC ---------- */
    hr {
        border-color: var(--border-light);
        margin: 1.5rem 0;
    }

    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chart' not in st.session_state:
    st.session_state.chart = None
if 'birth_data' not in st.session_state:
    st.session_state.birth_data = None
if 'awaiting_birth_data' not in st.session_state:
    st.session_state.awaiting_birth_data = False
if 'initial_summary_shown' not in st.session_state:
    st.session_state.initial_summary_shown = False


def main():
    """Main application."""
    
    # Sidebar for admin functions
    with st.sidebar:
        st.title("🔮 AstroChat")
        st.caption("*Your AI Astrologer*")
        st.divider()
        
        # Admin section
        with st.expander("📚 Upload New PDF", expanded=False):
            st.caption("Add astrology books to database")
            uploaded_file = st.file_uploader("PDF file", type=['pdf'], label_visibility="collapsed")
            if uploaded_file and st.button("Upload"):
                process_pdf(uploaded_file)
        
        # Chart info if available
        if st.session_state.chart:
            with st.expander("🌟 Your Birth Chart", expanded=False):
                for planet, house in sorted(st.session_state.chart.items()):
                    st.text(f"{planet}: House {house}")
        
        # Clear chat
        if st.button("🗑️ New Reading"):
            st.session_state.messages = []
            st.session_state.chart = None
            st.session_state.birth_data = None
            st.session_state.awaiting_birth_data = False
            st.session_state.initial_summary_shown = False
            st.rerun()
    
    # Main chat interface
    st.markdown('<div class="chat-header"><h1>🔮 AstroChat</h1><p>Your Personal AI Astrologer</p></div>', unsafe_allow_html=True)
    
    # Welcome message
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Welcome! I'm your AI astrologer. I can provide personalized astrological insights based on your birth chart.\n\nTo get started, please tell me:\n- Your birth date (e.g., January 15, 1990)\n- Your birth time (e.g., 10:30 AM)\n- Your birth place (e.g., Ahmedabad)"
        })
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_user_message(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


def process_user_message(message: str) -> str:
    """Process user message and generate response."""
    
    # If we don't have birth data yet, try to extract it using LLM
    if not st.session_state.birth_data:
        birth_data_result = extract_birth_data_with_llm(message)
        
        if birth_data_result['status'] == 'complete':
            # We have all birth data
            st.session_state.birth_data = birth_data_result['data']
            
            # Generate chart
            try:
                chart = generate_chart(birth_data_result['data'])
                st.session_state.chart = chart
                
                # Generate initial summary
                summary = generate_initial_summary(chart)
                st.session_state.initial_summary_shown = True
                
                return f"✅ Got it! Let me calculate your birth chart for {birth_data_result['data']['place']}...\n\n{summary}\n\n💬 Feel free to ask me any questions about your chart!"
                
            except Exception as e:
                st.session_state.birth_data = None  # Reset on error
                return f"❌ I couldn't calculate your birth chart. Error: {str(e)}\n\nPlease provide your birth details again."
        
        elif birth_data_result['status'] == 'incomplete':
            # Some fields are missing
            missing = birth_data_result['missing_fields']
            missing_str = ", ".join(missing)
            return f"I need more information. Please provide:\n\n" + "\n".join([f"• {field.title()}" for field in missing])
        
        else:
            # Non-astrology question asked before providing birth data
            return birth_data_result['message']
    
    # If we have birth data, validate question is astrology-related
    else:
        # Check if question is astrology-related
        is_astrology = validate_astrology_question(message)
        
        if not is_astrology:
            return "I am an astrology assistant and can only answer questions related to your birth chart and astrological predictions. Please ask me about topics like health, career, relationships, wealth, education, or other life aspects based on your horoscope."
        
        # Answer the question
        try:
            answer = answer_question(message, st.session_state.messages)
            return answer
        except Exception as e:
            return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question."


def extract_birth_data_with_llm(message: str) -> dict:
    """
    Use LLM to extract birth data from natural language.
    Returns: {
        'status': 'complete' | 'incomplete' | 'non_astrology',
        'data': {...} or None,
        'missing_fields': [...] or None,
        'message': str or None
    }
    """
    
    prompt = f"""You are a birth data extraction assistant. Extract birth information from the user's message.

USER MESSAGE:
{message}

TASK:
1. Check if the message is trying to provide birth details (date, time, place)
2. If it's clearly NOT about birth details (e.g., "what's the weather?", "tell me a joke"), return "non_astrology"
3. Otherwise, extract whatever birth information is present

Extract and return in this EXACT JSON format:
{{
    "date": "YYYY-MM-DD" or null,
    "time": "HH:MM" (24-hour) or null,
    "place": "City name" or null
}}

RULES:
- Convert ANY date format to YYYY-MM-DD (e.g., "jan 16 2004" → "2004-01-16", "16/1/04" → "2004-01-16")
- Convert ANY time format to HH:MM in 24-hour (e.g., "10.30 AM" → "10:30", "2:30 PM" → "14:30")
- Handle month abbreviations (jan → january)
- Fix common place name typos (Ahmadabad → Ahmedabad)
- Assume 2000s for 2-digit years (04 → 2004)
- If a field is not mentioned, set it to null
- Return ONLY the JSON, nothing else

EXAMPLES:
Input: "date: jan 16 2004 time: 10.30 place: Ahmedabad"
Output: {{"date": "2004-01-16", "time": "10:30", "place": "Ahmedabad"}}

Input: "I was born on 15-1-1990 at 10:30 AM in Mumbai"
Output: {{"date": "1990-01-15", "time": "10:30", "place": "Mumbai"}}

Input: "born 16 jan 2004"
Output: {{"date": "2004-01-16", "time": null, "place": null}}

Input: "what's the weather today?"
Output: "non_astrology"
"""
    
    try:
        gemini_client = GeminiClient()
        response = gemini_client.generate_response(prompt, temperature=0.1)
        
        # Check if response is "non_astrology"
        if response.strip().lower() == "non_astrology":
            return {
                'status': 'non_astrology',
                'data': None,
                'missing_fields': None,
                'message': "I'm an astrology assistant. To get started, please provide your birth date, time, and place."
            }
        
        # Parse JSON response
        import json
        data = json.loads(response.strip())
        
        # Check which fields are missing
        missing = []
        if not data.get('date'):
            missing.append('birth date')
        if not data.get('time'):
            missing.append('birth time')
        if not data.get('place'):
            missing.append('birth place')
        
        if missing:
            return {
                'status': 'incomplete',
                'data': None,
                'missing_fields': missing,
                'message': None
            }
        
        # All fields present
        return {
            'status': 'complete',
            'data': {
                'date': data['date'],
                'time': data['time'],
                'place': data['place'],
                'timezone': 5.5  # Default to IST
            },
            'missing_fields': None,
            'message': None
        }
        
    except Exception as e:
        # If LLM fails, assume incomplete
        return {
            'status': 'incomplete',
            'data': None,
            'missing_fields': ['birth date', 'birth time', 'birth place'],
            'message': None
        }


def validate_astrology_question(question: str) -> bool:
    """
    Use LLM to validate if a question is astrology-related.
    Returns True if astrology-related, False otherwise.
    """
    
    prompt = f"""You are a question validator. Determine if this question is related to astrology or not.

USER QUESTION:
{question}

ASTROLOGY-RELATED topics include:
- Birth chart, planetary positions, houses
- Health, career, wealth, marriage, education predictions
- Astrological remedies
- Life aspects based on horoscope
- Personality traits from astrology

NON-ASTROLOGY topics include:
- General knowledge, current events, news
- Technical/coding questions
- Weather, recipes, jokes
- Medical/legal/financial advice (not astrological)
- Anything unrelated to the user's horoscope

Return ONLY "yes" if astrology-related, or "no" if not.
"""
    
    try:
        gemini_client = GeminiClient()
        response = gemini_client.generate_response(prompt, temperature=0.1)
        return response.strip().lower() == "yes"
    except:
        # If validation fails, assume it's astrology (be permissive)
        return True


def generate_chart(birth_data: dict) -> dict:
    """Generate horoscope chart from birth data."""
    calculator = HoroscopeCalculator()
    chart = calculator.calculate_chart_by_place(
        date=birth_data['date'],
        time=birth_data['time'],
        place_name=birth_data['place'],
        timezone_offset=birth_data['timezone']
    )
    return chart


def generate_initial_summary(chart: dict) -> str:
    """Generate initial 4-aspect summary."""
    
    # Retrieve rules
    pinecone_client = PineconeClient()
    pinecone_client.connect_to_index()
    rules = pinecone_client.query_by_chart(chart)
    
    if len(rules) == 0:
        return "⚠️ I don't have any astrological data in my database yet. Please upload a PDF first."
    
    # Generate summary
    gemini_client = GeminiClient()
    summary = gemini_client.generate_summary(
        rules=rules,
        chart=chart,
        aspects=["Health", "Education", "Wealth", "Marriage"]
    )
    
    # Format as markdown
    output = "## 🌟 Your Astrological Summary\n\n"
    
    aspects_icons = {
        "Health": "❤️",
        "Education": "📚",
        "Wealth": "💰",
        "Marriage": "💑"
    }
    
    for aspect in ["Health", "Education", "Wealth", "Marriage"]:
        icon = aspects_icons.get(aspect, "•")
        output += f"### {icon} {aspect}\n\n"
        output += summary.get(aspect, "No information available") + "\n\n"
    
    return output


def answer_question(question: str, conversation_history: List[Dict] = None) -> str:
    """Answer follow-up question using hybrid search with conversation history."""
    
    # Generate question embedding
    embedder = EmbeddingsGenerator()
    question_embedding = embedder.generate_embedding(question)
    
    # Hybrid query
    pinecone_client = PineconeClient()
    pinecone_client.connect_to_index()
    
    results = pinecone_client.query_by_chart_and_question(
        chart=st.session_state.chart,
        question_embedding=question_embedding,
        top_k=3
    )
    
    # Generate answer with conversation history
    gemini_client = GeminiClient()
    from src.generation.prompt_builder import PromptBuilder
    
    prompt = PromptBuilder.build_question_prompt(
        rules=results,
        chart=st.session_state.chart,
        question=question,
        conversation_history=conversation_history
    )
    
    answer = gemini_client.generate_response(prompt, temperature=0.7)
    return answer


def process_pdf(uploaded_file):
    """Process and ingest PDF."""
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        with st.spinner("Processing PDF..."):
            # Load PDF
            loader = TextLoader()
            text = loader.load_text(tmp_path)
            
            # Extract chunks
            chunker = LalKitabChunker()
            chunks = chunker.extract_chunks(text)
            
            # Generate embeddings
            embedder = EmbeddingsGenerator()
            embedded_chunks = embedder.embed_chunks(chunks, show_progress=False)
            
            # Upload to Pinecone
            pinecone_client = PineconeClient()
            pinecone_client.create_index(dimension=768)
            result = pinecone_client.upsert_chunks(embedded_chunks, show_progress=False)
            
            st.success(f"✅ Uploaded {result['total_uploaded']} rules to database!")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
