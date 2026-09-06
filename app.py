import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
from supabase import create_client, Client


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Industries Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DARK NAVY UI
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #07111f;
        color: #f4f7fb;
    }

    .main {
        background: #07111f;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, label, span, div {
        color: #e8edf5;
    }

    /* Inputs */
    input, textarea, select {
        background-color: #111d2d !important;
        color: #ffffff !important;
        border: 1px solid #304158 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #111d2d !important;
        color: #ffffff !important;
        border-color: #304158 !important;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #38506d;
        background: #13243a;
        color: #ffffff;
        font-weight: 600;
        padding: 0.65rem 1rem;
    }

    .stButton > button:hover {
        background: #1b3452;
        border-color: #55779e;
        color: #ffffff;
    }

    /* Cards */
    .product-card {
        background: #101c2c;
        border: 1px solid #263a52;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 20px;
        min-height: 100%;
    }

    .product-card img {
        width: 100%;
        height: 210px;
        object-fit: cover;
        border-radius: 12px;
    }

    .product-name {
        font-size: 20px;
        font-weight: 700;
        margin-top: 12px;
        color: #ffffff;
    }

    .product-description {
        color: #b8c4d4;
        min-height: 55px;
        margin-top: 8px;
    }

    .price {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin: 10px 0;
    }

    .cart-box {
        background: #101c2c;
        border: 1px solid #263a52;
        padding: 18px;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    .order-box {
        background: #101c2c;
        border: 1px solid #263a52;
        border-radius: 16px;
        padding: 24px;
    }

    /* File uploader */
    section[data-testid="stFileUploader"] {
        background: #101c2c;
        border-radius: 12px;
        padding: 8px;
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px;
    }

    /* Hide Streamlit menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: #07111f !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SECRETS
# ============================================================

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
    SMTP_APP_PASSWORD = st.secrets["SMTP_APP_PASSWORD"]

except Exception:
    st.error("Missing required secrets in .streamlit/secrets.toml")
    st.stop()


STORE_EMAIL = "quantumindustries258@gmail.com"


# ============================================================
# SUPABASE
# ============================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


supabase = get_supabase()


# ============================================================
# SESSION STATE
# ============================================================

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

if "order_confirmation" not in st.session_state:
    st.session_state.order_confirmation = None


# ============================================================
# SESSION HELPERS
# ============================================================

def restore_session():
    """
    Restore the Supabase session after Streamlit reruns.
    """

    if (
        st.session_state.access_token
        and st.session_state.refresh_token
    ):
        try:
            supabase.auth.set_session(
                st.session_state.access_token,
                st.session_state.refresh_token,
            )

            session = supabase.auth.get_session()

            if session and session.user:
                st.session_state.user = session.user
                return True

        except Exception:
            pass

    return False


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.cart = {}
    st.session_state.page = "Store"
    st.session_state.order_confirmation = None

    st.rerun()


# ============================================================
# EMAIL FUNCTION
# ============================================================

def send_order_email(
    order_code,
    full_name,
    customer_email,
    phone,
    address,
    country,
    state,
    payment_method,
    total,
    cart_items,
    proof_bytes=None,
    proof_name=None,
    proof_type=None,
):
    """
    Sends the order directly through Gmail SMTP.

    The payment proof is attached to the email.
    """

    msg = EmailMessage()

    msg["Subject"] = f"NEW ORDER - {order_code}"
    msg["From"] = SMTP_EMAIL
    msg["To"] = STORE_EMAIL

    if customer_email:
        msg["Reply-To"] = customer_email

    # --------------------------------------------------------
    # Build product list
    # --------------------------------------------------------

    product_lines = []

    for item in cart_items:
        name = item["name"]
        quantity = item["quantity"]
        price = float(item["price"])

        line_total = quantity * price

        product_lines.append(
            f"{name} x {quantity} - ${line_total:.2f}"
        )

    products_text = "\n".join(product_lines)

    # --------------------------------------------------------
    # Email body
    # --------------------------------------------------------

    body = f"""
NEW ORDER RECEIVED
==================

Order ID:
{order_code}


CUSTOMER INFORMATION
====================

Name:
{full_name}

Email:
{customer_email}

Phone:
{phone}


DELIVERY INFORMATION
====================

Address:
{address}

Country:
{country}

State:
{state}


ORDER INFORMATION
=================

Payment Method:
{payment_method}

Products:
{products_text}

Total:
${total:.2f}


ORDER STATUS
============

Payment Under Review


IMPORTANT
=========

The customer has submitted payment proof.

The payment has NOT been automatically confirmed.

Please review the attached payment proof before changing
the order status to "Payment Confirmed".


This message was automatically generated by
Quantum Industries Store.
"""

    msg.set_content(body)

    # --------------------------------------------------------
    # Attach payment proof
    # --------------------------------------------------------

    if proof_bytes and proof_name:

        maintype = "application"
        subtype = "octet-stream"

        if proof_type and "/" in proof_type:
            maintype, subtype = proof_type.split("/", 1)

        msg.add_attachment(
            proof_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=proof_name,
        )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=30,
        ) as smtp:

            smtp.login(
                SMTP_EMAIL,
                SMTP_APP_PASSWORD,
            )

            smtp.send_message(msg)

        return True, None

    except Exception as e:

        return False, str(e)


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

SAMPLE_PRODUCTS = [
    {
        "id": "sample-1",
        "name": "Quantum Wireless Headphones",
        "description": "Premium wireless headphones with clear sound and comfortable design.",
        "price": 39.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-2",
        "name": "Smart Watch Pro",
        "description": "Modern smartwatch for notifications, activity tracking and everyday use.",
        "price": 59.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-3",
        "name": "Wireless Speaker",
        "description": "Portable Bluetooth speaker designed for powerful everyday audio.",
        "price": 29.99,
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-4",
        "name": "Premium Backpack",
        "description": "Durable everyday backpack with a clean modern design.",
        "price": 34.99,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-5",
        "name": "Mechanical Keyboard",
        "description": "Responsive mechanical keyboard suitable for work, school and gaming.",
        "price": 49.99,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-6",
        "name": "Wireless Mouse",
        "description": "Comfortable wireless mouse with a clean ergonomic design.",
        "price": 19.99,
        "image": "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80",
    },
]


# ============================================================
# LOAD PRODUCTS
# ============================================================

@st.cache_data(ttl=60)
def load_products():

    products = []

    try:

        result = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        db_products = result.data or []

        for product in db_products:

            product_id = product.get("id")

            name = (
                product.get("name")
                or product.get("title")
                or "Product"
            )

            description = (
                product.get("description")
                or ""
            )

            price = (
                product.get("price")
                or product.get("unit_price")
                or 0
            )

            image = (
                product.get("image")
                or product.get("image_url")
                or product.get("image_path")
                or ""
            )

            products.append(
                {
                    "id": str(product_id),
                    "name": name,
                    "description": description,
                    "price": float(price),
                    "image": image,
                }
            )

    except Exception:
        products = []

    # --------------------------------------------------------
    # Add samples if missing
    # --------------------------------------------------------

    existing_ids = {
        str(product["id"])
        for product in products
    }

    for sample in SAMPLE_PRODUCTS:

        if sample["id"] not in existing_ids:

            products.append(sample)

    return products


products = load_products()


# ============================================================
# PRODUCT HELPERS
# ============================================================

def get_product(product_id):

    for product in products:

        if str(product["id"]) == str(product_id):
            return product

    return None


def add_to_cart(product_id):

    product_id = str(product_id)

    if product_id not in st.session_state.cart:

        st.session_state.cart[product_id] = 1

    else:

        st.session_state.cart[product_id] += 1


def remove_from_cart(product_id):

    product_id = str(product_id)

    if product_id in st.session_state.cart:

        st.session_state.cart[product_id] -= 1

        if st.session_state.cart[product_id] <= 0:

            del st.session_state.cart[product_id]


def delete_from_cart(product_id):

    product_id = str(product_id)

    if product_id in st.session_state.cart:

        del st.session_state.cart[product_id]


def cart_items():

    items = []

    for product_id, quantity in st.session_state.cart.items():

        product = get_product(product_id)

        if not product:
            continue

        items.append(
            {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": float(product["price"]),
                "image": product["image"],
                "quantity": quantity,
            }
        )

    return items


def cart_total():

    total = 0.0

    for item in cart_items():

        total += (
            item["price"] *
            item["quantity"]
        )

    return total


def money(amount):

    return f"${float(amount):,.2f}"


# ============================================================
# AUTH
# ============================================================

def authentication_page():

    st.markdown(
        """
        <div style="text-align:center; padding-top:40px;">
            <h1>🛍️ Quantum Industries Store</h1>
            <p>Welcome to our online store</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email",
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "Login",
            key="login_button",
        ):

            if not login_email or not login_password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = (
                        supabase.auth
                        .sign_in_with_password(
                            {
                                "email": login_email,
                                "password": login_password,
                            }
                        )
                    )

                    if response.user:

                        st.session_state.user = response.user

                        if response.session:

                            st.session_state.access_token = (
                                response.session.access_token
                            )

                            st.session_state.refresh_token = (
                                response.session.refresh_token
                            )

                        st.success(
                            "Login successful!"
                        )

                        st.rerun()

                except Exception as e:

                    error_text = str(e)

                    if "Email not confirmed" in error_text:

                        st.warning(
                            "Please confirm your email address "
                            "before logging in."
                        )

                    else:

                        st.error(
                            f"Login failed: {error_text}"
                        )

    # ========================================================
    # SIGNUP
    # ========================================================

    with signup_tab:

        st.subheader("Create Account")

        signup_email = st.text_input(
            "Email",
            key="signup_email",
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password",
        )

        signup_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm",
        )

        if st.button(
            "Create Account",
            key="signup_button",
        ):

            if not signup_email:

                st.error("Enter your email.")

            elif not signup_password:

                st.error("Enter a password.")

            elif signup_password != signup_confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    response = (
                        supabase.auth
                        .sign_up(
                            {
                                "email": signup_email,
                                "password": signup_password,
                            }
                        )
                    )

                    st.success(
                        "Account created! "
                        "Check your email and confirm your account."
                    )

                except Exception as e:

                    st.error(
                        f"Signup failed: {e}"
                    )


# ============================================================
# CHECK EMAIL CONFIRMATION CODE
# ============================================================

query_params = st.query_params

if "code" in query_params:

    code = query_params.get("code")

    if code:

        try:

            response = (
                supabase.auth
                .exchange_code_for_session(code)
            )

            if response and response.session:

                st.session_state.access_token = (
                    response.session.access_token
                )

                st.session_state.refresh_token = (
                    response.session.refresh_token
                )

                st.session_state.user = (
                    response.user
                )

                st.query_params.clear()

                st.success(
                    "Email confirmed successfully!"
                )

                st.rerun()

        except Exception:

            pass


# ============================================================
# RESTORE AUTH
# ============================================================

if not st.session_state.user:

    restore_session()


# ============================================================
# SHOW AUTH PAGE IF LOGGED OUT
# ============================================================

if not st.session_state.user:
    authentication_page()
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛍️ Quantum Store")

    user_email = getattr(
        st.session_state.user,
        "email",
        ""
    )

    st.caption(user_email)

    st.divider()

    if st.button("🏪 Store", key="sidebar_store"):

        st.session_state.page = "Store"
        st.rerun()

    if st.button(
        f"🛒 Cart ({sum(st.session_state.cart.values())})",
        key="sidebar_cart"
    ):

        st.session_state.page = "Cart"
        st.rerun()

    if st.button(
        "💳 Checkout",
        key="sidebar_checkout"
    ):

        if st.session_state.cart:

            st.session_state.page = "Checkout"
            st.rerun()

        else:

            st.warning("Your cart is empty.")


    st.divider()

    if st.button(
        "🚪 Logout",
        key="sidebar_logout"
    ):

        logout()


# ============================================================
# TOP NAVIGATION
# ============================================================

top1, top2, top3, top4 = st.columns(
    [3, 1, 1, 1]
)

with top1:

    st.markdown(
        "# 🛍️ Quantum Industries Store"
    )

with top2:

    if st.button(
        "Store",
        key="top_store"
    ):

        st.session_state.page = "Store"
        st.rerun()

with top3:

    if st.button(
        "Cart",
        key="top_cart"
    ):

        st.session_state.page = "Cart"
        st.rerun()

with top4:

    if st.button(
        "Checkout",
        key="top_checkout"
    ):

        if st.session_state.cart:

            st.session_state.page = "Checkout"
            st.rerun()

        else:

            st.warning(
                "Your cart is empty."
            )


st.divider()


# ============================================================
# STORE PAGE
# ============================================================

if st.session_state.page == "Store":

    st.subheader("Featured Products")

    if not products:

        st.warning(
            "No products available."
        )

    else:

        columns = st.columns(3)

        for index, product in enumerate(products):

            with columns[index % 3]:

                if product.get("image"):

                    st.markdown(
                        f"""
                        <div class="product-card">

                            <img
                                src="{product['image']}"
                                alt="{product['name']}"
                            >

                            <div class="product-name">
                                {product['name']}
                            </div>

                            <div class="product-description">
                                {product['description']}
                            </div>

                            <div class="price">
                                {money(product['price'])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="product-card">

                            <div class="product-name">
                                {product['name']}
                            </div>

                            <div class="product-description">
                                {product['description']}
                            </div>

                            <div class="price">
                                {money(product['price'])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if st.button(
                    "🛒 Add to Cart",
                    key=f"add_{product['id']}"
                ):

                    add_to_cart(
                        product["id"]
                    )

                    st.success(
                        f"{product['name']} added to cart."
                    )


# ============================================================
# CART PAGE
# ============================================================

elif st.session_state.page == "Cart":

    st.subheader("🛒 Your Cart")

    items = cart_items()

    if not items:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "Continue Shopping",
            key="continue_shopping_empty"
        ):

            st.session_state.page = "Store"
            st.rerun()

    else:

        for item in items:

            st.markdown(
                '<div class="cart-box">',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(
                [3, 1, 1, 1]
            )

            with col1:

                st.markdown(
                    f"### {item['name']}"
                )

                st.write(
                    money(item["price"])
                )

            with col2:

                st.write(
                    f"Quantity: {item['quantity']}"
                )

            with col3:

                if st.button(
                    "➖",
                    key=f"minus_{item['id']}"
                ):

                    remove_from_cart(
                        item["id"]
                    )

                    st.rerun()

                if st.button(
                    "➕",
                    key=f"plus_{item['id']}"
                ):

                    add_to_cart(
                        item["id"]
                    )

                    st.rerun()

            with col4:

                if st.button(
                    "🗑️ Remove",
                    key=f"remove_{item['id']}"
                ):

                    delete_from_cart(
                        item["id"]
                    )

                    st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        st.divider()

        total = cart_total()

        st.markdown(
            f"## Total: {money(total)}"
        )

        if st.button(
            "💳 Proceed to Checkout",
            key="cart_checkout"
        ):

            st.session_state.page = "Checkout"
            st.rerun()


# ============================================================
# CHECKOUT PAGE
# ============================================================

elif st.session_state.page == "Checkout":

    st.subheader("💳 Checkout")

    items = cart_items()

    if not items:

        st.warning(
            "Your cart is empty."
        )

        if st.button(
            "Return to Store",
            key="return_store_empty_checkout"
        ):

            st.session_state.page = "Store"
            st.rerun()

        st.stop()

    total = cart_total()


    # --------------------------------------------------------
    # ORDER SUMMARY
    # --------------------------------------------------------

    st.markdown(
        "### 🛒 Order Summary"
    )

    for item in items:

        line_total = (
            item["price"] *
            item["quantity"]
        )

        st.write(
            f"**{item['name']}** × "
            f"{item['quantity']} — "
            f"{money(line_total)}"
        )

    st.markdown(
        f"### Total: {money(total)}"
    )

    st.divider()


    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    st.markdown(
        "### 👤 Customer Information"
    )

    full_name = st.text_input(
        "Full Name",
        key="checkout_full_name"
    )

    customer_email = st.text_input(
        "Email",
        value=getattr(
            st.session_state.user,
            "email",
            ""
        ),
        key="checkout_email"
    )

    phone = st.text_input(
        "Phone Number",
        key="checkout_phone"
    )


    # --------------------------------------------------------
    # DELIVERY INFORMATION
    # --------------------------------------------------------

    st.markdown(
        "### 📍 Delivery Information"
    )

    address = st.text_area(
        "Delivery Address",
        key="checkout_address",
        height=100
    )

    country = st.text_input(
        "Country",
        key="checkout_country"
    )

    state = st.text_input(
        "State",
        key="checkout_state"
    )


    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    st.markdown(
        "### 💰 Payment Method"
    )

    payment_method = st.selectbox(
        "Select Payment Method",
        [
            "Bank Transfer",
            "Gift Card"
        ],
        key="checkout_payment_method"
    )


    # --------------------------------------------------------
    # PAYMENT PROOF
    # --------------------------------------------------------

    st.markdown(
        "### 📎 Payment Proof"
    )

    st.info(
        "Upload a screenshot or image showing your payment proof."
    )

    proof = st.file_uploader(
        "Choose payment proof",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        key="checkout_payment_proof"
    )

    proof_bytes = None
    proof_name = None
    proof_type = None

    if proof:

        proof_bytes = proof.getvalue()
        proof_name = proof.name
        proof_type = proof.type

        st.success(
            f"File ready: {proof.name}"
        )


    st.divider()


    # ========================================================
    # CONFIRM ORDER
    # ========================================================

    if st.button(
        "✅ Confirm Order",
        key="confirm_order"
    ):

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        missing = []

        if not full_name.strip():

            missing.append(
                "Full Name"
            )

        if not customer_email.strip():

            missing.append(
                "Email"
            )

        if not phone.strip():

            missing.append(
                "Phone Number"
            )

        if not address.strip():

            missing.append(
                "Delivery Address"
            )

        if not country.strip():

            missing.append(
                "Country"
            )

        if not state.strip():

            missing.append(
                "State"
            )

        if not proof:

            missing.append(
                "Payment Proof"
            )

        if missing:

            st.error(
                "Please complete: "
                + ", ".join(missing)
            )

            st.stop()


        # ----------------------------------------------------
        # CREATE ORDER ID
        # ----------------------------------------------------

        order_id = str(
            uuid.uuid4()
        )

        order_code = (
            "ORD-"
            + uuid.uuid4()
            .hex[:8]
            .upper()
        )

        order_status = (
            "Payment Under Review"
        )


        # ----------------------------------------------------
        # SAVE ORDER TO SUPABASE
        # ----------------------------------------------------

        try:

            order_row = {

                "id": order_id,

                "user_id": str(
                    st.session_state.user.id
                ),

                "order_code": order_code,

                "full_name": full_name.strip(),

                "phone": phone.strip(),

                "address": address.strip(),

                "payment_method": payment_method,

                "total": float(total),

                "status": order_status,

                "payment_proof_path": proof_name
            }

            order_result = (
                supabase
                .table("orders")
                .insert(order_row)
                .execute()
            )

            if not order_result.data:

                st.error(
                    "Could not save the order."
                )

                st.stop()

        except Exception as e:

            st.error(
                f"Could not create order: {e}"
            )

            st.stop()


        # ----------------------------------------------------
        # SAVE ORDER ITEMS
        # ----------------------------------------------------

        try:

            order_items_rows = []

            for item in items:

                order_items_rows.append(
                    {

                        "order_id": order_id,

                        "product_id": str(
                            item["id"]
                        ),

                        "product_name": item["name"],

                        "quantity": int(
                            item["quantity"]
                        ),

                        "unit_price": float(
                            item["price"]
                        )

                    }
                )

            if order_items_rows:

                (
                    supabase
                    .table("order_items")
                    .insert(
                        order_items_rows
                    )
                    .execute()
                )

        except Exception as e:

            st.warning(
                "Order was saved, but some "
                "order items could not be saved."
            )

            st.error(str(e))


        # ----------------------------------------------------
        # SEND DIRECT GMAIL
        # ----------------------------------------------------

        email_sent, email_error = (
            send_order_email(

                order_code=order_code,

                full_name=full_name.strip(),

                customer_email=customer_email.strip(),

                phone=phone.strip(),

                address=address.strip(),

                country=country.strip(),

                state=state.strip(),

                payment_method=payment_method,

                total=total,

                cart_items=items,

                proof_bytes=proof_bytes,

                proof_name=proof_name,

                proof_type=proof_type
            )
        )


        # ----------------------------------------------------
        # SAVE CONFIRMATION DATA
        # ----------------------------------------------------

        st.session_state.order_confirmation = {

            "order_code": order_code,

            "total": total,

            "status": order_status,

            "email_sent": email_sent,

            "email_error": email_error
        }


        # Empty cart
        st.session_state.cart = {}


        # Go to confirmation page
        st.session_state.page = (
            "Order Confirmation"
        )

        st.rerun()


# ============================================================
# ORDER CONFIRMATION PAGE
# ============================================================

elif st.session_state.page == "Order Confirmation":

    confirmation = (
        st.session_state.order_confirmation
    )

    if not confirmation:

        st.session_state.page = "Store"
        st.rerun()


    st.markdown(
        """
        <div style="text-align:center;">
            <h1>🎉 Order Received!</h1>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="order-box">',
        unsafe_allow_html=True
    )


    st.markdown(
        f"## Order ID: `{confirmation['order_code']}`"
    )

    st.markdown(
        f"### Total: "
        f"{money(confirmation['total'])}"
    )

    st.markdown(
        "### Status: Payment Under Review"
    )


    st.info(
        "Your payment proof has been submitted "
        "for review. Payment is NOT considered "
        "confirmed until the owner verifies it."
    )


    # --------------------------------------------------------
    # EMAIL STATUS
    # --------------------------------------------------------

    if confirmation["email_sent"]:

        st.success(
            "Order information and payment proof "
            "were sent to the store owner."
        )

    else:

        st.warning(
            "The order was saved in Supabase, "
            "but the owner email could not be sent."
        )

        if confirmation["email_error"]:

            st.error(
                f"Email error: "
                f"{confirmation['email_error']}"
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    st.write("")


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "🏪 Continue Shopping",
            key="confirmation_store"
        ):

            st.session_state.page = "Store"

            st.session_state.order_confirmation = None

            st.rerun()


    with col2:

        if st.button(
            "🚪 Logout",
            key="confirmation_logout"
        ):

            logout()