import streamlit as st
import uuid
from datetime import datetime
import pandas as pd

# TODO: replace these with your real supabase functions
# from utils.database import create_order, upload_payment_proof, get_products

st.set_page_config(page_title="Fedex.COM", page_icon="🛒", layout="wide")

# ---------- SESSION STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "cart_total" not in st.session_state:
    st.session_state.cart_total = 0
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- DUMMY DATA - REPLACE WITH DB ----------
def get_products():
    return [
        {"id": 1, "name": "iPhone 15 Pro", "price": 1200, "image": "https://via.placeholder.com/200"},
        {"id": 2, "name": "Samsung S24 Ultra", "price": 1100, "image": "https://via.placeholder.com/200"},
        {"id": 3, "name": "MacBook Air M3", "price": 1500, "image": "https://via.placeholder.com/200"},
    ]

def create_order(order_data):
    # REPLACE WITH YOUR SUPABASE INSERT
    # supabase.table("orders").insert(order_data).execute()
    print("Order saved:", order_data) # for testing

def upload_payment_proof(file):
    # REPLACE WITH YOUR SUPABASE STORAGE UPLOAD
    # return supabase.storage.from_("proofs").upload(...)
    return "https://fake-url.com/proof.jpg"

# ---------- HELPER FUNCTIONS ----------
def add_to_cart(product):
    st.session_state.cart.append(product)
    st.session_state.cart_total += product["price"]
    st.success(f"{product['name']} added to cart")

def remove_from_cart(index):
    st.session_state.cart_total -= st.session_state.cart[index]["price"]
    st.session_state.cart.pop(index)

# ---------- PAGES ----------
def home_page():
    st.title("🛒 Welcome to CHANGE2.COM")
    st.subheader("The #1 Gadgets Store")
    st.write("Shop the latest phones, laptops and accessories with secure payment.")
    if st.button("Shop Now"):
        st.session_state.page = "Products"
        st.rerun()

def products_page():
    st.title("Products")
    products = get_products()

    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            st.image(product["image"])
            st.subheader(product["name"])
            st.write(f"**${product['price']}**")
            if st.button("Add to Cart", key=product["id"]):
                add_to_cart(product)

    if st.button("View Cart"):
        st.session_state.page = "Cart"
        st.rerun()

def cart_page():
    st.title("Your Cart")
    if len(st.session_state.cart) == 0:
        st.info("Your cart is empty")
    else:
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([3,1,1])
            with col1: st.write(item["name"])
            with col2: st.write(f"${item['price']}")
            with col3:
                if st.button("Remove", key=f"remove{i}"):
                    remove_from_cart(i)
                    st.rerun()

        st.divider()
        st.subheader(f"Total: ${st.session_state.cart_total}")

        if st.button("Proceed to Checkout"):
            st.session_state.page = "Checkout"
            st.rerun()

    if st.button("Continue Shopping"):
        st.session_state.page = "Products"
        st.rerun()

def checkout_page():
    st.title("CHANGE2.COM - Checkout")
    st.write("Complete your order below")

    with st.form("checkout_form"):
        st.subheader("1. Delivery Information")

        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="youremail@example.com")
            country = st.selectbox("Country *", ["Nigeria", "Ghana", "Kenya", "USA", "UK", "Canada", "Other"])
        with col2:
            phone = st.text_input("Phone Number *", placeholder="+234 800 000 0000")
            state = st.text_input("State / Province *", placeholder="Lagos")
            address = st.text_area("Delivery Address *", placeholder="123 Main Street, City")

        st.subheader("2. Payment Details")
        st.warning("Send payment to the wallet address shown at checkout, then upload proof below")
        btc_address = st.text_input("Your BTC Wallet Address for Refunds", placeholder="bc1q...")

        st.subheader("3. Payment Proof")
        payment_proof = st.file_uploader("Upload screenshot of payment", type=["jpg", "png", "jpeg"])

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Confirm Order")
        with col2:
            back = st.form_submit_button("⬅ Back to Cart")

        if back:
            st.session_state.page = "Cart"
            st.rerun()

        if submitted:
            required_fields = [full_name, email, phone, country, state, address]
            if not all(required_fields):
                st.error("Please fill all required fields marked with *")
            else:
                with st.spinner("Placing order..."):
                    try:
                        proof_url = None
                        if payment_proof:
                            proof_url = upload_payment_proof(payment_proof)

                        order_data = {
                            "order_code": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                            "email": email,
                            "customer_email": email,
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
                            "total_amount": st.session_state.cart_total,
                            "created_at": datetime.now().isoformat(),
                            "order_items": st.session_state.cart
                        }

                        create_order(order_data)
                        st.success(f"Order Placed Successfully! 🎉")
                        st.info(f"Your Order Code: **{order_data['order_code']}** Save this to track your order")
                        st.balloons()
                        st.session_state.cart = []
                        st.session_state.cart_total = 0

                    except Exception as e:
                        st.error(f"Order failed: {e}")
                        st.info("Check that all columns exist in Supabase and RLS is disabled")

# ---------- NAVIGATION ----------
st.sidebar.title("CHANGE2.COM")
page = st.sidebar.radio("Menu", ["Home", "Products", "Cart", "Checkout"], index=["Home", "Products", "Cart", "Checkout"].index(st.session_state.page))

st.session_state.page = page

if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Products":
    products_page()
elif st.session_state.page == "Cart":
    cart_page()
elif st.session_state.page == "Checkout":
    checkout_page()

st.sidebar.divider()
st.sidebar.write("© 2026 FedEx.COM")