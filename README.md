# LinkedIn Optimizer Chat

An AI-powered LinkedIn profile optimization tool built with Streamlit, LangGraph, and Groq API. This multi-agent system provides personalized recommendations for improving your LinkedIn profile.

## Features

- **Multi-Agent AI System**: Three specialized agents for profile optimization, career guidance, and content enhancement
- **Profile Analysis**: Complete assessment of profile completeness and improvement areas
- **Memory Persistence**: Conversations and profile data saved across sessions
- **Interactive Chat Interface**: Real-time chat with AI agents

## Architecture

```
├── agents.py                 # LangGraph multi-agent system
├── main.py                  # Streamlit main application
├── config/settings.py       # Configuration and environment variables
├── database/memory.py       # Database operations and memory management
├── services/agent_service.py # Agent routing and business logic
├── ui/                      # User interface components
└── utils/helpers.py         # Utility functions and session management
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (free tier available at https://console.groq.com/)

### Setup

1. **Clone and setup**
```bash
git clone https://github.com/yourusername/linkedin-optimizer-chat.git
cd linkedin-optimizer-chat
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Setup**
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

3. **Run**
```bash
streamlit run main.py
```

Application opens at `http://localhost:8501`

## Usage

1. Enter your LinkedIn profile information in the form
2. Chat with AI agents for:
   - Profile optimization advice
   - Career guidance and job matching
   - Content writing assistance

### Example Questions
- "How can I improve my LinkedIn profile?"
- "What jobs fit my background?"
- "Help me write a better headline"

## Key Dependencies

- `streamlit`: Web interface framework
- `langgraph`: Multi-agent orchestration
- `groq`: AI model API client
- `langchain-core`: LangChain core components
- `python-dotenv`: Environment variable management

## Data Storage

All data is stored locally in SQLite database (`linkedin_memory.db`) including:
- Profile information
- Chat conversations
- Session data

---

Built with Streamlit, LangGraph, and Groq AI