import streamlit as st
from typing import Dict, List
import uuid

def generate_user_id():
    """Generate a consistent user ID based on session or create new one"""
    # Try to get existing user ID from session state first
    if "user_id" in st.session_state:
        return st.session_state.user_id
    
    # For demo purposes, create a simple persistent user ID
    if "persistent_user_id" not in st.session_state:
        st.session_state.persistent_user_id = "user_demo_001"  # Simple demo user
    
    return st.session_state.persistent_user_id

def init_session_state():
    """Initialize session state variables"""
    # Generate or retrieve user ID
    if "user_id" not in st.session_state:
        st.session_state.user_id = generate_user_id()
    
    defaults = {
        "session_id": str(uuid.uuid4()),
        "chat_history": [],
        "profile_data": None,
        "profile_url": "",
        "conversation_context": [],
        "memory_loaded": False  # Flag to track if memory has been loaded
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_existing_user_data(db_manager, user_id: str):
    """Load existing user data from database and restore chat history"""
    if not st.session_state.get('memory_loaded', False):
        try:
            # Load profile data only (ignoring goals and preferences)
            existing_profile, _, _ = db_manager.load_user_profile(user_id)
            
            # Always load profile data if it exists in database
            if existing_profile and not st.session_state.get('profile_data'):
                st.session_state.profile_data = existing_profile
                st.info("✅ Previous profile data restored!")
            
            # Load recent chat history for continuity
            recent_interactions = db_manager.get_user_interaction_history(user_id, 20)
            if recent_interactions and len(st.session_state.chat_history) == 0:
                # Convert database interactions to chat history format
                restored_history = []
                for interaction in reversed(recent_interactions):
                    # Add user message
                    restored_history.append({
                        "role": "user",
                        "content": interaction['message']
                    })
                    # Add assistant response
                    restored_history.append({
                        "role": "assistant", 
                        "content": interaction['response'],
                        "agent": interaction['agent_used'],
                        "agent_display": get_agent_display_name(interaction['agent_used'])
                    })
                
                st.session_state.chat_history = restored_history
                if len(restored_history) > 0:
                    st.info(f"✅ Previous conversation restored! ({len(restored_history)//2} messages)")
            
            # Mark memory as loaded
            st.session_state.memory_loaded = True
            
        except Exception as e:
            st.warning(f"⚠️ Could not load previous data: {str(e)}")
            st.session_state.memory_loaded = True

def get_agent_display_name(agent_id: str) -> str:
    """Get display name for agent"""
    agent_names = {
        "profile_analyzer": "📊 Profile Optimizer",
        "job_fit_analyzer": "🎯 Career Advisor",
        "content_enhancer": "✍️ Content Writer"
    }
    return agent_names.get(agent_id, "🤖 AI Agent")

def force_save_current_state(db_manager, user_id: str):
    """Force save current session state to database"""
    try:
        db_manager.save_user_profile(
            user_id,
            st.session_state.get('profile_data'),
            [],  # Empty career goals
            {}   # Empty preferences
        )
        return True
    except Exception as e:
        st.error(f"Failed to save state: {e}")
        return False