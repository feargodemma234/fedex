import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
# from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="FedEx Store", page_icon="📦", layout="wide")

# ========== SECRETS ==========
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_EMAILS = st.secrets.get("ADMIN_EMAILS", [])
SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
SMTP_APP_PASSWORD = st.secrets["SMTP_APP_PASSWORD"]
STORE_EMAIL = st.secrets["STORE_EMAIL"]

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== CSS ==========
st.markdown("""
<style>
.stApp { background: #0f172a; color: #f8fafc; }
.store-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 16px; }
.price { color: #22c55e; font-size: 20px; font-weight: 800; }
.success-box { background: #064e3b; padding: 16px; border-radius: 10px; border: 1px solid #059669; }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "checkout_info" not in st.session_state: st.session_state.checkout_info = None
if "cart_total" not in st.session_state: st.session_state.cart_total = 0

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS

def logout():
    # supabase.auth.sign_out()
    for k in list(st.session_state.keys()): del st.session_state[k]

# ========== EMAIL FUNCTION ==========
def send_order_email(order_code, customer_info, cart_items, total):
    msg = EmailMessage()
    msg['Subject'] = f"NEW FEDEX ORDER: {order_code}"
    msg['From'] = SMTP_EMAIL
    msg['To'] = STORE_EMAIL

    items_text = '\n'.join([f"- {i['quantity']} x {i['name']} = ${i['price']*i['quantity']:.2f}" for i in cart_items])

    body = f"""
    NEW ORDER RECEIVED
    Order ID: {order_code}
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    CUSTOMER INFO
    Name: {customer_info['full_name']}
    Email: {customer_info['email']}
    Phone: {customer_info['phone']}
    Address: {customer_info['address']}, {customer_info['state']}, {customer_info['country']}

    PRODUCTS ORDERED
    {items_text}

    TOTAL: ${total:.2f}
    PAYMENT: Pay on Delivery / Bank Transfer will be confirmed by admin
    """
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# ========== DB HELPERS ==========
@st.cache_data(ttl=60)
def load_products():
    return [
        {"id": 1, "name": "FedEx 10x13 Poly Mailer", "description": "Pack of 100", "price": 15.00, "image_url": "https://via.placeholder.com/300"},
        {"id": 2, "name": "FedEx Shipping Labels", "description": "Roll of 500", "price": 25.00, "image_url": "https://via.placeholder.com/300"},
        {"id": 3, "name": "FedEx Thermal Printer", "description": "4x6 Label Printer", "price": 280.00, "image_url": "https://via.placeholder.com/300"},
        {"id": 4, "name": "FedEx Digital Scale", "description": "Up to 50lbs", "price": 95.00, "image_url": "https://via.placeholder.com/300"}
    ]

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["quantity"] += 1
            return
    st.session_state.cart.append({**product, "quantity": 1})

def cart_total():
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart)

# ========== AUTH ==========
def auth_page():
    st.title("📦 FedEx Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")  # ADDED KEY
        password = st.text_input("Password", type="password", key="login_pass") # ADDED KEY
        if st.button("Login", use_container_width=True, key="login_btn"): # ADDED KEY
            # res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = type('obj', (object,), {'email': email}) # fake login
            st.rerun()
    with tab2:
        email = st.text_input("Email ", key="su_email")
        password = st.text_input("Password ", type="password", key="su_pass")
        confirm = st.text_input("Confirm Password", type="password", key="su_confirm") # ADDED KEY
        if st.button("Create Account", use_container_width=True, key="su_btn"): # ADDED KEY
            if password!= confirm: st.error("Passwords don't match")
            else:
                # supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Please Login")

# ========== MAIN APP ==========
if st.session_state.user is None:
    auth_page()
else:
    with st.sidebar:
        st.write(f"Logged in: {st.session_state.user.email}")
        if st.button("Store", use_container_width=True): st.session_state.page = "Store"; st.rerun()
        if st.button(f"Cart ({sum(i['quantity'] for i in st.session_state.cart)})", use_container_width=True): st.session_state.page = "Cart"; st.rerun()
        if st.button("Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()
        if is_admin():
            if st.button("Admin", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True): logout(); st.rerun()

    products = load_products()

    # ========== ROUTER ==========
if st.session_state.user is None:
    auth_page()

else:
    # Sidebar only shows when logged in
    with st.sidebar:
        st.write(f"Logged in: {st.session_state.user.email}")
        if st.button("Store", use_container_width=True): st.session_state.page = "Store"; st.rerun()
        if st.button(f"Cart ({sum(i['quantity'] for i in st.session_state.cart)})", use_container_width=True): st.session_state.page = "Cart"; st.rerun()
        if st.button("Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()
        if is_admin():
            if st.button("Admin", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True): logout(); st.rerun()

    products = load_products()

    # ========== STORE PAGE ==========
    if st.session_state.page == "Store":
        st.title("📦 FedEx Shipping Supplies")
        cols = st.columns(3)
        for i, p in enumerate(products):
            with cols[i%3]:
                st.markdown('<div class="store-card">', unsafe_allow_html=True)
                st.image(p["image_url"])
                st.write(f"**{p['name']}**")
                st.write(f"{p['description']}")
                st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
                if st.button("Add to Cart", key=p["id"]):
                    add_to_cart(p); st.success("Added!"); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ========== CART PAGE ==========
    elif st.session_state.page == "Cart":
        st.title("Your Cart")
        if not st.session_state.cart: st.info("Cart is empty")
        else:
            for item in st.session_state.cart:
                c1,c2,c3,c4 = st.columns([3,2,1,1])
                c1.write(item["name"])
                c2.write(f"${item['price']}")
                c3.write(f"Qty: {item['quantity']}")
                c4.write(f"**${item['price']*item['quantity']:.2f}**")
            st.divider()
            st.metric("Total", f"${cart_total():.2f}")
            if st.button("Proceed to Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()

    # ========== CHECKOUT PAGE ==========
    elif st.session_state.page == "Checkout":
        st.title("Checkout")
        with st.form("checkout_form"):
            st.subheader("Shipping Information")
            full_name = st.text_input("Full Name *", value=st.session_state.user.email)
            email = st.text_input("Email *", value=st.session_state.user.email, disabled=True)
            phone = st.text_input("Phone *")
            address = st.text_area("Address *")
            country = st.text_input("Country *", "USA")
            state = st.text_input("State *")
            st.subheader("Payment Method")
            st.info("We will contact you for payment. Options: Pay on Delivery or Bank Transfer")

            if st.form_submit_button("✅ Place Order", use_container_width=True):
                if not all([full_name, phone, address, country, state]):
                    st.error("Please fill all * fields")
                else:
                    order_code = f"FEDEX-{uuid.uuid4().hex[:8].upper()}"
                    customer_info = {"full_name": full_name, "email": email, "phone": phone, "address": address, "country": country, "state": state}
                    # TODO: supabase.table("orders").insert({...}).execute()
                    send_order_email(order_code, customer_info, st.session_state.cart, cart_total())
                    st.markdown(f'<div class="success-box"><h2>Order Placed! 🎉</h2>Order ID: <strong>{order_code}</strong><br>We will email you shortly.</div>', unsafe_allow_html=True)
                    st.session_state.cart = []

    # ========== ADMIN PAGE ==========
    elif st.session_state.page == "Admin" and is_admin():
        st.title("Admin Dashboard 📊")
        st.write("View and manage orders here")
        orders = supabase.table("orders").select("*").order("created_at", desc=True).execute().data
        if not orders: st.info("No orders yet")
        else:
            for o in orders:
                with st.expander(f"Order: {o['order_code']} - {o['full_name']} - ${o['total']:.2f}"):
                    st.write(f"**Email:** {o['customer_email']}")
                    st.write(f"**Status:** {o['order_status']}")
                    new_status = st.selectbox("Update Status", ["pending", "processing", "shipped", "delivered", "cancelled"], key=o['id'])
                    if st.button("Update", key=f"btn_{o['id']}"):
                        supabase.table("orders").update({"order_status": new_status}).eq("id", o['id']).execute()
                        st.success("Status Updated!")
                        st.rerun()