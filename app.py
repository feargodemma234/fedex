import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
# from supabase import create_client, Client
from datetime import datetime
from urllib.parse import quote

st.set_page_config(page_title="Quantum Store", page_icon="🛒", layout="wide")

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
.price { color: #38bdf8; font-size: 20px; font-weight: 800; }
.success-box { background: #064e3b; padding: 16px; border-radius: 10px; border: 1px solid #059669; }
.info-box { background: #1e3a8a; padding: 16px; border-radius: 10px; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "checkout_info" not in st.session_state: st.session_state.checkout_info = None
if "cart_total" not in st.session_state: st.session_state.cart_total = 0
if "user_email" not in st.session_state: st.session_state.user_email = ""

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS

def logout():
    supabase.auth.sign_out()
    for k in list(st.session_state.keys()): del st.session_state[k]

# ========== EMAIL FUNCTION ==========
def send_order_email(order_code, customer_info, cart_items, total, payment_method, proof_note):
    msg = EmailMessage()
    msg['Subject'] = f"NEW ORDER: {order_code}"
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
    PAYMENT METHOD: {payment_method}
    PROOF STATUS: {proof_note}
    """
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except: return False

# ========== DB HELPERS ==========
@st.cache_data(ttl=60)
def load_products():
    try:
        res = supabase.table("products").select("*").execute()
        if res.data: return res.data
    except: pass
    return [
        {"id": str(uuid.uuid4()), "name": "Noise cancelling bluetooth", "description": "Noise cancelling bluetooth", "price": 49.99, "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
        {"id": str(uuid.uuid4()), "name": "Bluetooth Speaker", "description": "Portable waterproof", "price": 34.99, "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"}
    ]

def get_admin_settings():
    try:
        res = supabase.table("admin_settings").select("*").eq("id", 1).execute()
        if res.data and len(res.data) > 0: return res.data[0]
    except: pass
    default = {
        "account_name": "Deborah Oluchukwu Phillips",
        "account_number": "09832113433",
        "bank_instructions": "Buy card and upload photo"
    }
    try: supabase.table("admin_settings").insert(default).execute()
    except: pass
    return default

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
    st.title("🛒 Quantum Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error("Invalid email or password")
    with tab2:
        email = st.text_input("Email ", key="su_email")
        password = st.text_input("Password ", type="password", key="su_pass")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if password!= confirm: st.error("Passwords don't match")
            else:
                try:
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created! Check email to confirm then Login")
                except Exception as e: st.error(str(e))

# ========== SIDEBAR ==========
if st.session_state.user:
    with st.sidebar:
        st.write(f"Welcome {st.session_state.user.email}")
        if st.button("Store", use_container_width=True): st.session_state.page = "Store"; st.rerun()
        if st.button(f"Cart ({sum(i['quantity'] for i in st.session_state.cart)})", use_container_width=True): st.session_state.page = "Cart"; st.rerun()
        if st.button("Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()
        if is_admin():
            st.button("Admin", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True): logout(); st.rerun()

products = load_products()
settings = get_admin_settings()

# ========== STORE PAGE ==========
if st.session_state.page == "Store":
    st.title("🛒 Quantum Store")
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i%3]:
            with st.markdown('<div class="store-card">', unsafe_allow_html=True):
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
        st.markdown(f"### Total: ${cart_total():.2f}")
        if st.button("Proceed to Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()

# ========== CHECKOUT INFO PAGE ==========
elif st.session_state.page == "Checkout":
    st.subheader("Customer Information")
    with st.form("customer_form"):
        full_name = st.text_input("Full Name", value=st.session_state.user_email)
        email = st.text_input("Email", value=st.session_state.user.email)
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        country = st.text_input("Country")
        state = st.text_input("State")
        if st.form_submit_button("Save & Continue to Payment", use_container_width=True):
            if not all([full_name, phone, address, country, state]):
                st.error("Please fill all fields")
            else:
                st.session_state.checkout_info = {"full_name": full_name, "phone": phone, "address": address, "country": country, "state": state, "email": email}
                st.session_state.page = "Payment"; st.rerun()

# ========== PAYMENT PAGE ==========
elif st.session_state.page == "Payment":
    if not st.session_state.checkout_info:
        st.error("Please fill customer info first")
        if st.button("Back"): st.session_state.page = "Checkout"; st.rerun()
    else:
        st.subheader("Order Summary")
        for i in st.session_state.cart:
            st.write(f"{i['name']} x {i['quantity']} = ${i['price']*i['quantity']:.2f}")
        st.markdown(f"### Total: ${cart_total():.2f}")
        st.divider()
        st.subheader("Choose Payment Method")
        payment_method = st.radio("Payment Method", ["Bank Transfer", "Gift Card"], horizontal=True)
        
        if payment_method == "Bank Transfer":
            st.markdown(f'<div class="store-card"><h3>Bank Transfer Details</h3><b>Account Name:</b> {settings["account_name"]}<br><b>Account Number:</b> {settings["account_number"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="store-card"><h3>Gift Card</h3>{settings["bank_instructions"]}</div>', unsafe_allow_html=True)
        
        order_code = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        items_list = "\n".join([f"{i['quantity']} x {i['name']}" for i in st.session_state.cart])
        
        subject = quote(f"Payment Proof for {order_code}")
        body = quote(f"""Hello Quantum Store,
I am sending payment proof for my order.
Order Number: {order_code}
Name: {st.session_state.checkout_info['full_name']}
Email: {st.session_state.checkout_info['email']}
Phone: {st.session_state.checkout_info['phone']}
Payment Method: {payment_method}
PRODUCTS:
{items_list}
Order Total: ${cart_total():.2f}
I have attached my payment proof/screenshot.
Thank you.""")
        
        mailto_link = f"mailto:{STORE_EMAIL}?subject={subject}&body={body}"
        st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:block;text-align:center;background:#38bdf8;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">Send Payment Proof via Gmail</a>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Add image proof of payment to the email before sending. OR click below</div>', unsafe_allow_html=True)
        if st.button("I have sent the proof", use_container_width=True): st.button("Confirm Order")
        
        # NO ERROR DISPLAY HERE
        order_data = {
            "order_code": order_code,
            "user_id": st.session_state.user.id,
            "full_name": st.session_state.checkout_info["full_name"],
            "phone": st.session_state.checkout_info["phone"],
            "address": st.session_state.checkout_info["address"],
            "country": st.session_state.checkout_info["country"],
            "state": st.session_state.checkout_info["state"],
            "customer_email": st.session_state.checkout_info["email"],
            "payment_method": payment_method,
            "order_status": "pending",
            "payment_proof_url": None,
            "total": cart_total()
        }
        table = supabase.table("orders").insert(order_data).execute()
        order_id = table.data[0]["id"]
        
        items = [{
            "order_id": order_id,
            "product_id": i["id"],
            "product_name": i["name"],
            "quantity": i["quantity"],
            "unit_price": i["price"]
        } for i in st.session_state.cart]
        supabase.table("order_items").insert(items).execute()
        
        send_order_email(order_code, st.session_state.checkout_info, st.session_state.cart, cart_total(), payment_method, "Customer will send via Gmail")
        
        st.session_state.cart = []
        st.session_state.checkout_info = None
        st.session_state.page = "Confirmation"
        st.session_state.last_order = order_code
        st.rerun()

# ========== CONFIRMATION ==========
elif st.session_state.page == "Confirmation":
    st.markdown(f'<div class="success-box"><h2>Order Received!</h2>Order ID: <strong>{st.session_state.last_order}</strong></div>', unsafe_allow_html=True)
    if st.button("Continue Shopping"): st.session_state.page = "Store"; st.rerun()

# ========== ADMIN ==========
elif st.session_state.page == "Admin" and is_admin():
    st.title("Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Orders", "Products", "Settings"])
    with tab1:
        orders = supabase.table("orders").select("*").order("created_at", desc=True).execute().data
        for o in orders:
            st.write(f"**#{o['order_code']}** - {o['full_name']} - ${o['total']:.2f}")
            new_status = st.selectbox("Status", ["Received", "Payment Under Review", "Processing", "Completed", "Cancelled"], key=o['id'])
            if st.button("Update", key=f"up_{o['id']}"):
                supabase.table("orders").update({"order_status": new_status}).eq("id", o['id']).execute(); st.rerun()