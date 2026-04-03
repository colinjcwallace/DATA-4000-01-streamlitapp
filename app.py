import streamlit as st
import pandas as pd
from supabase import create_client, Client

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
    # We display each item with a Delete button
    for index, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{row['item_name']}** ({row['quantity']}x) - {row['category']}")
        with col2:
            # We use the row['id'] to identify the record to delete
            if st.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("inventory").delete().eq("id", row['id']).execute()
                st.rerun() # Refresh the app to remove the item from view
else:
    st.info("Your inventory is currently empty.")
