# Development Guide - LinkedIn Optimizer Chat

## Technology Stack

**Frontend: Streamlit**
- Rapid prototyping and built-in state management
- Easy deployment with rich UI components

**AI Framework: LangGraph** 
- Multi-agent orchestration with supervisor pattern
- Integration with LangChain ecosystem

**AI Model: Groq API (llama-3.1-8b-instant)**
- Fast inference (300+ tokens/sec) with generous free tier

**Database: SQLite**
- Zero-configuration setup, perfect for single-user applications

## Key Challenges & Solutions

### Agent Routing Accuracy
**Problem**: Simple keyword matching caused misrouted messages.

**Solution**: Enhanced keyword matching with multiple patterns:
```python
def determine_agent(self, user_message: str) -> Dict[str, str]:
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["optimize", "improve", "profile"]):
        return {"id": "profile_analyzer", ...}
    elif any(word in message_lower for word in ["job", "career", "role"]):
        return {"id": "job_fit_analyzer", ...}
```

### Context Window Management
**Problem**: Long conversations exceeded token limits.

**Solution**: Limit chat history to last 10 messages:
```python
for msg in chat_history[-10:]:  # Last 10 messages only
    if msg["role"] == "user":
        messages.append(HumanMessage(content=msg["content"]))
```

### Session State Management
**Problem**: Streamlit session state unpredictable with page reloads.

**Solution**: Comprehensive state initialization and database restoration:
```python
def init_session_state():
    # Initialize all required variables
    # Load from database if available

def load_existing_user_data(db_manager, user_id):
    # Restore profile data and chat history from database
```

## Development Setup

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GROQ_API_KEY

# Run application
streamlit run main.py
```

## Testing Approach

Manual testing focused on:

1. **User Journey Testing**: Profile creation, chat interactions, memory persistence
2. **Agent Response Quality**: Domain-specific questions and routing accuracy  
3. **Data Persistence**: Session state and database integrity


**Multi-layer persistence:**
- Session State (immediate)
- Database (persistent) 
- Context Building (intelligent)

## Performance Optimization

- Limit chat history to 50 messages maximum
- Index database columns for user_id and timestamp
- Clean up old sessions periodically (30+ days)

## Future Enhancements

- LinkedIn API integration for direct profile import
- Job board integration for real-time matching
- Export functionality (PDF resume generation)
- Multi-user authentication system