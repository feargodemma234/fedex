import streamlit as st
import requests
import uuid
from supabase import create_client


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="My Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #eef2f7;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #172033;
}

p, label {
    color: #30394d;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {
    background-color: #ffffff;
    color: #172033;
    border-radius: 12px;
}

div[data-testid="stButton"] > button {
    border-radius: 10px;
    min-height: 45px;
    font-weight: 600;
}

div[data-testid="stFileUploader"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 10px;
}

.product-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
}

.price {
    font-size: 22px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

FORMSPREE_ENDPOINT = st.secrets.get(
    "FORMSPREE_ENDPOINT",
    ""
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# SESSION STATE
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "order_number" not in st.session_state:
    st.session_state.order_number = None

if "order_total" not in st.session_state:
    st.session_state.order_total = 0


# =========================================================
# RESTORE SUPABASE SESSION
# =========================================================

if (
    st.session_state.access_token
    and st.session_state.refresh_token
):

    try:

        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        current_user = supabase.auth.get_user().user

        if current_user:
            st.session_state.user = current_user

    except Exception:

        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None


# =========================================================
# LOGIN
# =========================================================

def login():

    email = st.session_state.login_email.strip()
    password = st.session_state.login_password

    if not email or not password:
        st.error("Please enter your email and password.")
        return

    try:

        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not result.session:
            st.error("Could not create a login session.")
            return

        st.session_state.user = result.user

        st.session_state.access_token = (
            result.session.access_token
        )

        st.session_state.refresh_token = (
            result.session.refresh_token
        )

        st.session_state.page = "Store"

        st.success("Login successful!")

        st.rerun()

    except Exception as e:

        error_text = str(e).lower()

        if "email not confirmed" in error_text:
            st.error(
                "Please confirm your email address first."
            )
        else:
            st.error(
                "Login failed. Check your email and password."
            )


# =========================================================
# SIGNUP
# =========================================================

def signup():

    email = st.session_state.signup_email.strip()
    password = st.session_state.signup_password
    confirm = st.session_state.signup_confirm

    if not email:
        st.error("Please enter your email.")
        return

    if not password:
        st.error("Please enter a password.")
        return

    if password != confirm:
        st.error("Passwords do not match.")
        return

    if len(password) < 6:
        st.error(
            "Password must be at least 6 characters."
        )
        return

    try:

        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        st.success(
            "Account created! Check your email and "
            "confirm your account before logging in."
        )

    except Exception as e:

        st.error(str(e))


# =========================================================
# LOGIN / SIGNUP SCREEN
# =========================================================

if st.session_state.user is None:

    st.title("🛍️ My Store")

    st.write(
        "Create an account or login to start shopping."
    )

    login_tab, signup_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # -------------------------
    # LOGIN
    # -------------------------

    with login_tab:

        st.text_input(
            "Email",
            key="login_email"
        )

        st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        st.button(
            "Login",
            on_click=login,
            use_container_width=True
        )

    # -------------------------
    # SIGNUP
    # -------------------------

    with signup_tab:

        st.text_input(
            "Email",
            key="signup_email"
        )

        st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        st.button(
            "Create Account",
            on_click=signup,
            use_container_width=True
        )

    st.stop()


# =========================================================
# LOAD PRODUCTS
# =========================================================

SAMPLE_PRODUCTS = [

    {
        "id": "sample-1",
        "name": "Wireless Headphones",
        "description":
            "Premium wireless headphones with clear sound.",
        "price": 49.99,
        "image_url":
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    },

    {
        "id": "sample-2",
        "name": "Smart Watch",
        "description":
            "Modern smartwatch for everyday use.",
        "price": 79.99,
        "image_url":
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30"
    },

    {
        "id": "sample-3",
        "name": "Running Shoes",
        "description":
            "Comfortable shoes for sports and everyday use.",
        "price": 59.99,
        "image_url":
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },

    {
        "id": "sample-4",
        "name": "Backpack",
        "description":
            "Durable backpack suitable for school and travel.",
        "price": 39.99,
        "image_url":
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62"
    },

    {
        "id": "sample-5",
        "name": "Gaming Mouse",
        "description":
            "Fast and accurate mouse for gaming and work.",
        "price": 29.99,
        "image_url":
            "https://images.unsplash.com/photo-1527814050087-3793815479db"
    },

    {
        "id": "sample-6",
        "name": "Bluetooth Speaker",
        "description":
            "Portable speaker with powerful sound.",
        "price": 44.99,
        "image_url":
            "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1"
    }

]


def load_products():

    try:

        result = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        products = result.data or []

        if products:
            return products

        return SAMPLE_PRODUCTS

    except Exception:

        return SAMPLE_PRODUCTS


products = load_products()

product_map = {
    str(product["id"]): product
    for product in products
}


# =========================================================
# HEADER
# =========================================================

st.title("🛍️ My Store")

user_email = st.session_state.user.email

c1, c2, c3 = st.columns([5, 2, 1])

with c1:

    st.write(
        f"Welcome, **{user_email}**"
    )

with c2:

    if st.button(
        f"🛒 Cart ({sum(st.session_state.cart.values())})",
        use_container_width=True
    ):

        st.session_state.page = "Cart"
        st.rerun()

with c3:

    if st.button(
        "Logout",
        use_container_width=True
    ):

        try:
            supabase.auth.sign_out()
        except:
            pass

        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.cart = {}

        st.rerun()


# =========================================================
# NAVIGATION
# =========================================================

nav1, nav2, nav3 = st.columns(3)

with nav1:

    if st.button(
        "🏪 Store",
        use_container_width=True
    ):

        st.session_state.page = "Store"
        st.rerun()

with nav2:

    if st.button(
        "🛒 Cart",
        use_container_width=True
    ):

        st.session_state.page = "Cart"
        st.rerun()

with nav3:

    if st.button(
        "📦 My Orders",
        use_container_width=True
    ):

        st.session_state.page = "Orders"
        st.rerun()


# =========================================================
# STORE
# =========================================================

if st.session_state.page == "Store":

    st.subheader("Products")

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search for a product..."
    )

    visible_products = products

    if search:

        visible_products = [
            p for p in products
            if (
                search.lower()
                in p["name"].lower()
            )
            or (
                search.lower()
                in (p.get("description") or "").lower()
            )
        ]

    if not visible_products:

        st.info("No products found.")

    else:

        columns = st.columns(3)

        for i, product in enumerate(visible_products):

            with columns[i % 3]:

                st.markdown(
                    '<div class="product-card">',
                    unsafe_allow_html=True
                )

                image_url = product.get(
                    "image_url",
                    ""
                )

                if image_url:

                    st.image(
                        image_url,
                        use_container_width=True
                    )

                st.subheader(
                    product["name"]
                )

                st.write(
                    product.get(
                        "description",
                        ""
                    )
                )

                st.markdown(
                    f'<div class="price">'
                    f'${float(product["price"]):,.2f}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "Add to Cart",
                    key=f"add_{product['id']}",
                    use_container_width=True
                ):

                    pid = str(product["id"])

                    st.session_state.cart[pid] = (
                        st.session_state.cart.get(
                            pid,
                            0
                        ) + 1
                    )

                    st.success(
                        "Added to cart!"
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =========================================================
# CART
# =========================================================

elif st.session_state.page == "Cart":

    st.subheader("🛒 Your Cart")

    if not st.session_state.cart:

        st.info("Your cart is empty.")

        if st.button(
            "Continue Shopping",
            use_container_width=True
        ):

            st.session_state.page = "Store"
            st.rerun()

    else:

        total = 0

        for pid, quantity in list(
            st.session_state.cart.items()
        ):

            product = product_map.get(pid)

            if not product:
                continue

            price = float(product["price"])

            subtotal = price * quantity

            total += subtotal

            c1, c2, c3, c4 = st.columns(
                [3, 1, 1, 1]
            )

            with c1:

                st.write(
                    f"**{product['name']}**"
                )

                st.write(
                    f"${price:.2f} each"
                )

            with c2:

                st.write(
                    f"Quantity: {quantity}"
                )

            with c3:

                if st.button(
                    "➕",
                    key=f"plus_{pid}"
                ):

                    st.session_state.cart[pid] += 1
                    st.rerun()

                if st.button(
                    "➖",
                    key=f"minus_{pid}"
                ):

                    if (
                        st.session_state.cart[pid]
                        > 1
                    ):

                        st.session_state.cart[pid] -= 1

                    else:

                        del st.session_state.cart[pid]

                    st.rerun()

            with c4:

                if st.button(
                    "Remove",
                    key=f"remove_{pid}"
                ):

                    del st.session_state.cart[pid]
                    st.rerun()

            st.divider()

        st.subheader(
            f"Total: ${total:,.2f}"
        )

        if st.button(
            "Proceed to Checkout",
            use_container_width=True
        ):

            st.session_state.page = "Checkout"
            st.rerun()


# =========================================================
# CHECKOUT
# =========================================================

elif st.session_state.page == "Checkout":

    st.subheader("🧾 Checkout")

    if not st.session_state.cart:

        st.warning("Your cart is empty.")
        st.stop()

    # -------------------------
    # CALCULATE TOTAL
    # -------------------------

    total = sum(
        float(product_map[pid]["price"])
        * quantity

        for pid, quantity
        in st.session_state.cart.items()

        if pid in product_map
    )

    st.write(
        f"### Order Total: ${total:,.2f}"
    )

    # -------------------------
    # FORM
    # -------------------------

    with st.form("checkout_form"):

        st.markdown(
            "### 👤 Customer Information"
        )

        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter your phone number"
        )

        address = st.text_area(
            "Delivery Address",
            placeholder="Enter your full delivery address"
        )

        country = st.text_input(
            "Country",
            value="Nigeria"
        )

        state = st.text_input(
            "State",
            placeholder="Enter your state"
        )

        customer_email = st.text_input(
            "Email",
            value=st.session_state.user.email
        )

        # -------------------------
        # PAYMENT
        # -------------------------

        st.markdown(
            "### 💳 Payment"
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "Bank Transfer",
                "Gift Card"
            ]
        )

        # -------------------------
        # PAYMENT PROOF
        # -------------------------

        st.markdown(
            "### 📎 Payment Proof"
        )

        if payment_method == "Bank Transfer":

            st.info(
                "After making your bank transfer, "
                "take a photo of your payment receipt "
                "or choose the receipt from your device."
            )

        else:

            st.info(
                "Upload a photo of your gift-card "
                "payment proof. You can take a new "
                "photo or choose one from your device."
            )

        payment_proof = st.file_uploader(
            "📷 Take Photo / Choose File",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            accept_multiple_files=False,
            help=(
                "On a phone, your browser may provide "
                "the option to use the camera or choose "
                "a file from your device."
            )
        )

        if payment_proof:

            st.success(
                f"✅ File ready: "
                f"{payment_proof.name}"
            )

        # -------------------------
        # CONFIRM
        # -------------------------

        confirm_order = st.form_submit_button(
            "Confirm Order",
            use_container_width=True
        )

    # =====================================================
    # PROCESS ORDER
    # =====================================================

    if confirm_order:

        full_name = full_name.strip()
        phone = phone.strip()
        address = address.strip()
        country = country.strip()
        state = state.strip()
        customer_email = customer_email.strip()

        # -------------------------
        # VALIDATION
        # -------------------------

        missing = []

        if not full_name:
            missing.append("Full Name")

        if not phone:
            missing.append("Phone Number")

        if not address:
            missing.append("Delivery Address")

        if not country:
            missing.append("Country")

        if not state:
            missing.append("State")

        if not customer_email:
            missing.append("Email")

        if missing:

            st.error(
                "Please complete: "
                + ", ".join(missing)
            )

        elif payment_proof is None:

            st.error(
                "Please upload your payment proof "
                "before confirming your order."
            )

        else:

            try:

                # -------------------------
                # VERIFY SESSION
                # -------------------------

                session = (
                    supabase.auth.get_session()
                )

                if not session or not session.user:

                    st.error(
                        "Your login session expired. "
                        "Please log in again."
                    )

                    st.session_state.user = None
                    st.session_state.access_token = None
                    st.session_state.refresh_token = None

                    st.stop()

                # -------------------------
                # ORDER ID
                # -------------------------

                order_number = (
                    "ORD-"
                    + uuid.uuid4().hex[:8].upper()
                )

                # -------------------------
                # FILE
                # -------------------------

                file_bytes = (
                    payment_proof.getvalue()
                )

                file_extension = (
                    payment_proof.name
                    .split(".")[-1]
                    .lower()
                )

                file_path = (
                    f"{st.session_state.user.id}/"
                    f"{order_number}."
                    f"{file_extension}"
                )

                # -------------------------
                # UPLOAD PAYMENT PROOF
                # -------------------------

                supabase.storage.from_(
                    "payment-proofs"
                ).upload(
                    file_path,
                    file_bytes,
                    {
                        "content-type":
                            payment_proof.type,
                        "upsert": "false"
                    }
                )

                # -------------------------
                # CREATE ORDER
                # -------------------------

                order = (
                    supabase
                    .table("orders")
                    .insert({
                        "user_id":
                            st.session_state.user.id,

                        "order_id":
                            order_number,

                        "full_name":
                            full_name,

                        "phone":
                            phone,

                        "address":
                            address,

                        "country":
                            country,

                        "state":
                            state,

                        "customer_email":
                            customer_email,

                        "total":
                            total,

                        "payment_method":
                            payment_method,

                        "payment_proof_path":
                            file_path,

                        "status":
                            "Received"
                    })
                    .execute()
                )

                if not order.data:

                    raise Exception(
                        "The order was not created."
                    )

                order_db_id = (
                    order.data[0]["id"]
                )

                # -------------------------
                # ORDER ITEMS
                # -------------------------

                items = []

                for pid, quantity in (
                    st.session_state.cart.items()
                ):

                    product = product_map.get(pid)

                    if product:

                        items.append({
                            "order_id":
                                order_db_id,

                            "product_id":
                                str(product["id"]),

                            "product_name":
                                product["name"],

                            "price":
                                float(product["price"]),

                            "quantity":
                                quantity
                        })

                if items:

                    (
                        supabase
                        .table("order_items")
                        .insert(items)
                        .execute()
                    )

                # -------------------------
                # FORMSPREE
                # -------------------------

                if FORMSPREE_ENDPOINT:

                    message = f"""
NEW ORDER

Order ID:
{order_number}

Customer:
{full_name}

Email:
{customer_email}

Phone:
{phone}

Delivery Address:
{address}

Country:
{country}

State:
{state}

Payment Method:
{payment_method}

Payment Proof File:
{payment_proof.name}

Total:
${total:,.2f}

Status:
Received

IMPORTANT:
Payment has NOT been verified yet.
"""

                    try:

                        requests.post(
                            FORMSPREE_ENDPOINT,

                            data={
                                "subject":
                                    f"New Order - "
                                    f"{order_number}",

                                "message":
                                    message,

                                "email":
                                    customer_email
                            },

                            files={
                                "payment_proof": (
                                    payment_proof.name,
                                    file_bytes,
                                    payment_proof.type
                                )
                            },

                            timeout=20
                        )

                    except Exception:

                        st.warning(
                            "The order was saved, but "
                            "the Formspree notification "
                            "could not be sent."
                        )

                # -------------------------
                # SUCCESS
                # -------------------------

                st.session_state.cart = {}

                st.session_state.order_number = (
                    order_number
                )

                st.session_state.order_total = (
                    total
                )

                st.session_state.page = (
                    "Success"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not create order: {e}"
                )


# =========================================================
# SUCCESS
# =========================================================

elif st.session_state.page == "Success":

    st.success(
        "🎉 Order placed successfully!"
    )

    st.write(
        "### Order ID"
    )

    st.code(
        st.session_state.order_number
    )

    st.write(
        f"**Total:** "
        f"${st.session_state.order_total:,.2f}"
    )

    st.info(
        "Your order has been received. "
        "Payment has NOT been automatically verified."
    )

    if st.button(
        "🏪 Back to Store",
        use_container_width=True
    ):

        st.session_state.page = "Store"
        st.rerun()


# =========================================================
# MY ORDERS
# =========================================================

elif st.session_state.page == "Orders":

    st.subheader("📦 My Orders")

    try:
        result = (
            supabase
            .table("orders")
            .select("*")
            .eq(
                "user_id",
                st.session_state.user.id
            )
            .execute()
        )

        orders = result.data or []

        if not orders:

            st.info(
                "You haven't placed any orders yet."
            )

        else:

            for order in orders:

                order_total = float(
                    order.get("total", 0)
                )

                with st.expander(
                    f"{order.get('order_id', 'Order')} — "
                    f"${order_total:,.2f}"
                ):

                    st.write(
                        f"**Status:** "
                        f"{order.get('status', 'Received')}"
                    )

                    st.write(
                        f"**Payment:** "
                        f"{order.get('payment_method', '')}"
                    )

                    st.write(
                        f"**Name:** "
                        f"{order.get('full_name', '')}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{order.get('phone', '')}"
                    )

                    st.write(
                        f"**Address:** "
                        f"{order.get('address', '')}"
                    )

                    st.write(
                        f"**Country:** "
                        f"{order.get('country', '')}"
                    )

                    st.write(
                        f"**State:** "
                        f"{order.get('state', '')}"
                    )

                    st.write(
                        f"**Email:** "
                        f"{order.get('customer_email', '')}"
                    )

                    st.write(
                        f"**Date:** "
                        f"{order.get('created_at', '')}"
                    )

                    if order.get("payment_proof_path"):

                        st.write(
                            "📎 Payment proof uploaded"
                        )

    except Exception as e:

        st.error(
            f"Could not load orders: {e}"
        )
        