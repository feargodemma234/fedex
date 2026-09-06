import uuid
import requests
import streamlit as st

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="My Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# DARKER BACKGROUND / UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #151a24;
    color: #eeeeee;
}

[data-testid="stHeader"] {
    background: #151a24;
}

[data-testid="stSidebar"] {
    background: #10141c;
}

h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

p, label, span, div {
    color: #e6e6e6;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #242a36 !important;
    color: #ffffff !important;
    border: 1px solid #414958 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #aeb5c2 !important;
}

.stButton > button {
    background: #252c3a;
    color: #ffffff;
    border: 1px solid #4b5565;
    border-radius: 10px;
    min-height: 44px;
}

.stButton > button:hover {
    border-color: #8da2c4;
    color: #ffffff;
}

div[data-testid="stFileUploader"] {
    background: #202631;
    border-radius: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.product-card {
    background: #202631;
    border: 1px solid #394252;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
}

.price {
    font-size: 20px;
    font-weight: 700;
    color: #9fc5ff;
}

.small-muted {
    color: #aeb5c2 !important;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SECRETS
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

FORMSPREE_ENDPOINT = st.secrets.get(
    "FORMSPREE_ENDPOINT",
    ""
)


# =========================================================
# SUPABASE
# =========================================================

@st.cache_resource
def get_supabase():

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(
            flow_type="pkce",
            auto_refresh_token=True,
            persist_session=True
        )
    )


supabase: Client = get_supabase()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "user": None,
    "session": None,
    "cart": {},
    "page": "Home",
    "order_number": None,
    "order_total": 0,
    "auth_message": None,
    "auth_error": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HANDLE SUPABASE EMAIL CONFIRMATION
# =========================================================

try:

    query_params = st.query_params

    code = query_params.get("code")

    if code and not st.session_state.user:

        try:

            response = (
                supabase
                .auth
                .exchange_code_for_session(
                    {
                        "auth_code": code
                    }
                )
            )

            if response.session:

                st.session_state.session = (
                    response.session
                )

                st.session_state.user = (
                    response.user
                    if response.user
                    else response.session.user
                )

                st.session_state.page = "Home"

                st.query_params.clear()

                st.rerun()

        except Exception as e:

            st.session_state.auth_error = (
                f"Email confirmation failed: {e}"
            )


except Exception:
    pass


# =========================================================
# RESTORE SESSION
# =========================================================

if (
    st.session_state.user is None
    and st.session_state.session is not None
):

    try:

        session = st.session_state.session

        supabase.auth.set_session(
            session.access_token,
            session.refresh_token
        )

        user_response = supabase.auth.get_user()

        if user_response.user:

            st.session_state.user = (
                user_response.user
            )

    except Exception:

        st.session_state.user = None
        st.session_state.session = None


# =========================================================
# LOAD PRODUCTS
# =========================================================

SAMPLE_PRODUCTS = [

    {
        "id": "sample-1",
        "name": "Wireless Headphones",
        "description": "Comfortable wireless headphones with clear sound.",
        "price": 49.99,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    },

    {
        "id": "sample-2",
        "name": "Smart Watch",
        "description": "Modern smartwatch for everyday use.",
        "price": 79.99,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"
    },

    {
        "id": "sample-3",
        "name": "Running Shoes",
        "description": "Lightweight shoes designed for comfort.",
        "price": 59.99,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },

    {
        "id": "sample-4",
        "name": "Backpack",
        "description": "Durable backpack for school and travel.",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62"
    },

    {
        "id": "sample-5",
        "name": "Phone Stand",
        "description": "Adjustable stand for phones and tablets.",
        "price": 19.99,
        "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07"
    },

    {
        "id": "sample-6",
        "name": "Portable Speaker",
        "description": "Compact Bluetooth speaker.",
        "price": 34.99,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1"
    }
]


def load_products():

    try:

        response = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        database_products = response.data or []

        if database_products:

            return database_products

    except Exception:

        pass

    return SAMPLE_PRODUCTS


products = load_products()

product_map = {
    str(product["id"]): product
    for product in products
}


# =========================================================
# NAVIGATION
# =========================================================

if st.session_state.user:

    top1, top2, top3, top4 = st.columns(4)

    with top1:

        if st.button(
            "🏠 Store",
            use_container_width=True
        ):

            st.session_state.page = "Home"
            st.rerun()

    with top2:

        if st.button(
            "🛒 Cart",
            use_container_width=True
        ):

            st.session_state.page = "Cart"
            st.rerun()

    with top3:

        if st.button(
            "📦 Orders",
            use_container_width=True
        ):

            st.session_state.page = "Orders"
            st.rerun()

    with top4:

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            try:
                supabase.auth.sign_out()
            except Exception:
                pass

            st.session_state.user = None
            st.session_state.session = None
            st.session_state.cart = {}
            st.session_state.page = "Home"

            st.rerun()


# =========================================================
# AUTH PAGE
# =========================================================

if not st.session_state.user:

    st.title("🛍️ My Store")

    st.write(
        "Create an account or sign in to continue."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    with login_tab:

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True,
            type="primary"
        ):

            if not login_email or not login_password:

                st.error(
                    "Enter your email and password."
                )

            else:

                try:

                    response = (
                        supabase
                        .auth
                        .sign_in_with_password(
                            {
                                "email":
                                    login_email.strip(),

                                "password":
                                    login_password
                            }
                        )
                    )

                    if response.session:

                        st.session_state.session = (
                            response.session
                        )

                        st.session_state.user = (
                            response.user
                        )

                        st.session_state.page = "Home"

                        st.success(
                            "Login successful."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Login did not create a session."
                        )

                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )


    with signup_tab:

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        signup_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "Create Account",
            use_container_width=True,
            type="primary"
        ):

            if not signup_email:

                st.error(
                    "Enter your email."
                )

            elif not signup_password:

                st.error(
                    "Enter a password."
                )

            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            elif signup_password != signup_confirm:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    # Streamlit's current URL.
                    redirect_url = (
                        "https://"
                        + st.context.headers["host"]
                    )

                    response = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email":
                                    signup_email.strip(),

                                "password":
                                    signup_password,

                                "options": {
                                    "email_redirect_to":
                                        redirect_url
                                }
                            }
                        )
                    )

                    if response.session:

                        st.session_state.session = (
                            response.session
                        )

                        st.session_state.user = (
                            response.user
                        )

                        st.session_state.page = "Home"

                        st.success(
                            "Account created."
                        )

                        st.rerun()

                    else:

                        st.success(
                            "Account created! "
                            "Check your email and press "
                            "the confirmation link."
                        )

                except Exception as e:

                    st.error(
                        f"Could not create account: {e}"
                    )


    st.stop()


# =========================================================
# HOME / STORE
# =========================================================

if st.session_state.page == "Home":

    st.title("🛍️ Store")

    st.write(
        f"Welcome, {st.session_state.user.email}"
    )

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search..."
    )

    filtered = products

    if search:

        search_lower = search.lower()

        filtered = [
            p
            for p in products
            if search_lower in
            p["name"].lower()
            or search_lower in
            str(p.get("description", "")).lower()
        ]

    if not filtered:

        st.info("No products found.")

    else:

        columns = st.columns(2)

        for index, product in enumerate(filtered):

            with columns[index % 2]:

                st.markdown(
                    '<div class="product-card">',
                    unsafe_allow_html=True
                )

                image_url = product.get(
                    "image_url"
                )

                if image_url:

                    try:

                        st.image(
                            image_url,
                            use_container_width=True
                        )

                    except Exception:
                        pass

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

                pid = str(product["id"])

                if st.button(
                    "🛒 Add to Cart",
                    key=f"add_{pid}",
                    use_container_width=True
                ):

                    st.session_state.cart[pid] = (
                        st.session_state.cart.get(
                            pid,
                            0
                        ) + 1
                    )

                    st.success(
                        "Added to cart."
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =========================================================
# CART
# =========================================================

elif st.session_state.page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

        if st.button("Continue Shopping"):

            st.session_state.page = "Home"
            st.rerun()

    else:

        total = 0

        for pid in list(
            st.session_state.cart.keys()
        ):

            product = product_map.get(pid)

            if not product:
                continue

            quantity = st.session_state.cart[pid]

            price = float(
                product["price"]
            )

            subtotal = price * quantity

            total += subtotal

            col1, col2, col3, col4 = st.columns(
                [3, 1, 1, 1]
            )

            with col1:

                st.write(
                    f"**{product['name']}**"
                )

                st.write(
                    f"${price:,.2f} each"
                )

            with col2:

                if st.button(
                    "−",
                    key=f"minus_{pid}"
                ):

                    quantity -= 1

                    if quantity <= 0:

                        del st.session_state.cart[pid]

                    else:

                        st.session_state.cart[pid] = quantity

                    st.rerun()

                st.write(
                    f"Qty: {quantity}"
                )

            with col3:

                if st.button(
                    "+",
                    key=f"plus_{pid}"
                ):

                    st.session_state.cart[pid] = (
                        quantity + 1
                    )

                    st.rerun()

            with col4:

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
            use_container_width=True,
            type="primary"
        ):

            st.session_state.page = "Checkout"
            st.rerun()


# =========================================================
# CHECKOUT
# =========================================================

elif st.session_state.page == "Checkout":

    st.title("🧾 Checkout")

    if not st.session_state.cart:

        st.warning(
            "Your cart is empty."
        )

        st.stop()

    total = 0

    for pid, quantity in (
        st.session_state.cart.items()
    ):

        product = product_map.get(pid)

        if product:

            total += (
                float(product["price"])
                * quantity
            )

    st.subheader(
        f"Order Total: ${total:,.2f}"
    )

    # -----------------------------------------------------
    # CUSTOMER INFORMATION
    # -----------------------------------------------------

    st.markdown(
        "### 👤 Customer Information"
    )

    full_name = st.text_input(
        "Full Name",
        key="checkout_full_name",
        placeholder="Enter your full name"
    )

    phone = st.text_input(
        "Phone Number",
        key="checkout_phone",
        placeholder="Enter your phone number"
    )

    address = st.text_area(
        "Delivery Address",
        key="checkout_address",
        placeholder="Enter your full delivery address"
    )

    country = st.text_input(
        "Country",
        value="Nigeria",
        key="checkout_country"
    )

    state = st.text_input(
        "State",
        key="checkout_state",
        placeholder="Enter your state"
    )

    customer_email = st.text_input(
        "Email",
        value=st.session_state.user.email,
        key="checkout_email"
    )

    # -----------------------------------------------------
    # PAYMENT
    # -----------------------------------------------------

      st.markdown(
        "### 📎 Payment Proof"
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
        key="checkout_payment_proof"
    )

    if payment_proof:

        st.success(
            f"✅ File ready: "
            f"{payment_proof.name}"
        )

    # -----------------------------------------------------
    # CONFIRM ORDER
    # -----------------------------------------------------

    if st.button(
        "✅ Confirm Order",
        use_container_width=True,
        type="primary"
    ):

        full_name = st.session_state.get(
            "checkout_full_name",
            ""
        ).strip()

        phone = st.session_state.get(
            "checkout_phone",
            ""
        ).strip()

        address = st.session_state.get(
            "checkout_address",
            ""
        ).strip()

        country = st.session_state.get(
            "checkout_country",
            ""
        ).strip()

        state = st.session_state.get(
            "checkout_state",
            ""
        ).strip()

        customer_email = st.session_state.get(
            "checkout_email",
            ""
        ).strip()

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

            st.stop()

        if payment_proof is None:

            st.error(
                "Please upload your payment proof."
            )

            st.stop()

        order_number = (
            "ORD-"
            + uuid.uuid4().hex[:8].upper()
        )

        file_bytes = (
            payment_proof.getvalue()
        )

        try:

            # =============================================
            # 1. SEND ORDER + FILE TO FORMSPREE
            # =============================================

            if not FORMSPREE_ENDPOINT:

                st.error(
                    "FORMSPREE_ENDPOINT is missing "
                    "from Streamlit secrets."
                )

                st.stop()

            form_message = f"""
NEW ORDER

Order ID:
{order_number}

Customer:
{full_name}

Email:
{customer_email}

Phone:
{phone}

Address:
{address}

Country:
{country}

State:
{state}

Payment Method:
{payment_method}

Payment Proof:
{payment_proof.name}

Total:
${total:,.2f}

Status:
Received

IMPORTANT:
Payment has NOT been verified automatically.
The payment proof must be reviewed.
"""

            with st.spinner(
                "Sending order..."
            ):

                formspree_response = requests.post(
                    FORMSPREE_ENDPOINT,
                    data={
                        "subject":
                            f"New Order - {order_number}",

                        "email":
                            customer_email,

                        "message":
                            form_message,

                        "order_id":
                            order_number,

                        "customer_name":
                            full_name,

                        "phone":
                            phone,

                        "address":
                            address,

                        "country":
                            country,

                        "state":
                            state,

                        "payment_method":
                            payment_method,

                        "total":
                            f"${total:,.2f}"
                    },

                    files={
                        "payment_proof": (
                            payment_proof.name,
                            file_bytes,
                            payment_proof.type
                        )
                    },

                    timeout=30
                )

            if not (
                200
                <= formspree_response.status_code
                < 300
            ):

                raise Exception(
                    "Formspree rejected the submission: "
                    + formspree_response.text
                )

            # =============================================
            # 2. SAVE ORDER IN SUPABASE
            # =============================================

            # IMPORTANT:
            # Your current orders table does not have
            # country/customer_email, so we don't insert
            # those two columns here.

            with st.spinner(
                "Saving order..."
            ):

                order_response = (
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

                        "state":
                            state,

                        "total":
                            total,

                        "payment_method":
                            payment_method,

                        "payment_proof_path":
                            payment_proof.name,

                        "status":
                            "Received"
                    })
                    .execute()
                )

            if not order_response.data:

                raise Exception(
                    "Supabase did not return the new order."
                )

            database_order_id = (
                order_response.data[0]["id"]
            )

            # =============================================
            # 3. SAVE ORDER ITEMS
            # =============================================

            order_items = []

            for pid, quantity in (
                st.session_state.cart.items()
            ):

                product = product_map.get(pid)

                if product:

                    order_items.append({

                        "order_id":
                            database_order_id,

                        "product_id":
                            str(product["id"]),

                        "product_name":
                            product["name"],

                        "price":
                            float(product["price"]),

                        "quantity":
                            quantity
                    })

            if order_items:

                (
                    supabase
                    .table("order_items")
                    .insert(order_items)
                    .execute()
                )

            # =============================================
            # 4. SUCCESS
            # =============================================

            st.session_state.order_number = (
                order_number
            )

            st.session_state.order_total = (
                total
            )

            st.session_state.cart = {}

            st.session_state.page = "Success"

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create order: {e}"
            )


# =========================================================
# SUCCESS
# =========================================================

elif st.session_state.page == "Success":

    st.title("🎉 Order Received")

    st.success(
        "Your order has been successfully received."
    )

    st.write(
        "Your payment proof has been submitted "
        "for review."
    )

    st.warning(
        "Payment is not automatically verified. "
        "Your order will remain under review until "
        "the payment is checked."
    )

    st.markdown(
        f"### Order ID: "
        f"`{st.session_state.order_number}`"
    )

    st.markdown(
        f"### Total: "
        f"${st.session_state.order_total:,.2f}"
    )

    if st.button(
        "📦 View My Orders",
        use_container_width=True
    ):

        st.session_state.page = "Orders"
        st.rerun()

    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True
    ):

        st.session_state.page = "Home"
        st.rerun()


# =========================================================
# ORDERS
# =========================================================

elif st.session_state.page == "Orders":

    st.title("📦 My Orders")

    try:

        response = (
            supabase
            .table("orders")
            .select("*")
            .eq(
                "user_id",
                st.session_state.user.id
            )
            .execute()
        )

        orders = response.data or []

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
                    f"{order.get('order_id', 'Order')} "
                    f"— ${order_total:,.2f}"
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
                        f"**State:** "
                        f"{order.get('state', '')}"
                    )

                    st.write(
                        f"**Date:** "
                        f"{order.get('created_at', '')}"
                    )

                    if order.get(
                        "payment_proof_path"
                    ):

                        st.write(
                            "📎 Payment proof submitted"
                        )

    except Exception as e:

        st.error(
            f"Could not load orders: {e}"
        )