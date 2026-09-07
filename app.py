import streamlit as st
import uuid
from datetime import datetime

st.set_page_config(page_title="FedEx Store", page_icon="📦", layout="wide")

# ---------- SESSION STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "cart_total" not in st.session_state:
    st.session_state.cart_total = 0
if "user" not in st.session_state:
    st.session_state.user = None  # will hold logged in user email
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- SUPABASE FUNCTIONS - REPLACE THESE ----------
# from utils.database import supabase, create_order, upload_payment_proof

def get_products():
    return [
        {"id": 1, "name": "FedEx 10x13 Poly Mailer", "price": 15, "image": "https://via.placeholder.com/200"},
        {"id": 2, "name": "FedEx Shipping Labels", "price": 25, "image": "https://via.placeholder.com/200"},
        {"id": 3, "name": "FedEx Thermal Printer", "price": 280, "image": "https://via.placeholder.com/200"},
        {"id": 4, "name": "FedEx Digital Scale", "price": 95, "image": "https://via.placeholder.com/200"},
    ]

def sign_up(email, password):
    # TODO: supabase.auth.sign_up({"email": email, "password": password})
    st.success("Account created! Please login.")
    return True

def log_in(email, password):
    # TODO: res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    st.session_state.user = email # fake login
    st.success(f"Welcome back {email}")
    return True

def log_out():
    st.session_state.user = None
    st.session_state.cart = []
    st.session_state.cart_total = 0

def create_order(order_data):
    # TODO: supabase.table("orders").insert(order_data).execute()
    print("Order:", order_data)

def upload_payment_proof(file):
    return "https://storage.supabase.co/proof.jpg"

# ---------- AUTH PAGES ----------
def login_signup_page():
    st.title("📦 FedEx Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                log_in(email, password)
                st.rerun()

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email ")
            password = st.text_input("Password ", type="password")
            if st.form_submit_button("Create Account"):
                sign_up(email, password)

# ---------- MAIN APP PAGES ----------
def home_page():
    st.title(f"Welcome {st.session_state.user} 👋")
    st.subheader("Official FedEx Shipping Supplies")
    if st.button("Shop Now"):
        st.session_state.page = "Products"
        st.rerun()

def products_page():
    st.title("Shop Products")
    products = get_products()
    cols = st.columns(4)
    for i, product in enumerate(products):
        with cols[i % 4]:
            st.image(product["image"])
            st.write(f"**{product['name']}**")
            st.write(f"${product['price']}")
            if st.button("Add to Cart", key=product["id"]):
                st.session_state.cart.append(product)
                st.session_state.cart_total += product["price"]
                st.toast("Added to cart")

def cart_page():
    st.title("Your Cart")
    if len(st.session_state.cart) == 0:
        st.info("Cart is empty")
    else:
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([3,1,1])
            with col1: st.write(item["name"])
            with col2: st.write(f"${item['price']}")
            with col3:
                if st.button("Remove", key=f"remove{i}"):
                    st.session_state.cart_total -= item["price"]
                    st.session_state.cart.pop(i)
                    st.rerun()

        st.divider()
        st.metric("Total", f"${st.session_state.cart_total}")
        if st.button("Proceed to Checkout"):
            st.session_state.page = "Checkout"
            st.rerun()

def checkout_page():
    st.title("Checkout")
    
    with st.form("checkout_form"):
        st.subheader("Shipping Information")
        # Auto-fill email from login
        email = st.text_input("Email *", value=st.session_state.user, disabled=True)
        full_name = st.text_input("Full Name *")
        phone = st.text_input("Phone *")
        address = st.text_area("Address *")
        
        col1, col2 = st.columns(2)
        with col1: country = st.text_input("Country *", "USA")
        with col2: state = st.text_input("State *")
        
        st.subheader("Payment Proof")
        payment_proof = st.file_uploader("Upload screenshot", type=["jpg","png","jpeg"])
        btc_address = st.text_input("Transaction ID")

        if st.form_submit_button("✅ Place Order"):
            with st.spinner("Processing..."):
                try:
                    proof_url = upload_payment_proof(payment_proof) if payment_proof else None
                    
                    order = {
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
                        "order_status": "Processing",
                        "total_amount": st.session_state.cart_total,
                        "created_at": datetime.now().isoformat(),
                        "order_items": st.session_state.cart
                    }
                    
                    create_order(order)
                    st.success("Order Placed! 🎉")
                    st.info(f"Order Code: **{order['order_code']}**")
                    st.session_state.cart = []
                    st.session_state.cart_total = 0

                except Exception as e:
                    st.error(f"Error: {e}")

# ---------- ROUTER ----------
if st.session_state.user is None:
    login_signup_page()
else:
    st.sidebar.title("FedEx Store")
    st.sidebar.write(f"Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        log_out()
        st.rerun()
        
    page = st.sidebar.radio("Menu", ["Home", "Products", "Cart", "Checkout"],
                            index=["Home", "Products", "Cart", "Checkout"].index(st.session_state.page))
    st.session_state.page = page

    if st.session_state.page == "Home": home_page()
    elif st.session_state.page == "Products": products_page()
    elif st.session_state.page == "Cart": cart_page()
    elif st.session_state.page == "Checkout": checkout_page()