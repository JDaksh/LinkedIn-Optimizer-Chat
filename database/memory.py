import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st
from config.settings import Config

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self.init_database()
    
    def init_database(self) -> sqlite3.Connection:
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # no dropping existing data
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                career_goals TEXT,
                preferences TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                last_active TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT DEFAULT 'default',
                interaction_type TEXT,
                query TEXT,
                response TEXT,
                agent_used TEXT,
                timestamp TIMESTAMP,
                context_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_data TEXT,
                created_at TIMESTAMP,
                last_activity TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            );
        ''')
        
        conn.commit()
        return conn
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def save_user_profile(self, user_id: str, profile_data: Optional[Dict], 
                         career_goals: Optional[List] = None, 
                         preferences: Optional[Dict] = None) -> None:
        """Save user profile to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, profile_data, career_goals, preferences, created_at, updated_at, last_active)
            VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM user_profiles WHERE user_id = ?), ?), ?, ?)
        ''', (
            user_id, 
            json.dumps(profile_data) if profile_data else None,
            json.dumps(career_goals) if career_goals else None,
            json.dumps(preferences) if preferences else None,
            user_id, now, now, now
        ))
        
        conn.commit()
        conn.close()
    
    def load_user_profile(self, user_id: str) -> Tuple[Optional[Dict], List, Dict]:
        """Load user profile from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT profile_data, career_goals, preferences 
            FROM user_profiles 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return (
                json.loads(result[0]) if result[0] else None,
                json.loads(result[1]) if result[1] else [],
                json.loads(result[2]) if result[2] else {}
            )
        
        return None, [], {}
    
    def save_interaction(self, user_id: str, query: str, response: str, agent_used: str, 
                        session_id: str = None, context_data: Dict = None) -> None:
        """Save user interaction to database with session tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_interactions (user_id, session_id, interaction_type, query, response, agent_used, timestamp, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            session_id or "default", 
            "chat", 
            query, 
            response, 
            agent_used, 
            datetime.now().isoformat(),
            json.dumps(context_data) if context_data else None
        ))
        
        # Update last active time
        cursor.execute('''
            UPDATE user_profiles SET last_active = ? WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_interaction_history(self, user_id: str, limit: int = 10, days_back: int = 30) -> List[Dict]:
        """Get recent user interactions within specified timeframe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get interactions from last N days
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        cursor.execute('''
            SELECT query, response, agent_used, timestamp, session_id, context_data
            FROM user_interactions 
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, cutoff_date, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'message': row[0],
                'response': row[1], 
                'agent_used': row[2],
                'timestamp': row[3],
                'session_id': row[4] or 'default',
                'context_data': json.loads(row[5]) if row[5] else {}
            }
            for row in results
        ]
    
    def save_session_data(self, session_id: str, user_id: str, session_data: Dict) -> None:
        """Save session data for persistence"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (session_id, user_id, session_data, created_at, last_activity, is_active)
            VALUES (?, ?, ?, COALESCE((SELECT created_at FROM user_sessions WHERE session_id = ?), ?), ?, 1)
        ''', (session_id, user_id, json.dumps(session_data), session_id, now, now))
        
        conn.commit()
        conn.close()
    
    def load_session_data(self, session_id: str) -> Optional[Dict]:
        """Load session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT session_data FROM user_sessions 
            WHERE session_id = ? AND is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else None
    
    def get_active_sessions_for_user(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent active sessions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT session_id, created_at, last_activity 
            FROM user_sessions 
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_activity DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'session_id': row[0],
                'created_at': row[1],
                'last_activity': row[2]
            }
            for row in results
        ]
    
    def clear_user_data(self, user_id: str) -> None:
        """Clear all user data from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_interactions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def cleanup_old_sessions(self, days_old: int = 30) -> None:
        """Clean up old inactive sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        cursor.execute('''
            UPDATE user_sessions SET is_active = 0 
            WHERE last_activity < ?
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()

@st.cache_resource
def init_memory_system():
    """Initialize memory system with database"""
    from langgraph.checkpoint.memory import MemorySaver
    db_manager = DatabaseManager()
    memory_saver = MemorySaver()
    return memory_saver, db_manager