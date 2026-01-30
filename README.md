# VastuAi

AI-powered Vedic astrology consultation application with conversational interface.

## 🎬 Demo

[📹 Watch Demo Video](assets/demo.mov) (1:41)

> **Note**: The video file is 35MB. Download it locally to view, or check the [releases](https://github.com/Rajan093/VastuAi/releases) for a compressed version.

## Technologies Used

- **Streamlit** - Web UI framework
- **Google Gemini** - LLM (gemini-3-flash-preview)
- **Pinecone** - Vector database
- **PySwissEph** - Planetary calculations
- **Geopy** - Geocoding (Nominatim)
- **PyMuPDF** - PDF processing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Add your API keys to `.env`:
```env
GEMINI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=lal-kitab-rules
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
VastuAi/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
└── src/
    ├── calculation/         # Geocoding, horoscope, house system
    ├── generation/          # Gemini client, prompt builder
    ├── ingestion/           # PDF loader, chunker, embeddings
    └── retrieval/           # Pinecone client, query builder
```

## Requirements

- Python 3.8+
- Gemini API key
- Pinecone API key
