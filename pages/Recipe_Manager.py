import streamlit as st
from supabase import create_client

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("📖 Recipe Manager")

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

# --- STEP 2: MANAGE RECIPE DETAILS ---
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
            st.write(f"Add ingredients to **{selected_r_name}**")
            ing_input = st.text_input("Ingredient Name (e.g., Flour, Milk)")
            
            # Layout for Quantity and Unit
            col_q, col_u = st.columns([1, 2])
            with col_q:
                ing_qty = st.number_input("Qty", min_value=1, step=1)
            with col_u:
                # New Input for Units
                ing_unit = st.text_input("Unit (e.g., cups, grams, large, tbsp)", value="unit")
            
            ing_cat = st.selectbox("Category (If new)", ["Pantry", "Dairy", "Produce", "Meat", "Frozen", "Other"])
            
            if st.form_submit_button("Add Ingredient"):
                if ing_input:
                    clean_name = ing_input.strip().title()
                    existing_item = next((i for i in item_defs if i['item_name'] == clean_name), None)
                    
                    # 1. Register item if it doesn't exist
                    if not existing_item:
                        new_def = supabase.table("item_definitions").insert({
                            "item_name": clean_name, 
                            "category": ing_cat
                        }).execute()
                        item_id = new_def.data[0]['item_id']
                    else:
                        item_id = existing_item['item_id']

                    # 2. Upsert into recipe_ingredients WITH the unit
                    supabase.table("recipe_ingredients").upsert({
                        "recipe_id": recipe_id,
                        "item_id": item_id,
                        "quantity_required": ing_qty,
                        "unit": ing_unit.strip().lower() # Standardize units to lowercase
                    }).execute()
                    st.success(f"Added {ing_qty} {ing_unit} of {clean_name}")
                    st.rerun()

    with tab2:
        # Background auto-step logic
        existing_steps = supabase.table("recipe_instructions").select("step_number").eq("recipe_id", recipe_id).execute()
        next_step = max([s['step_number'] for s in existing_steps.data]) + 1 if existing_steps.data else 1

        with st.form("add_step_form", clear_on_submit=True):
            step_desc = st.text_area("Type the next instruction:")
            if st.form_submit_button("Add Instruction"):
                if step_desc:
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
            # Updated to show the unit next to the quantity
            st.write(f"• {i['item_definitions']['item_name']}: {i['quantity_required']} {i['unit']}")
            
    with col_b:
        st.write("**Instructions**")
        inst = supabase.table("recipe_instructions").select("*").eq("recipe_id", recipe_id).order("step_number").execute()
        for s in inst.data:
            st.write(f"{s['step_number']}. {s['step_description']}")