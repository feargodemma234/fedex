import streamlit as st
import uuid
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="FedEx Store", page_icon="📦", layout="wide")

# ---------- SESSION STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "cart_total" not in st.session_state:
    st.session_state.cart_total = 0
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- SUPABASE FUNCTIONS ----------
# Replace with your real supabase imports
# from utils.database import create_order, upload_payment_proof, get_products

def get_products():
    return [
        {"id": 1, "name": "FedEx Laptop Bag", "price": 45, "image": "https://via.placeholder.com/200"},
        {"id": 2, "name": "FedEx Shipping Scale", "price": 120, "image": "https://via.placeholder.com/200"},
        {"id": 3, "name": "FedEx Thermal Printer", "price": 250, "image": "https://via.placeholder.com/200"},
    ]

def create_order(order_data):
    # REPLACE WITH: supabase.table("orders").insert(order_data).execute()
    st.write("DEBUG: Order Data", order_data) # remove after testing

def upload_payment_proof(file):
    # REPLACE WITH: supabase storage upload
    return "https://storage.supabase.co/proof.jpg"

# ---------- HELPER ----------
def add_to_cart(product):
    st.session_state.cart.append(product)
    st.session_state.cart_total += product["price"]
    st.toast(f"{product['name']} added to cart")

def remove_from_cart(index):
    st.session_state.cart_total -= st.session_state.cart[index]["price"]
    st.session_state.cart.pop(index)

# ---------- PAGES ----------
def home_page():
    st.title("📦 Welcome to FedEx Store")
    st.subheader("Official Shipping Supplies & Equipment")
    st.write("Get everything you need for fast and reliable shipping.")
    if st.button("Shop Supplies"):
        st.session_state.page = "Products"
        st.rerun()

def products_page():
    st.title("FedEx Products")
    products = get_products()

    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            st.image(product["image"])
            st.subheader(product["name"])
            st.write(f"**${product['price']}**")
            if st.button("Add to Cart", key=product["id"]):
                add_to_cart(product)

    st.divider()
    if st.button("View Cart 🛒"):
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
    st.title("FedEx Store - Checkout")
    st.write("Enter your shipping and payment details")

    with st.form("checkout_form"):
        st.subheader("1. Shipping Information")

        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            country = st.selectbox("Country *", ["USA", "Canada", "UK", "Nigeria", "Other"])
        with col2:
            phone = st.text_input("Phone Number *")
            state = st.text_input("State *")
            address = st.text_area("Shipping Address *")

        st.subheader("2. Payment Method")
        payment_method = st.radio("Choose Payment", ["Credit Card", "Bank Transfer", "PayPal"])
        btc_address = ""
        if payment_method == "Bank Transfer":
            st.info("Send payment to FedEx Bank Account. Upload proof below.")
            btc_address = st.text_input("Reference / Transaction ID")

        st.subheader("3. Payment Proof")
        payment_proof = st.file_uploader("Upload payment screenshot", type=["jpg", "png", "jpeg"])

        submitted = st.form_submit_button("✅ Place Order")

        if submitted:
            if not all([full_name, email, phone, country, state, address]):
                st.error("Please fill all required fields *")
            else:
                with st.spinner("Processing order..."):
                    try:
                        proof_url = None
                        if payment_proof:
                            proof_url = upload_payment_proof(payment_proof)

                        order_data = {
                            "order_code": f"FEDEX-{uuid.uuid4().hex[:8].upper()}",
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
                            "payment_method": payment_method,
                            "order_status": "Processing",
                            "total_amount": st.session_state.cart_total,
                            "created_at": datetime.now().isoformat(),
                            "order_items": st.session_state.cart
                        }

                        create_order(order_data)
                        st.success("Order Placed Successfully! 🎉")
                        st.info(f"Your Order Code: **{order_data['order_code']}**")
                        st.balloons()
                        st.session_state.cart = []
                        st.session_state.cart_total = 0

                    except Exception as e:
                        st.error(f"Order failed: {e}")

# ---------- ROUTER ----------
st.sidebar.title("FedEx Store")
page = st.sidebar.radio("Menu", ["Home", "Products", "Cart", "Checkout"],
                        index=["Home", "Products", "Cart", "Checkout"].index(st.session_state.page))

st.session_state.page = page

if st.session_state.page == "Home": home_page()
elif st.session_state.page == "Products": products_page()
elif st.session_state.page == "Cart": cart_page()
elif st.session_state.page == "Checkout": checkout_page()

st.sidebar.divider()
st.sidebar.write("© 2026 FedEx Store")