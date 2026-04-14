import streamlit as st
from supabase import create_client

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("📖 Recipe Book")

# --- STEP 1: CREATE NEW RECIPE ---
st.subheader("➕ Create New Recipe")
with st.form("new_recipe_form", clear_on_submit=True):
    new_recipe_name = st.text_input("Recipe Name")
    if st.form_submit_button("Save Recipe Name"):
        if new_recipe_name:
            res = supabase.table("recipe").insert({"recipe_name": new_recipe_name.strip().title()}).execute()
            st.success(f"Added {new_recipe_name}!")
            st.rerun()

st.divider()

# --- STEP 2: MANIPULATE RECIPE ---
recipe_query = supabase.table("recipe").select("*").execute()
if recipe_query.data:
    recipe_list = {r['recipe_name']: r['recipe_id'] for r in recipe_query.data}
    selected_r_name = st.selectbox("Select a Recipe to Edit", options=list(recipe_list.keys()))
    recipe_id = recipe_list[selected_r_name]

    tab1, tab2 = st.tabs(["🥕 Add Ingredients", "📝 Add Instructions"])

    with tab1:
        item_query = supabase.table("item_definitions").select("*").execute()
        item_defs = item_query.data
        
        with st.form("add_ing_form", clear_on_submit=True):
            ing_input = st.text_input("Ingredient Name")
            ing_cat = st.selectbox("Category (If new)", ["Pantry", "Dairy", "Produce", "Meat", "Frozen", "Other"])
            ing_qty = st.number_input("Quantity Required", min_value=1, step=1)
            
            if st.form_submit_button("Add to Recipe"):
                if ing_input:
                    clean_name = ing_input.strip().title()
                    existing_item = next((i for i in item_defs if i['item_name'] == clean_name), None)
                    
                    if not existing_item:
                        new_def = supabase.table("item_definitions").insert({
                            "item_name": clean_name, 
                            "category": ing_cat
                        }).execute()
                        item_id = new_def.data[0]['item_id']
                    else:
                        item_id = existing_item['item_id']

                    supabase.table("recipe_ingredients").upsert({
                        "recipe_id": recipe_id,
                        "item_id": item_id,
                        "quantity_required": ing_qty
                    }).execute()
                    st.rerun()

    with tab2:
        # --- BACKGROUND AUTO-STEP LOGIC ---
        # User sees nothing, but we calculate the number here
        existing_steps = supabase.table("recipe_instructions").select("step_number").eq("recipe_id", recipe_id).execute()
        next_step = max([s['step_number'] for s in existing_steps.data]) + 1 if existing_steps.data else 1

        with st.form("add_step_form", clear_on_submit=True):
            # Only the description input is visible
            step_desc = st.text_area("Type the next instruction here:")
            
            if st.form_submit_button("Add Instruction"):
                if step_desc:
                    # Database gets the 'next_step' calculated above
                    supabase.table("recipe_instructions").insert({
                        "recipe_id": recipe_id,
                        "step_number": next_step,
                        "step_description": step_desc
                    }).execute()
                    st.rerun()

    # --- FINAL PREVIEW ---
    st.divider()
    st.subheader(f"Recipe Preview: {selected_r_name}")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Ingredients**")
        ings = supabase.table("recipe_ingredients").select("*, item_definitions(item_name)").eq("recipe_id", recipe_id).execute()
        for i in ings.data:
            st.write(f"• {i['item_definitions']['item_name']} ({i['quantity_required']})")
            
    with col_b:
        st.write("**Instructions**")
        inst = supabase.table("recipe_instructions").select("*").eq("recipe_id", recipe_id).order("step_number").execute()
        for s in inst.data:
            st.write(f"{s['step_number']}. {s['step_description']}")