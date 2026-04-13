import streamlit as st
from supabase import create_client

# Setup Connection
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🛒 Inventory Manager")

# --- SECTION 1: ADD / UPDATE ITEMS ---
st.subheader("Add or Use Items")

with st.form("inventory_form", clear_on_submit=True):
    # Fetch existing items for the dropdown
    item_query = supabase.table("item_definitions").select("*").execute()
    item_options = {item['item_name']: item['item_id'] for item in item_query.data}
    
    selected_item_name = st.selectbox("Select Item", options=list(item_options.keys()))
    
    # Use a number input. 
    # Positive = Grocery Shopping, Negative = Cooking/Eating
    amt = st.number_input("Quantity Change (e.g., 12 for buying, -2 for eating)", step=1)
    
    submitted = st.form_submit_button("Log Transaction")
    
    if submitted:
        item_id = item_options[selected_item_name]
        
        # Insert into the Ledger (inventory table)
        data = {
            "item_id": item_id,
            "item_name": selected_item_name,
            "quantity": amt
        }
        
        response = supabase.table("inventory").insert(data).execute()
        
        if response.data:
            st.success(f"Logged {amt} for {selected_item_name}!")
            st.rerun()

# --- SECTION 2: CURRENT STOCK ---
st.divider()
st.subheader("❄️ Current Fridge Contents")

# Pull from the View we created earlier
stock_query = supabase.table("current_stock").select("*").execute()

if stock_query.data:
    # Display as a clean table
    st.table(stock_query.data)
else:
    st.info("The fridge is empty. Time to go shopping!")

# --- SECTION 3: RECENT TRANSACTIONS ---
with st.expander("View Transaction History"):
    history = supabase.table("inventory").select("*").order("created_at", desc=True).limit(10).execute()
    st.dataframe(history.data)