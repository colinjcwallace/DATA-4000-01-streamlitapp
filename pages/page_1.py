import streamlit as st
from supabase import create_client

# Setup Connection
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🛒 Inventory Manager")

# --- SECTION 1: LOG TRANSACTION ---
st.subheader("📥 Add or Use Items")

# 1. Fetch current definitions for the selection list
item_query = supabase.table("item_definitions").select("*").order("item_name").execute()
item_defs = item_query.data
item_names = [item['item_name'] for item in item_defs]

with st.form("log_transaction_form", clear_on_submit=True):
    # 'options' contains existing items. User can also type a new one.
    selected_name = st.selectbox(
        "Item Name", 
        options=["-- New Item --"] + item_names,
        help="Select an existing item or choose 'New Item' to register a fresh one below."
    )
    
    # If they chose New Item, they need to type it out
    new_item_input = st.text_input("If New Item, type name here:")
    
    cat_choice = st.selectbox("Category", ["Dairy", "Produce", "Meat", "Pantry", "Frozen", "Other"])
    amt = st.number_input("Quantity Change (e.g., 5, -2)", step=1)
    
    submitted = st.form_submit_button("Update Inventory")

    if submitted:
        # Determine the final name and clean it (the "mIlk" fix)
        raw_name = new_item_input if selected_name == "-- New Item --" else selected_name
        
        if not raw_name or raw_name == "-- New Item --":
            st.error("Please provide a valid item name.")
        elif amt == 0:
            st.error("Quantity cannot be zero.")
        else:
            clean_name = raw_name.strip().title()
            
            # A. Check if item exists in definitions
            existing_item = next((i for i in item_defs if i['item_name'] == clean_name), None)
            
            if not existing_item:
                # Register new item definition first
                new_def = supabase.table("item_definitions").insert({
                    "item_name": clean_name, 
                    "category": cat_choice
                }).execute()
                item_id = new_def.data[0]['item_id']
                st.info(f"✨ Registered '{clean_name}' as a new item.")
            else:
                item_id = existing_item['item_id']

            # B. Insert the transaction into the Ledger (inventory table)
            payload = {
                "item_id": item_id,
                "item_name": clean_name,
                "quantity": amt,
                "category": cat_choice
            }
            
            supabase.table("inventory").insert(payload).execute()
            st.success(f"Successfully logged {amt} units for {clean_name}!")
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