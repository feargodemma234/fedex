import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="Quantum Store", page_icon="🛍️", layout="wide")

# ========== SECRETS ==========
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_EMAILS = st.secrets.get("ADMIN_EMAILS", [])
SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
SMTP_APP_PASSWORD = st.secrets["SMTP_APP_PASSWORD"]
STORE_EMAIL = st.secrets["STORE_EMAIL"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== CSS ==========
st.markdown("""
<style>
.stApp {background: #0f172a; color: #f8fafc;}
.store-card {background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 16px;}
.price {color: #38bdf8; font-size: 20px; font-weight: 800;}
.success-box {background: #064e3b; padding: 20px; border-radius: 12px; border: 1px solid #059669;}
</style>
""", unsafe_allow_html=True)

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS

def logout():
    supabase.auth.sign_out()
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# ========== EMAIL FUNCTION ==========
def send_order_email(order_code, customer_info, cart_items, total, payment_method, proof_url):
    msg = EmailMessage()
    msg["Subject"] = f"NEW ORDER: {order_code}"
    msg["From"] = SMTP_EMAIL
    msg["To"] = STORE_EMAIL
    
    items_text = "\n".join([f"- {i['name']} x {i['quantity']} = ${i['price']*i['quantity']:.2f}" for i in cart_items])
    
    body = f"""
NEW ORDER RECEIVED

Order ID: {order_code}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CUSTOMER INFO
Name: {customer_info['full_name']}
Email: {customer_info['email']}
Phone: {customer_info['phone']}
Address: {customer_info['address']}, {customer_info['state']}, {customer_info['country']}

ORDER ITEMS
{items_text}

TOTAL: ${total:.2f}
PAYMENT METHOD: {payment_method}
PAYMENT PROOF: {proof_url}

Login to admin dashboard to update status.
"""
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email failed to send: {e}")
        return False

# ========== DB HELPERS ==========
@st.cache_data(ttl=60)
def load_products():
    try:
        res = supabase.table("products").select("*").execute()
        if res.data: return res.data
    except: pass
    return [ # SAMPLE PRODUCTS
        {"id": str(uuid.uuid4()), "name": "Wireless Headphones", "description": "Noise cancelling bluetooth", "price": 49.99, "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
        {"id": str(uuid.uuid4()), "name": "Smart Watch Pro", "description": "Fitness + notifications", "price": 79.99, "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"},
        {"id": str(uuid.uuid4()), "name": "Bluetooth Speaker", "description": "Portable waterproof", "price": 34.99, "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"},
    ]

@st.cache_data(ttl=30)
def get_admin_settings(): # <-- FIXED FUNCTION
    try:
        res = supabase.table("admin_settings").select("*").eq("id", 1).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        st.warning(f"admin_settings not found, creating defaults")
    
    # Create default if missing
    default = {
        "id": 1,
        "bank_name": "Opay",
        "account_name": "Deborah Oluchukwu Phillips", 
        "account_number": "9032113433",
        "bank_instructions": "Transfer and upload proof",
        "giftcard_instructions": "Buy card and upload photo"
    }
    try:
        supabase.table("admin_settings").insert(default).execute()
    except:
        pass
    return default

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]: item["quantity"] += 1; return
    st.session_state.cart.append({**product, "quantity": 1})

def cart_total(): return sum(item["price"] * item["quantity"] for item in st.session_state.cart)

# ========== AUTH ==========
if not st.session_state.user:
    st.title("🛍️ Quantum Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user; st.rerun()
            except Exception as e:
                if "Email not confirmed" in str(e): st.error("Please confirm your email first")
                else: st.error("Invalid email or password")
    with tab2:
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if password!= confirm: st.error("Passwords don't match")
            else:
                try:
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created! Check your email to confirm, then login.")
                except Exception as e: st.error(str(e))
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.write(f"👤 {st.session_state.user.email}")
    if st.button("🛒 Store", use_container_width=True): st.session_state.page = "Store"; st.rerun()
    if st.button(f"🛍️ Cart ({sum(i['quantity'] for i in st.session_state.cart)})", use_container_width=True): st.session_state.page = "Cart"; st.rerun()
    if st.button("💳 Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()
    if is_admin():
        st.divider()
        if st.button("⚙️ Admin", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
    if st.button("🚪 Logout", use_container_width=True): logout()

products = load_products()
settings = get_admin_settings() # <-- THIS LINE NO LONGER CRASHES

# ========== STORE ==========
if st.session_state.page == "Store":
    st.title("🛍️ Quantum Store")
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i%3]:
            st.markdown('<div class="store-card">', unsafe_allow_html=True)
            st.image(p["image_url"], use_container_width=True)
            st.write(f"**{p['name']}**")
            st.write(p["description"])
            st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
            if st.button("Add to Cart", key=p["id"]): add_to_cart(p); st.success("Added!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ========== CART ==========
elif st.session_state.page == "Cart":
    st.title("🛒 Your Cart")
    if not st.session_state.cart: st.info("Cart is empty")
    else:
        for item in st.session_state.cart:
            c1, c2, c3, c4 = st.columns([3,2,2,1])
            c1.write(item['name'])
            c2.write(f"${item['price']}")
            c3.write(f"Qty: {item['quantity']}")
            c4.write(f"**${item['price']*item['quantity']:.2f}**")
        st.divider()
        st.markdown(f"### Total: ${cart_total():.2f}")
        if st.button("Proceed to Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()

# ========== CHECKOUT ==========
elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")
    with st.form("checkout"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        country = st.text_input("Country")
        state = st.text_input("State")
        
        st.subheader("Payment Method")
        payment_method = st.radio("Choose", ["Bank Transfer", "Gift Card"])
        
        if payment_method == "Bank Transfer":
            st.info(f"**Bank:** {settings['bank_name']}\n**Account:** {settings['account_number']}\n**Name:** {settings['account_name']}")
        
        payment_proof = st.file_uploader("Upload Payment Proof JPG/PNG", type=["jpg","jpeg","png","webp"])
        
        if st.form_submit_button("✅ Confirm Order", use_container_width=True):
            if not all([full_name, phone, address, country, state]): st.error("Fill all fields"); st.stop()
            if not payment_proof: st.error("Upload payment proof"); st.stop()
            
            # 1. Upload proof
            file_bytes = payment_proof.read()
            file_path = f"{st.session_state.user.id}/{uuid.uuid4()}_{payment_proof.name}"
            supabase.storage.from_("payment-proofs").upload(file_path, file_bytes)
            proof_url = supabase.storage.from_("payment-proofs").get_public_url(file_path)
            
            # 2. Create order
            order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            order_data = {
                "order_code": order_code, "user_id": st.session_state.user.id,
                "full_name": full_name, "phone": phone, "address": address,
                "country": country, "state": state, "customer_email": st.session_state.user.email,
                "payment_method": payment_method, "payment_proof_url": proof_url,
                "total": cart_total(), "status": "Received"
            }
            order_res = supabase.table("orders").insert(order_data).execute()
            order_id = order_res.data[0]["id"]
            
            # 3. Order items
            items = [{
                "order_id": order_id, "product_id": i["id"], "product_name": i["name"],
                "quantity": i["quantity"], "unit_price": i["price"]
            } for i in st.session_state.cart]
            supabase.table("order_items").insert(items).execute()
            
            # 4. SEND DIRECT EMAIL
            customer_info = {"full_name": full_name, "email": st.session_state.user.email, "phone": phone, "address": address, "state": state, "country": country}
            email_sent = send_order_email(order_code, customer_info, st.session_state.cart, cart_total(), payment_method, proof_url)
            
            st.session_state.cart = []
            st.session_state.page = "Confirmation"
            st.session_state.last_order = order_code
            if email_sent: st.success("Order + Email sent to owner!")
            st.rerun()

# ========== CONFIRMATION ==========
elif st.session_state.page == "Confirmation":
    st.markdown(f'<div class="success-box"><h2>✅ Order Received!</h2><p>Order ID: <strong>{st.session_state.last_order}</strong></p><p>We will verify your payment and update you.</p></div>', unsafe_allow_html=True)
    if st.button("Continue Shopping"): st.session_state.page = "Store"; st.rerun()

# ========== ADMIN ==========
elif st.session_state.page == "Admin" and is_admin():
    st.title("⚙️ Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Orders", "Products", "Settings"])
    
    with tab1:
        orders = supabase.table("orders").select("*").order("created_at", desc=True).execute().data
        for o in orders:
            st.write(f"**{o['order_code']}** - {o['full_name']} - ${o['total']} - {o['status']}")
            if o['payment_proof_url']: st.image(o['payment_proof_url'], width=200)
            new_status = st.selectbox("Status", ["Received","Payment Under Review","Payment Confirmed","Processing","Completed","Cancelled"], key=o["id"])
            if st.button("Update", key=f"up_{o['id']}"):
                supabase.table("orders").update({"status": new_status}).eq("id", o["id"]).execute(); st.rerun()
    
    with tab2:
        st.subheader("Add Product")
        with st.form("add_product"):
            name = st.text_input("Name"); desc = st.text_area("Description")
            price = st.number_input("Price", min_value=0.0); img = st.text_input("Image URL")
            if st.form_submit_button("Add"): supabase.table("products").insert({"name":name,"description":desc,"price":price,"image_url":img}).execute(); st.rerun()
    
    with tab3:
        st.subheader("Bank Settings")
        with st.form("settings"):
            bank = st.text_input("Bank Name", settings['bank_name'])
            acc_name = st.text_input("Account Name", settings['account_name'])
            acc_num = st.text_input("Account Number", settings['account_number'])
            if st.form_submit_button("Save"): supabase.table("admin_settings").update({"bank_name":bank,"account_name":acc_name,"account_number":acc_num}).eq("id",1).execute(); st.rerun()