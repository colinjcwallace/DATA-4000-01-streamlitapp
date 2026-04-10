import streamlit as st
import pandas as pd
from supabase import create_client, Client


def get_supabase():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url,key)
supabase = get_supabase()
get_supabase()

# Initialize Supabase client
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("Food Inventory Manager")

# --- DATA FUNCTIONS ---
def get_inventory():
    # Fetch data from Supabase
    response = supabase.table("inventory").select("*").execute()
    return response.data

def add_item(name, qty, cat):
    # Insert data into Supabase
    data = {
        "item_name": name,
        "quantity": qty,
        "category": cat,
    }
    supabase.table("inventory").insert(data).execute()
    st.cache_data.clear() # Refresh data

# --- Helper Functions ---
def update_tags(item_id, current_tags, new_tag=None, remove_tag=None):
    updated_tags = list(current_tags) if current_tags else []
    
    if new_tag and new_tag not in updated_tags:
        updated_tags.append(new_tag)
    
    if remove_tag in updated_tags:
        updated_tags.remove(remove_tag)
    
    # Update Supabase
    supabase.table("inventory").update({"tags": updated_tags}).eq("id", item_id).execute()
    st.rerun()


# --- UI SECTION ---
with st.expander("➕ Add New Grocery Item"):
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Item Name")
            qty = st.number_input("Quantity", min_value=1)
        with col2:
            cat = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Pantry", "Frozen"])
        if st.form_submit_button("Save to Inventory"):
            if name:
                add_item(name, qty, cat)
                st.success(f"Added {name}!")
            else:
                st.error("Please enter an item name.")

# --- DISPLAY SECTION ---
st.subheader("Current Stock")
inventory_data = get_inventory()

if inventory_data:
    df = pd.DataFrame(inventory_data)
    # Cleaning up display
    df = df[['item_name', 'quantity', 'category']]
    st.dataframe(df, use_container_width=True)
# 1. Create a display string for the dropdown (Name + Category)
    # This helps if you have "Milk" in both 'Dairy' and 'Pantry'
    df['display_name'] = df['item_name'] + " (" + df['category'] + ")"
    
    # 2. Multiselect for deletion
    to_delete = st.multiselect(
        "Select items to remove from inventory:",
        options=df['display_name'].tolist(),
        help="Select one or more items to delete permanently."
    )
    # 3. Delete Button Logic
    if to_delete:
        if st.button("🗑️ Delete Selected Items", type="primary"):
            # Find the IDs for the selected display names
            ids_to_del = df[df['display_name'].isin(to_delete)]['id'].tolist()
            
            # Execute batch delete in Supabase
            supabase.table("inventory").delete().in_("id", ids_to_del).execute()
            
            st.success(f"Successfully removed {len(to_delete)} items!")
            st.rerun()
else:
    st.info("Your inventory is currently empty.")

