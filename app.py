import streamlit as st
import uuid
import smtplib
import qrcode
import base64
from io import BytesIO
from email.message import EmailMessage
from supabase import create_client, Client
from datetime import datetime
from urllib.parse import quote

st.set_page_config(page_title="FedEx Store", page_icon="📦", layout="wide")

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
.info-box {background: #1e3a8a; padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; color: #bfdbfe;}
.btc-box {background: #f97316; padding: 20px; border-radius: 12px; border: 2px solid #fb923c; color: #fff; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "checkout_info" not in st.session_state: st.session_state.checkout_info = None

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS

def logout():
    supabase.auth.sign_out()
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# ========== EMAIL FUNCTION ==========
def send_order_email(order_code, customer_info, cart_items, total, payment_method, proof_note):
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
BTC Address: {customer_info.get('btc_address', 'N/A')}

PRODUCTS ORDERED
{items_text}

TOTAL: ${total:.2f}
PAYMENT METHOD: {payment_method}
PROOF STATUS: {proof_note}
"""
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# ========== DB HELPERS ==========
@st.cache_data(ttl=60)
def load_products():
    try:
        res = supabase.table("products").select("*").execute()
        if res.data: return res.data
    except: pass
    return [
        {"id": str(uuid.uuid4()), "name": "Wireless Headphones", "description": "Noise cancelling bluetooth", "price": 49.99, "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
        {"id": str(uuid.uuid4()), "name": "Bluetooth Speaker", "description": "Portable waterproof speaker", "price": 34.99, "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"},
        {"id": str(uuid.uuid4()), "name": "Smart Watch", "description": "Fitness tracker with heart rate", "price": 89.99, "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"},
        {"id": str(uuid.uuid4()), "name": "Wireless Mouse", "description": "Ergonomic gaming mouse", "price": 24.99, "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
        {"id": str(uuid.uuid4()), "name": "Sneakers", "description": "Casual running sneakers", "price": 85.00, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"},
    ]

@st.cache_data(ttl=30)
def get_admin_settings():
    try:
        res = supabase.table("admin_settings").select("*").eq("id", 1).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except: pass

    default = {
        "id": 1, "bank_name": "Opay", "account_name": "Deborah Oluchukwu Phillips",
        "account_number": "9032113433", "bank_instructions": "Transfer",
        "giftcard_instructions": "Buy card and upload photo",
        "btc_address": "bc1qtl8hcsssakafwa4a9xrzjfl8thwdkjdmv292tm" # YOUR BTC ADDRESS
    }
    try: supabase.table("admin_settings").insert(default).execute()
    except: pass
    return default

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]: item["quantity"] += 1; return
    st.session_state.cart.append({**product, "quantity": 1})

def cart_total(): return sum(item["price"] * item["quantity"] for item in st.session_state.cart)

# ========== AUTH ==========
def sign_up(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user: return True, "Account created! Check your email to confirm."
        return False, "Signup failed. Please try again."
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg: return False, "Too many signups. Wait 1 hour."
        elif "already registered" in error_msg: return False, "This email already has an account."
        else: return False, "Signup failed."

def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state.user = res.user
            return True, "Logged in!"
        return False, "Login failed."
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid login" in error_msg: return False, "Wrong email or password."
        elif "email not confirmed" in error_msg: return False, "Please confirm your email first."
        else: return False, "Login failed."

if not st.session_state.user:
    st.title("📦 FedEx Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            success, msg = sign_in(email, password)
            if success: st.rerun()
            else: st.error(msg)

    with tab2:
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if password!= confirm:
                st.error("Passwords don't match")
            else:
                success, msg = sign_up(email, password)
                if success: st.success(msg)
                else: st.error(msg)

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
settings = get_admin_settings()

# ========== STORE ==========
if st.session_state.page == "Store":
    st.title("📦 FedEx Store")
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

# ========== CHECKOUT INFO PAGE ==========
elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")
    st.subheader("1. Customer Information")
    with st.form("customer_info"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        country = st.text_input("Country")
        state = st.text_input("State")
        btc_address = st.text_input("Your BTC Wallet Address (Optional)", placeholder="bc1q... for refunds")
        customer_email = st.text_input("Email", value=st.session_state.user.email)

        if st.form_submit_button("Save & Continue to Payment", use_container_width=True):
            if not all([full_name, phone, address, country, state]):
                st.error("Fill all required fields")
            else:
                st.session_state.checkout_info = {
                    "full_name": full_name, "phone": phone, "address": address,
                    "country": country, "state": state, "email": customer_email,
                    "btc_address": btc_address
                }
                st.session_state.page = "Payment"
                st.rerun()

# ========== PAYMENT PAGE ==========
elif st.session_state.page == "Payment":
    st.title("💳 Payment")

    info = st.session_state.get("checkout_info")
    if not info:
        st.error("Please fill customer info first")
        if st.button("Back"): st.session_state.page = "Checkout"; st.rerun()
        st.stop()

    st.subheader("Order Summary")
    for item in st.session_state.cart:
        st.write(f"**{item['name']}** x {item['quantity']} = ${item['price']*item['quantity']:.2f}")
    st.markdown(f"### Total: ${cart_total():.2f}")
    st.divider()

    st.subheader("2. Choose Payment Method")
    payment_method = st.radio("Payment Method", ["Bank Transfer", "Gift Card", "Bitcoin (BTC)"], horizontal=True)

    btc_addr = settings['btc_address']
    if payment_method == "Bank Transfer":
        st.markdown(f"""<div class="store-card"><h3>🏦 Bank Transfer Details</h3><p><b>Bank:</b> {settings['bank_name']}</p><p><b>Account Name:</b> {settings['account_name']}</p><p><b>Account Number:</b> {settings['account_number']}</p></div>""", unsafe_allow_html=True)
    elif payment_method == "Gift Card":
        st.markdown(f"""<div class="store-card"><h3>🎁 Gift Card</h3><p>{settings['giftcard_instructions']}</p></div>""", unsafe_allow_html=True)
    else: # BTC WITH QR CODE
        qr = qrcode.make(f"bitcoin:{btc_addr}?amount={cart_total():.2f}")
        buf = BytesIO()
        qr.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        st.markdown(f"""<div class="btc-box">
            <h3>₿ Pay with Bitcoin</h3>
            <img src="data:image/png;base64,{b64}" width="220">
            <p style="margin-top:10px;">Send <b>${cart_total():.2f}</b> to:</p>
            <p style="font-family:monospace;font-size:13px;word-break:break-all;background:#000;padding:10px;border-radius:8px;">{btc_addr}</p>
            <p>After sending, take screenshot and email it below.</p>
        </div>""", unsafe_allow_html=True)

    order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    items_list = "\n".join([f"- {i['name']} x {i['quantity']}" for i in st.session_state.cart])
    subject = quote(f"Payment Proof - {order_code}")
    body = quote(f"""Hello FedEx Store,

I am sending payment proof for my order.

Order Number: {order_code}
Name: {info['full_name']}
Email: {info['email']}
Phone: {info['phone']}
BTC Address: {info.get('btc_address', 'N/A')}
Payment Method: {payment_method}

PRODUCTS:
{items_list}

Order Total: ${cart_total():.2f}

I have attached my payment proof/screenshot.

Thank you.""")

    mailto_link = f"mailto:{STORE_EMAIL}?subject={subject}&body={body}"

    st.markdown(f"""<a href="{mailto_link}" target="_blank" style="display:block;text-align:center;background:#2563eb;color:white;padding:15px;border-radius:10px;text-decoration:none;font-weight:700;font-size:17px;margin-top:10px;">📎 Send Payment Proof via Gmail</a>""", unsafe_allow_html=True)

    st.markdown('<div class="info-box">Add image proof of payment to the email, then tap Confirm Order below</div>', unsafe_allow_html=True)

    if st.button("✅ Confirm Order - I have sent the proof", use_container_width=True):
        try:
            order_data = {
                "order_code": order_code, "user_id": st.session_state.user.id,
                "full_name": info['full_name'], "phone": info['phone'], "address": info['address'],
                "country": info['country'], "state": info['state'], "customer_email": info['email'],
                "btc_address": info.get('btc_address'),
                "payment_method": payment_method, "payment_proof_url": None,
                "total": cart_total(), "status": "Received"
            }
            order_res = supabase.table("orders").insert(order_data).execute()
            order_id = order_res.data[0]["id"]

            items = [{
                "order_id": order_id, "product_id": i["id"], "product_name": i["name"],
                "quantity": i["quantity"], "unit_price": i["price"]
            } for i in st.session_state.cart]
            supabase.table("order_items").insert(items).execute()

            send_order_email(order_code, info, st.session_state.cart, cart_total(), payment_method, "Customer will send via Gmail")

            st.session_state.cart = []
            st.session_state.checkout_info = None
            st.session_state.page = "Confirmation"
            st.session_state.last_order = order_code
            st.rerun()
        except Exception as e:
            st.error(f"Order failed: {e}")

    if st.button("← Back to Info"): st.session_state.page = "Checkout"; st.rerun()

# ========== CONFIRMATION ==========
elif st.session_state.page == "Confirmation":
    st.markdown(f'<div class="success-box"><h2>✅ Order Received!</h2><p>Order ID: <strong>{st.session_state.last_order}</strong></p><p>We will confirm your payment soon.</p></div>', unsafe_allow_html=True)
    if st.button("Continue Shopping"): st.session_state.page = "Store"; st.rerun()

# ========== ADMIN ==========
elif st.session_state.page == "Admin" and is_admin():
    st.title("⚙️ Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Orders", "Products", "Settings"])
    with tab1:
        orders = supabase.table("orders").select("*").order("created_at", desc=True).execute().data
        for o in orders:
            st.write(f"**{o['order_code']}** - {o['full_name']} - ${o['total']} - {o['payment_method']} - BTC: {o.get('btc_address', 'N/A')}")
            new_status = st.selectbox("Status", ["Received","Payment Under Review","Payment Confirmed","Processing","Completed","Cancelled"], key=o["id"])
            if st.button("Update", key=f"up_{o['id']}"):
                supabase.table("orders").update({"status": new_status}).eq("id", o["id"]).execute(); st.rerun()