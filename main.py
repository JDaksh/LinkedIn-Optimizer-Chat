import streamlit as st
from config.settings import Config
from database.memory import init_memory_system
from services.agent_service import AgentService
from ui.sidebar import SidebarManager
from ui.chat import ChatInterface
from utils.helpers import init_session_state, load_existing_user_data

def main():
    """Main application function"""

    st.set_page_config(page_title="LinkedIn Optimizer Chat", layout="centered")
    st.title("💬 LinkedIn Optimizer Chat")
    st.markdown("*Enhance your LinkedIn profile with AI-powered insights and personalized recommendations*")
    
    Config.validate_env_vars()
    
    session_memory, db_manager = init_memory_system()
    agent_service = AgentService(db_manager)
    
    sidebar_manager = SidebarManager(db_manager)
    chat_interface = ChatInterface(agent_service, db_manager)
    
    init_session_state()
    
    st.caption(f"👤 User ID: {st.session_state.user_id}")
    
    load_existing_user_data(db_manager, st.session_state.user_id)
    
    _, _ = sidebar_manager.render_sidebar(
        st.session_state.user_id,
        [],  
        {},  
        st.session_state.profile_data
    )
    
    if not st.session_state.get('profile_data'):
        profile_data = chat_interface.render_profile_input()
    else:
        # Show existing profile summary
        with st.expander("📋 Current Profile Summary", expanded=False):
            profile = st.session_state.profile_data
            st.write(f"**Name:** {profile.get('fullName', 'N/A')}")
            st.write(f"**Headline:** {profile.get('headline', 'N/A')}")
            st.write(f"**Location:** {profile.get('location', 'N/A')}")
            
            if st.button("🔄 Update Profile"):
                st.session_state.profile_data = None
                st.rerun()
    
    # Render main chat interface with empty goals/preferences
    chat_interface.render_chat_interface(
        st.session_state.user_id,
        st.session_state.profile_data,
        [],
        {} 
    )

if __name__ == "__main__":
    main()