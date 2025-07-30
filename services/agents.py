import os
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
key = os.getenv("GROQ_API_KEY")
if not key:
    st.error("GROQ_API_KEY missing")
    st.stop()
client = Groq(api_key=key)

def call_groq(messages):
    formatted_messages = []
    for i, msg in enumerate(messages):
        if hasattr(msg, 'content') and hasattr(msg, 'type'):
            # LangGraph message object
            role = "user" if msg.type == "human" else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})
        elif isinstance(msg, dict) and "role" in msg and "content" in msg:
            formatted_messages.append(msg)
        else:
            print(f"❌ message[{i}] format not recognized: {msg}")
    
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=formatted_messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )
    return resp.choices[0].message.content

def profile_analyzer(state: MessagesState) -> Command:
    system_prompt = """You are a LinkedIn profile optimization expert. Analyze the provided LinkedIn profile data and provide specific, actionable feedback for improvement. Focus on:
    
    1. **Profile Completeness**: Missing sections, incomplete information
    2. **Professional Branding**: Headline, summary, photo quality
    3. **Experience Section**: Job descriptions, achievements, keywords
    4. **Skills & Endorsements**: Relevant skills, skill gaps
    5. **Network & Engagement**: Connection strategy, content sharing
    
    Provide specific recommendations with examples where possible."""
    
    content = call_groq(state["messages"] + [{"role": "system", "content": system_prompt}])
    return Command(goto=END, update={"messages": [{"role": "assistant", "content": content}]})

def job_fit_analyzer(state: MessagesState) -> Command:
    system_prompt = """You are a career advisor specializing in job-profile matching. Analyze the LinkedIn profile in context of job requirements. Focus on:
    
    1. **Skills Alignment**: Match between profile skills and job requirements
    2. **Experience Relevance**: How well past experience fits the target role
    3. **Industry Knowledge**: Relevant industry experience and knowledge gaps
    4. **Career Progression**: Logical career path and growth trajectory
    5. **Missing Elements**: What's needed to be competitive for target roles
    
    Provide a detailed analysis with improvement suggestions to better align with desired positions."""
    
    content = call_groq(state["messages"] + [{"role": "system", "content": system_prompt}])
    return Command(goto=END, update={"messages": [{"role": "assistant", "content": content}]})

def content_enhancer(state: MessagesState) -> Command:
    system_prompt = """You are a professional content writer specializing in LinkedIn optimization. Help enhance profile content for maximum impact. Focus on:
    
    1. **Headline Optimization**: Compelling, keyword-rich headlines
    2. **Summary/About Section**: Engaging professional narrative
    3. **Experience Descriptions**: Achievement-focused bullet points with metrics
    4. **Skills Presentation**: Strategic skill selection and ordering
    5. **Content Strategy**: Post ideas, article topics, engagement tactics
    
    Provide specific content suggestions, rewrites, and examples that will increase profile visibility and engagement."""
    
    content = call_groq(state["messages"] + [{"role": "system", "content": system_prompt}])
    return Command(goto=END, update={"messages": [{"role": "assistant", "content": content}]})

def supervisor(state: MessagesState) -> Command:
    # look at last user message for keywords
    last = state["messages"][-1].content.lower()
    
    if any(keyword in last for keyword in ["optimize", "improve", "profile", "completeness", "missing", "gaps"]):
        return Command(goto="profile_analyzer")
    elif any(keyword in last for keyword in ["job", "fit", "role", "position", "career", "match", "alignment"]):
        return Command(goto="job_fit_analyzer")
    elif any(keyword in last for keyword in ["content", "headline", "summary", "description", "writing", "enhance", "rewrite"]):
        return Command(goto="content_enhancer")
    else:
        # Default to profile analyzer for general questions
        return Command(goto="profile_analyzer")

# Build graph
graph = StateGraph(MessagesState)
graph.add_node(supervisor)
graph.add_node(profile_analyzer)
graph.add_node(job_fit_analyzer)
graph.add_node(content_enhancer)
graph.add_edge(START, "supervisor")
compiled_graph = graph.compile()
