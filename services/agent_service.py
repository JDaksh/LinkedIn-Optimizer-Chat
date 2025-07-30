import json
from datetime import datetime
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from config.settings import Config
import streamlit as st

# Trying to import agents, mock if unavailable
try:
    from services.agents import compiled_graph
except ImportError:
    class MockCompiledGraph:
        def invoke(self, input_data):
            return {"messages": [AIMessage(content="I'm here to help optimize your LinkedIn profile! Ask me about profile improvements, career advice, or content writing.")]}
    
    compiled_graph = MockCompiledGraph()

class AgentService:
    """Handles agent routing and communication"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def determine_agent(self, user_message: str) -> Dict[str, str]:
        """Determine which agent should handle the message"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["optimize", "improve", "profile", "completeness", "gaps"]):
            return {
                "id": "profile_analyzer", 
                "name": "Profile Optimizer", 
                "emoji": "📊", 
                "display": "📊 Profile Optimizer"
            }
        elif any(word in message_lower for word in ["job", "fit", "role", "career", "match", "alignment"]):
            return {
                "id": "job_fit_analyzer", 
                "name": "Career Advisor", 
                "emoji": "🎯", 
                "display": "🎯 Career Advisor"
            }
        elif any(word in message_lower for word in ["content", "headline", "summary", "writing", "enhance"]):
            return {
                "id": "content_enhancer", 
                "name": "Content Writer", 
                "emoji": "✍️", 
                "display": "✍️ Content Writer"
            }
        else:
            return {
                "id": "profile_analyzer", 
                "name": "Profile Optimizer", 
                "emoji": "📊", 
                "display": "📊 Profile Optimizer"
            }
    
    def build_system_context(self, user_id: str, profile_data: Dict, 
                           career_goals: List, user_preferences: Dict) -> str:
        """Build system context for agents with memory"""
        interaction_history = self.db_manager.get_user_interaction_history(user_id, 20, 7)  # Last 20 interactions from past 7 days
        
        # Build context from recent interactions
        recent_topics = []
        if interaction_history:
            for interaction in interaction_history[:5]:  # Last 5 interactions
                recent_topics.append(f"User asked: {interaction['message'][:100]}...")
        
        context = f"""
        You are LearnTube's AI Career Coach with access to the user's LinkedIn profile and conversation history.
        
        USER PROFILE:
        - Name: {profile_data.get('fullName', 'Not provided') if profile_data else 'No profile data'}
        - Headline: {profile_data.get('headline', 'Not provided') if profile_data else 'No headline'}
        - Career Goals: {', '.join(career_goals) if career_goals else 'None specified'}
        - Experience Level: {user_preferences.get('experience_level', 'Mid Level')}
        - Focus Areas: {', '.join(user_preferences.get('focus_areas', [])) if user_preferences.get('focus_areas') else 'None specified'}
        
        RECENT CONVERSATION HISTORY:
        {chr(10).join(recent_topics) if recent_topics else 'No previous conversations'}
        
        MEMORY CONTEXT:
        - Total interactions: {len(interaction_history)}
        - User has been active over multiple sessions
        - Maintain continuity with previous conversations
        
        PROFILE DATA:
        {json.dumps(profile_data, indent=2) if profile_data else 'No profile data available'}
        
        Provide personalized, actionable advice. Reference previous conversations when relevant to show continuity.
        """
        
        return context
    
    def process_message(self, user_message: str, chat_history: List, 
                       user_id: str, profile_data: Dict, 
                       career_goals: List, user_preferences: Dict) -> tuple:
        """Process user message and get agent response with memory persistence"""
        try:
            # Determine agent
            agent_info = self.determine_agent(user_message)
            
            # Build context with memory
            system_context = self.build_system_context(
                user_id, profile_data, career_goals, user_preferences
            )
            
            messages = [AIMessage(content=system_context)]
            
            for msg in chat_history[-10:]:  # Last 10 messages to maintain context
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            messages.append(HumanMessage(content=user_message))
            
            # Get response from agents
            result = compiled_graph.invoke({"messages": messages})
            
            if result and "messages" in result and result["messages"]:
                assistant_message = result["messages"][-1].content
                
                # Prepare context data for storage
                context_data = {
                    "agent_id": agent_info["id"],
                    "career_goals": career_goals,
                    "user_preferences": user_preferences,
                    "profile_available": bool(profile_data)
                }
                
                # Save interaction with session and context
                self.db_manager.save_interaction(
                    user_id, 
                    user_message, 
                    assistant_message, 
                    agent_info["id"],
                    st.session_state.get('session_id'),
                    context_data
                )
                
                # Save session data periodically
                self._save_session_state(user_id)
                
                return assistant_message, agent_info
            else:
                raise Exception("No response received from agents")
                
        except Exception as e:
            raise Exception(f"Error processing message: {str(e)}")
    
    def _save_session_state(self, user_id: str):
        """Save current session state to database"""
        session_data = {
            "chat_history_length": len(st.session_state.get('chat_history', [])),
            "profile_data_available": bool(st.session_state.get('profile_data')),
            "career_goals_count": len(st.session_state.get('career_goals', [])),
            "last_activity": datetime.now().isoformat()
        }
        
        self.db_manager.save_session_data(
            st.session_state.get('session_id'),
            user_id,
            session_data
        )