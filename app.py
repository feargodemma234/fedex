import streamlit as st
import uuid
from datetime import datetime
from utils.database import create_order, upload_payment_proof # your supabase functions

st.title("FedEx.COM - Checkout")

with st.form("checkout_form"):
    st.subheader("1. Delivery Information")
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *", placeholder="FearGod Emma")
        email = st.text_input("Email *", placeholder="rosemongan621@gmail.com")
        country = st.selectbox("Country *", ["Nigeria", "Ghana", "Kenya", "USA", "UK", "Canada"])
    with col2:
        phone = st.text_input("Phone Number *", placeholder="08061715444")
        state = st.text_input("State *", placeholder="Anambra")
        address = st.text_area("Delivery Address *", placeholder="No 1 umueze street nibo")

    st.subheader("2. Payment")
    st.info("Send BTC to: `bc1q...your_wallet_address...` for refunds")
    btc_address = st.text_input("Your BTC Wallet Address for Refunds")
    
    st.subheader("3. Payment Proof")
    payment_proof = st.file_uploader("Upload screenshot of payment", type=["jpg", "png", "jpeg"])
    
    submitted = st.form_submit_button("✅ Confirm Order - I have sent the proof")

    if submitted:
        if not all([full_name, email, phone, country, state, address]):
            st.error("Please fill all required fields *")
        else:
            with st.spinner("Placing order..."):
                try:
                    # 1. Upload image first
                    proof_url = None
                    if payment_proof:
                        proof_url = upload_payment_proof(payment_proof)
                    
                    # 2. Create order dict - matches your Supabase columns
                    order_data = {
                        "order_code": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                        "email": email, # Must match your DB column
                        "customer_email": email, # Keep both if you added both
                        "full_name": full_name,
                        "phone": phone,
                        "country": country,
                        "state": state,
                        "address": address,
                        "btc_address": btc_address,
                        "payment_proof_url": proof_url,
                        "payment_status": "pending",
                        "payment_method": "Bank Transfer",
                        "order_status": "Received",
                        "total_amount": 49.99, # get this from cart
                        "created_at": datetime.now().isoformat(),
                        "order_items": st.session_state.get("cart", []) # your cart
                    }
                    
                    create_order(order_data)
                    st.success(f"Order Placed Successfully! Order Code: {order_data['order_code']}")
                    st.balloons()
                    st.session_state.cart = [] # clear cart

                except Exception as e:
                    st.error(f"Order failed: {e}")