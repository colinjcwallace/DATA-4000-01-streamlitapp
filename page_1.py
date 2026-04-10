import streamlit as st
import pandas as pd
from supabase import create_client, Client

def get_recipe():
    ingredients = st.text_input()