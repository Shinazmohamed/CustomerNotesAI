import streamlit as st
import pandas as pd
import json
import os
from database import get_user_by_username

def initialize_auth():
    """Initialize authentication-related session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
        
# Initialize authentication at module load time
# This ensures session state variables are set in all pages
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

def authenticate_user(username, password):
    """
    Authenticate a user based on username and password
    In a production app, use proper authentication and password hashing
    """
    # Get user from database by username
    user = get_user_by_username(username)
    
    if user and user['password'] == password:  # In a real app, use password hashing!
        st.session_state.authenticated = True
        st.session_state.current_user = user
        return True
    
    return False

def is_authenticated():
    """Check if the user is authenticated"""
    return st.session_state.authenticated

def get_current_user():
    """Get the current authenticated user"""
    if is_authenticated():
        return st.session_state.current_user
    return None

def logout():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None

def is_manager():
    """Check if the current user is a manager or team lead"""
    user = get_current_user()
    if user:
        return user['role'] in ['TL', 'Manager']
    return False

def user_has_access(feature_name):
    """Check if the current user has access to a specific feature"""
    user = get_current_user()
    if not user:
        return False
    
    # Define access rules for different features
    access_rules = {
        'award_badges': ['TL', 'Manager'],
        'create_badges': ['TL', 'Manager'],
        'edit_teams': ['TL', 'Manager'],
        'create_sprints': ['TL', 'Manager'],
        'view_reports': ['TL', 'Manager', 'Dev', 'QA', 'RMO'],
        'export_data': ['TL', 'Manager']
    }
    
    if feature_name in access_rules:
        return user['role'] in access_rules[feature_name]
    
    # Default to not having access if feature not defined
    return False
