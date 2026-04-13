import streamlit as st
from supabase import create_client

# 1. Setup Connection
url: str = st.secrets ["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🍳 Fridge-to-Table Manager")
st.write("Welcome! Select a recipe below to see if you have the ingredients in stock.")

# 2. Select Recipe
# In a real app, you'd fetch this list from your 'recipes' table
recipe_query = supabase.table("recipe").select("*").execute()
recipe_options = {r['recipe_name']: r['recipe_id'] for r in recipe_query.data}

selection = st.selectbox("I want to make:", options=list(recipe_options.keys()))

if selection:
    recipe_id = recipe_options[selection]
    
    # 3. Fetch Data (Instructions)
    steps = supabase.table("recipe_instructions").select("*").eq("recipe_id", recipe_id).order("step_number").execute()
    
    # 4. Fetch Comparison Logic (Ingredients vs Stock)
    # We use a RPC (Stored Function) or a specific query here
    # For simplicity, let's fetch the ingredients and the current stock
    ingredients = supabase.table("recipe_ingredients").select("*, item_definitions(item_name)").eq("recipe_id", recipe_id).execute()
    stock = supabase.table("current_stock").select("*").execute()
    stock_dict = {item['item_id']: item['total_in_fridge'] for item in stock.data}

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Instructions")
        for step in steps.data:
            st.write(f"{step['step_number']}. {step['step_description']}")

    with col2:
        st.subheader("🛒 Ingredient Check")
        
        have = []
        need = []

        for ing in ingredients.data:
            item_id = ing['item_id']
            name = ing['item_definitions']['item_name']
            required = ing['quantity_required']
            current = stock_dict.get(item_id, 0)

            if current >= required:
                have.append(name)
            else:
                need.append(name)

        st.write("**Already in Fridge:**")
        if have:
            for item in have: st.success(item)
        else: st.info("Nothing in stock!")

        st.write("**Need to Buy:**")
        if need:
            for item in need: st.error(item)
        else: st.balloons() # Success! You have everything.