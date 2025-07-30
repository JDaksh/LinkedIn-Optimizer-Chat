import streamlit as st
from typing import Dict, List
from config.settings import Config
from datetime import datetime

class SidebarManager:
    """Manages sidebar UI components"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def render_sidebar(self, user_id: str, career_goals: List, user_preferences: Dict, profile_data: Dict) -> tuple:
        """Render complete sidebar"""
        with st.sidebar:
            st.header("🧠 Memory & Session Info")
            
            self._render_session_info(user_id)
            
            self._render_memory_controls(user_id)
            
            # Return empty values since we removed the sections
            return [], {}
    
    def _render_session_info(self, user_id: str):
        """Render session information with memory status"""
        with st.expander("🆔 Session & Memory Info", expanded=False):
            st.write(f"**User ID:** `{user_id}`")
            st.write(f"**Session ID:** `{st.session_state.get('session_id', 'N/A')[:12]}...`")
            
            # Get interaction history stats
            try:
                history_count = len(self.db_manager.get_user_interaction_history(user_id, 1000))
                recent_count = len(self.db_manager.get_user_interaction_history(user_id, 50, 7))
                st.write(f"**Total Interactions:** {history_count}")
                st.write(f"**This Week:** {recent_count}")
            except Exception as e:
                st.write(f"**Total Interactions:** Error loading")
                st.write(f"**This Week:** 0")
            
            memory_loaded = st.session_state.get('memory_loaded', False)
            memory_status = "✅ Loaded" if memory_loaded else "❌ Not Loaded"
            st.write(f"**Memory Status:** {memory_status}")
            
            has_profile = bool(st.session_state.get('profile_data'))
            profile_status = "✅ Available" if has_profile else "❌ Not Set"
            st.write(f"**Profile Status:** {profile_status}")
            
            chat_count = len(st.session_state.get('chat_history', []))
            st.write(f"**Current Chat Messages:** {chat_count}")
            
            if st.button("💾 Manual Save"):
                try:
                    self.db_manager.save_user_profile(
                        user_id,
                        st.session_state.get('profile_data'),
                        [],  # Empty career goals
                        {}   # Empty preferences
                    )
                    st.success("✅ Manually saved!")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
    
    def _render_memory_controls(self, user_id: str):
        """Render memory management controls"""
        st.subheader("💾 Memory Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Session"):
                # Start new session but keep user memory
                st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.chat_history = []
                st.session_state.memory_loaded = False
                st.success("New session started!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Memory"):
                self.db_manager.clear_user_data(user_id)
                st.session_state.clear()
                st.success("All memory cleared!")
                st.rerun()