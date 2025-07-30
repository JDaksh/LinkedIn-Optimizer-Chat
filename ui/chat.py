import streamlit as st
from typing import Dict, List
from config.settings import Config
import json

class ChatInterface:
    """Manages chat interface components"""
    
    def __init__(self, agent_service, db_manager):
        self.agent_service = agent_service
        self.db_manager = db_manager
    
    def render_agent_guide(self):
        """Render agent guide section"""
        with st.expander("🧠 Meet Your AI Agents", expanded=False):
            st.write("**Your personalized AI team is ready to help! Each agent specializes in different areas:**")
            
            # Display agents in columns
            cols = st.columns(3)
            for idx, agent in enumerate(Config.AGENT_CONFIGS):
                with cols[idx]:
                    st.write(f"**{agent['title']}**")
                    st.write(f"*{agent['description']}*")
                    st.write("**Ask about:**")
                    for skill in agent['skills']:
                        st.write(f"• {skill}")
            
            st.info("💡 **Tip:** The system automatically routes your question to the most relevant agent based on your keywords!")
    
    def render_profile_input(self):
        """Render manual profile input section"""
        st.header("📝 LinkedIn Profile Information")
        
        return self._render_manual_input()
    
    def _render_manual_input(self):
        """Render manual profile input method"""
        st.write("**Enter your LinkedIn profile information:**")
        
        with st.form("manual_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Basic Information")
                full_name = st.text_input("Full Name *", placeholder="John Doe")
                headline = st.text_input("Professional Headline *", placeholder="Senior Software Engineer at Microsoft")
                location = st.text_input("Location", placeholder="Seattle, WA")
            
            with col2:
                st.subheader("Current Position")
                current_title = st.text_input("Current Job Title", placeholder="Senior Software Engineer")
                current_company = st.text_input("Current Company", placeholder="Microsoft")
                current_duration = st.text_input("Duration", placeholder="Jan 2020 - Present")
            
            # Education section moved to full width
            st.subheader("Education")
            col3, col4 = st.columns(2)
            with col3:
                education_school = st.text_input("School/University", placeholder="University of Washington")
                education_degree = st.text_input("Degree", placeholder="Bachelor of Science in Computer Science")
            with col4:
                education_year = st.text_input("Graduation Year", placeholder="2018")
            
            summary = st.text_area(
                "Professional Summary/About",
                placeholder="Write a brief summary of your professional background, skills, and career goals...",
                height=100
            )
            
            skills_input = st.text_area(
                "Skills (comma-separated)",
                placeholder="Python, JavaScript, React, Node.js, AWS, Docker, Machine Learning",
                help="Enter your skills separated by commas"
            )
            
            st.subheader("Additional Work Experience (Optional)")
            additional_experience = st.text_area(
                "Previous positions",
                placeholder="• Software Developer at ABC Corp (2018-2020)\n• Intern at XYZ Inc (Summer 2017)",
                height=80
            )
            
            submit_manual = st.form_submit_button("📝 Create Profile", type="primary")
            
            if submit_manual and full_name and headline:
                return self._create_manual_profile(
                    full_name, headline, location,
                    current_title, current_company, current_duration,
                    education_school, education_degree, education_year,
                    summary, skills_input, additional_experience
                )
            elif submit_manual:
                st.error("Please fill in at least Full Name and Professional Headline (marked with *)")
        
        return None
    
    def _create_manual_profile(self, full_name, headline, location,
                              current_title, current_company, current_duration,
                              education_school, education_degree, education_year,
                              summary, skills_input, additional_experience):
        """Create profile data from manual input"""
        
        # Process experience
        experience = []
        if current_title and current_company:
            experience.append({
                "title": current_title,
                "company": current_company,
                "duration": current_duration or "Present",
                "description": f"Currently working as {current_title} at {current_company}"
            })
        
        if additional_experience:
            for exp_line in additional_experience.strip().split('\n'):
                if exp_line.strip():
                    experience.append({
                        "title": "Previous Role",
                        "company": "Previous Company",
                        "duration": "Previous",
                        "description": exp_line.strip()
                    })
        
        education = []
        if education_school:
            education.append({
                "school": education_school,
                "degree": education_degree or "Degree",
                "year": education_year or "N/A",
                "details": f"Studied at {education_school}"
            })
        
        skills = []
        if skills_input:
            skill_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            skills = [{"name": skill, "endorsements": 0} for skill in skill_list]
        
        profile_data = {
            "fullName": full_name,
            "headline": headline,
            "location": location or "Not specified",
            "summary": summary or f"Professional with experience in {headline.lower()}",
            "experience": experience,
            "education": education,
            "skills": skills,
            "input_method": "manual"
        }
        
        # Save to session state
        st.session_state.profile_data = profile_data
        st.session_state.profile_url = f"manual_entry_{full_name.replace(' ', '_').lower()}"
        
        # IMMEDIATELY save to database for persistence
        try:
            self.db_manager.save_user_profile(
                st.session_state.user_id,
                profile_data,
                st.session_state.get('career_goals', []),
                st.session_state.get('user_preferences', {})
            )
            st.success("✅ Profile created and saved successfully!")
        except Exception as e:
            st.warning(f"⚠️ Profile created but not saved to database: {e}")
            st.success("✅ Profile created successfully!")
        
        self._display_profile_preview(profile_data)
        
        # Add initial context to chat
        self._add_initial_chat_context(profile_data)
        
        return profile_data
    
    def _display_profile_preview(self, profile_data: Dict):
        """Display profile preview"""
        with st.expander("📊 Profile Preview", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**👤 Name:**", profile_data.get("fullName", "N/A"))
                st.write("**💼 Headline:**", profile_data.get("headline", "N/A"))
                st.write("**📍 Location:**", profile_data.get("location", "N/A"))
            with col2:
                st.write("**🎯 Skills Count:**", len(profile_data.get("skills", [])))
                st.write("**💼 Experience Count:**", len(profile_data.get("experience", [])))
                st.write("**🎓 Education Count:**", len(profile_data.get("education", [])))
            
            if profile_data.get("summary"):
                st.write("**📝 Summary:**")
                st.write(profile_data["summary"][:200] + "..." if len(profile_data["summary"]) > 200 else profile_data["summary"])
    
    def _add_initial_chat_context(self, profile_data: Dict):
        """Add initial context to chat history"""
        profile_summary = f"""
        Profile Analysis for: {profile_data.get('fullName', 'Unknown')}
        Headline: {profile_data.get('headline', 'N/A')}
        Experience: {len(profile_data.get('experience', []))} positions
        Skills: {len(profile_data.get('skills', []))} skills listed
        """
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"Great! I've analyzed your profile information. Here's what I found:\n\n{profile_summary}\n\nHow can I help you optimize your profile?",
            "agent": "profile_analyzer",
            "agent_display": "📊 Profile Optimizer"
        })
    
    def render_chat_interface(self, user_id: str, profile_data: Dict, 
                            career_goals: List, user_preferences: Dict):
        """Render main chat interface"""
        st.header("💬 AI Career Coach Chat")
        
        self.render_agent_guide()
        
        if profile_data:
            with st.expander(f"✍️ Current Profile: {profile_data.get('fullName', 'N/A')}", expanded=False):
                st.write(f"**Name:** {profile_data.get('fullName', 'N/A')}")
                st.write(f"**Headline:** {profile_data.get('headline', 'N/A')}")
                st.write(f"**Location:** {profile_data.get('location', 'N/A')}")
                
                if profile_data.get('experience'):
                    st.write("**Recent Experience:**")
                    for exp in profile_data['experience'][:2]:  # Show first 2 experiences
                        st.write(f"• {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                
                if profile_data.get('skills'):
                    st.write(f"**Skills:** {', '.join([skill.get('name', '') for skill in profile_data['skills'][:5]])}...")
                
                # Button to show full JSON for debugging
                if st.button("🔍 Show Full Profile Data"):
                    st.json(profile_data)
        
        user_prompt = st.chat_input("Ask about your LinkedIn profile optimization...")
        
        if user_prompt:
            self._process_chat_message(user_prompt, user_id, profile_data, career_goals, user_preferences)
        
        # Display chat history
        self._display_chat_history()
    
    def _process_chat_message(self, user_prompt: str, user_id: str, profile_data: Dict, 
                            career_goals: List, user_preferences: Dict):
        """Process user chat message"""
        try:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            
            # Get agent response
            with st.spinner("🤖 Processing your request..."):
                assistant_message, agent_info = self.agent_service.process_message(
                    user_prompt, st.session_state.chat_history, 
                    user_id, profile_data, career_goals, user_preferences
                )
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "agent": agent_info["id"],
                    "agent_display": agent_info["display"]
                })
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    def _display_chat_history(self):
        """Display chat history with agent information"""
        st.subheader("💭 Conversation History")
        
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(f"**You:** {message['content']}")
                else:
                    with st.chat_message("assistant"):
                        agent_display = message.get("agent_display", "🤖 AI Agent")
                        agent_name = message.get("agent", "unknown")
                        
                        st.markdown(f"**{agent_display}** responded:")
                        
                        if agent_name in Config.AGENT_DESCRIPTIONS:
                            st.caption(f"_{Config.AGENT_DESCRIPTIONS[agent_name]}_")
                        
                        st.write(message['content'])
            
            # Show session statistics
            user_messages = [m for m in st.session_state.chat_history if m['role'] == 'user']
            st.info(f"💡 **Session Stats:** {len(user_messages)} questions asked in this session")
        else:
            st.info("👋 Start a conversation by asking about your LinkedIn profile optimization!")