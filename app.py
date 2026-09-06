import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
from urllib.parse import quote
from supabase import create_client, Client


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SECRETS / SETTINGS
# ============================================================

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

SMTP_EMAIL = st.secrets.get(
    "SMTP_EMAIL",
    "quantumindustries258@gmail.com"
)

SMTP_APP_PASSWORD = st.secrets.get(
    "SMTP_APP_PASSWORD",
    ""
)

STORE_EMAIL = SMTP_EMAIL


# ============================================================
# EDITABLE PAYMENT SETTINGS
# ============================================================

PAYMENT_SETTINGS = {
    "bank_name": "Opay",
    "account_number": "9032113433",
    "account_name": "Deborah Oluchukwu Phillips",

    "gift_card_instructions": (
        "After purchasing your gift card, take a clear photo "
        "of the gift card and send the photo as an attachment "
        "to our store email."
    ),

    "gift_card_extra_instructions": (
        "Make sure the gift card details are clearly visible "
        "in the photo."
    ),
}


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #07111f;
        color: #f8fafc;
    }

    [data-testid="stSidebar"] {
        background: #0b1728;
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    p, label, span, div {
        color: inherit;
    }

    .store-card {
        background: #0d1b2f;
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.20);
    }

    .product-title {
        font-size: 21px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 10px;
    }

    .product-description {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.5;
        margin: 8px 0;
    }

    .price {
        color: #60a5fa;
        font-size: 22px;
        font-weight: 800;
        margin: 8px 0;
    }

    .order-box {
        background: #0d1b2f;
        border: 1px solid #2563eb;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }

    .payment-box {
        background: #101f35;
        border: 1px solid #334e68;
        border-radius: 14px;
        padding: 18px;
        margin: 12px 0;
    }

    .success-box {
        background: #09251b;
        border: 1px solid #16a34a;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }

    .warning-box {
        background: #2a2109;
        border: 1px solid #ca8a04;
        border-radius: 15px;
        padding: 18px;
        margin: 15px 0;
    }

    .muted {
        color: #94a3b8 !important;
    }

    .small-text {
        font-size: 13px;
        color: #94a3b8 !important;
    }

    .big-total {
        font-size: 28px;
        font-weight: 900;
        color: #60a5fa;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px;
        font-weight: 800;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SUPABASE
# ============================================================

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "Supabase settings are missing. "
        "Please add SUPABASE_URL and SUPABASE_KEY "
        "to Streamlit secrets."
    )
    st.stop()


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
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
    st.session_state.cart = []

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "last_order" not in st.session_state:
    st.session_state.last_order = None


# ============================================================
# EMAIL CONFIRMATION CALLBACK
# ============================================================

query_params = st.query_params

if "code" in query_params:
    code = query_params.get("code")

    if code:
        try:
            response = supabase.auth.exchange_code_for_session(code)

            if response and response.session:
                st.session_state.access_token = (
                    response.session.access_token
                )

                st.session_state.refresh_token = (
                    response.session.refresh_token
                )

                st.session_state.user = response.user

                st.query_params.clear()

                st.success(
                    "Email confirmed successfully! "
                    "You are now logged in."
                )

                st.rerun()

        except Exception:
            pass


# ============================================================
# AUTH HELPERS
# ============================================================

def restore_session():
    """
    Try to restore the existing Supabase session.
    """

    if (
        st.session_state.access_token
        and st.session_state.refresh_token
        and st.session_state.user
    ):
        return True

    return False


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.cart = []
    st.session_state.last_order = None
    st.session_state.page = "Store"

    st.rerun()


# ============================================================
# MONEY
# ============================================================

def money(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

SAMPLE_PRODUCTS = [
    {
        "id": "sample-001",
        "name": "Quantum Wireless Headphones",
        "description": (
            "Premium wireless headphones with "
            "comfortable ear cushions and clear sound."
        ),
        "price": 49.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1505740420928-5e560c06d30e"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-002",
        "name": "Smart Watch Pro",
        "description": (
            "Modern smartwatch with a bright display "
            "and useful everyday features."
        ),
        "price": 79.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1523275335684-37898b6baf30"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-003",
        "name": "Portable Bluetooth Speaker",
        "description": (
            "Compact wireless speaker designed for "
            "music at home or on the go."
        ),
        "price": 34.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1608043152269-423dbba4e7e1"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-004",
        "name": "USB-C Fast Charger",
        "description": (
            "Fast and convenient USB-C charging "
            "for compatible devices."
        ),
        "price": 24.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1583863788434-e58a36330cf0"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-005",
        "name": "Wireless Gaming Mouse",
        "description": (
            "Responsive wireless mouse designed "
            "for gaming and everyday computer use."
        ),
        "price": 39.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1527814050087-3793815479db"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-006",
        "name": "Laptop Backpack",
        "description": (
            "Durable backpack with space for a laptop, "
            "charger and everyday accessories."
        ),
        "price": 44.99,
        "image": (
            "https://images.unsplash.com/"
            "photo-1553062407-98eeb64c6a62"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
]


# ============================================================
# LOAD PRODUCTS
# ============================================================

@st.cache_data(ttl=60)
def load_products():
    try:
        response = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        rows = response.data or []

        if not rows:
            return SAMPLE_PRODUCTS

        products = []

        for row in rows:
            products.append(
                {
                    "id": row.get("id"),
                    "name": row.get("name", "Unnamed Product"),
                    "description": row.get(
                        "description",
                        ""
                    ),
                    "price": float(
                        row.get("price", 0)
                    ),
                    "image": row.get(
                        "image",
                        ""
                    ),
                }
            )

        return products

    except Exception:
        return SAMPLE_PRODUCTS


products = load_products()


# ============================================================
# PRODUCT LOOKUP
# ============================================================

def find_product(product_id):
    for product in products:
        if str(product["id"]) == str(product_id):
            return product

    return None


# ============================================================
# CART HELPERS
# ============================================================

def add_to_cart(product_id):
    product = find_product(product_id)

    if not product:
        return

    for item in st.session_state.cart:
        if str(item["id"]) == str(product_id):
            item["quantity"] += 1
            return

    st.session_state.cart.append(
        {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": float(product["price"]),
            "image": product["image"],
            "quantity": 1,
        }
    )


def remove_from_cart(product_id):
    for item in st.session_state.cart:
        if str(item["id"]) == str(product_id):
            item["quantity"] -= 1

            if item["quantity"] <= 0:
                st.session_state.cart.remove(item)

            return


def delete_from_cart(product_id):
    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if str(item["id"]) != str(product_id)
    ]


def cart_subtotal():
    total = 0

    for item in st.session_state.cart:
        total += (
            float(item["price"])
            * int(item["quantity"])
        )

    return total


def cart_count():
    total = 0

    for item in st.session_state.cart:
        total += int(item["quantity"])

    return total


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
    cart_items
):
    message = EmailMessage()

    message["Subject"] = (
        f"NEW ORDER - {order_code}"
    )

    message["From"] = SMTP_EMAIL
    message["To"] = STORE_EMAIL

    if customer_email:
        message["Reply-To"] = customer_email


    # --------------------------------------------------------
    # THIS IS WHERE PRODUCT NAMES ARE INCLUDED
    # --------------------------------------------------------

    items_text = ""

    for item in cart_items:

        line_total = (
            float(item["price"])
            * int(item["quantity"])
        )

        items_text += (
            f"Product Name: {item['name']}\n"
            f"Quantity: {item['quantity']}\n"
            f"Unit Price: {money(item['price'])}\n"
            f"Product Total: {money(line_total)}\n"
            f"{'-' * 40}\n"
        )


    body = f"""
NEW ORDER RECEIVED
==================

Order Number:
{order_code}


CUSTOMER
--------

Name:
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


ORDER ITEMS
-----------

{items_text}


PAYMENT
-------

Payment Method:
{payment_method}

Total:
{money(total)}


PAYMENT PROOF
-------------

The customer will send payment proof
directly by email.

Payment has NOT been verified.


Store Email:
{STORE_EMAIL}
"""

    message.set_content(body)

    try:

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=30
        ) as smtp:

            smtp.login(
                SMTP_EMAIL,
                SMTP_APP_PASSWORD
            )

            smtp.send_message(message)

        return True, None

    except Exception as e:

        return False, str(e)# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def authentication_page():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:20px 0 10px 0;
        ">
            <h1>🛍️ Quantum Store</h1>
            <p style="color:#94a3b8;">
                Create an account or log in to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )


    # ========================================================
    # LOGIN
    # ========================================================

    with tab1:

        st.subheader("Login")

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
            use_container_width=True
        ):

            if not login_email.strip():
                st.error("Please enter your email.")
                st.stop()

            if not login_password:
                st.error("Please enter your password.")
                st.stop()

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": login_email.strip(),
                        "password": login_password,
                    }
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

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error(
                        "Login failed. Please check your details."
                    )

            except Exception as e:

                error_text = str(e)

                if (
                    "Email not confirmed" in error_text
                    or "email_not_confirmed" in error_text.lower()
                ):

                    st.warning(
                        "Your email has not been confirmed yet. "
                        "Please check your email and press the "
                        "confirmation link."
                    )

                else:

                    st.error(
                        "Login failed. "
                        "Please check your email and password."
                    )


    # ========================================================
    # SIGNUP
    # ========================================================

    with tab2:

        st.subheader("Create Account")

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
            use_container_width=True
        ):

            if not signup_email.strip():
                st.error("Please enter your email.")
                st.stop()

            if not signup_password:
                st.error("Please enter a password.")
                st.stop()

            if signup_password != signup_confirm:
                st.error(
                    "The passwords do not match."
                )
                st.stop()

            if len(signup_password) < 6:
                st.error(
                    "Password must be at least 6 characters."
                )
                st.stop()

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": signup_email.strip(),
                        "password": signup_password,
                    }
                )

                if response.user:

                    st.success(
                        "Account created successfully!"
                    )

                    st.info(
                        "Check your email and press the "
                        "confirmation link before logging in."
                    )

                else:

                    st.error(
                        "Could not create your account."
                    )

            except Exception as e:

                st.error(
                    f"Could not create account: {e}"
                )


# ============================================================
# SHOW AUTH PAGE IF NOT LOGGED IN
# ============================================================

if not st.session_state.user:

    authentication_page()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🛍️ Quantum Store"
    )

    st.divider()

    user_email = getattr(
        st.session_state.user,
        "email",
        ""
    )

    st.write(
        f"👤 {user_email}"
    )

    st.divider()

    if st.button(
        "🛒 Store",
        use_container_width=True
    ):
        st.session_state.page = "Store"
        st.rerun()

    if st.button(
        f"🛍️ Cart ({cart_count()})",
        use_container_width=True
    ):
        st.session_state.page = "Cart"
        st.rerun()

    if st.button(
        "💳 Checkout",
        use_container_width=True
    ):
        st.session_state.page = "Checkout"
        st.rerun()

    if st.session_state.last_order:

        if st.button(
            "📦 Last Order",
            use_container_width=True
        ):
            st.session_state.page = "Confirmation"
            st.rerun()

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()


# ============================================================
# STORE PAGE
# ============================================================

if st.session_state.page == "Store":

    st.title("🛍️ Quantum Store")

    st.write(
        "Browse our products and add anything you like "
        "to your shopping cart."
    )

    st.divider()

    if not products:

        st.warning(
            "No products are currently available."
        )

    else:

        columns = st.columns(3)

        for index, product in enumerate(products):

            with columns[index % 3]:

                st.markdown(
                    '<div class="store-card">',
                    unsafe_allow_html=True
                )

                # Use Streamlit image rendering so HTML
                # does not appear as text.

                if product.get("image"):

                    try:

                        st.image(
                            product["image"],
                            use_container_width=True
                        )

                    except Exception:
                        st.info(
                            "Product image unavailable."
                        )

                st.markdown(
                    f"""
                    <div class="product-title">
                        {product["name"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="product-description">
                        {product["description"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="price">
                        {money(product["price"])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "🛒 Add to Cart",
                    key=f"add_{product['id']}",
                    use_container_width=True
                ):

                    add_to_cart(product["id"])

                    st.success(
                        "Added to cart!"
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# ============================================================
# CART PAGE
# ============================================================

elif st.session_state.page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "Continue Shopping",
            use_container_width=True
        ):

            st.session_state.page = "Store"
            st.rerun()

    else:

        for item in st.session_state.cart:

            st.markdown(
                '<div class="store-card">',
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(
                [1.5, 2.5, 2]
            )

            with col1:

                if item.get("image"):

                    try:

                        st.image(
                            item["image"],
                            use_container_width=True
                        )

                    except Exception:
                        pass

            with col2:

                st.markdown(
                    f"### {item['name']}"
                )

                st.write(
                    item["description"]
                )

                st.write(
                    f"Unit price: "
                    f"**{money(item['price'])}**"
                )

            with col3:

                st.write(
                    f"Quantity: **{item['quantity']}**"
                )

                plus = st.button(
                    "➕",
                    key=f"plus_{item['id']}"
                )

                minus = st.button(
                    "➖",
                    key=f"minus_{item['id']}"
                )

                if plus:

                    add_to_cart(item["id"])
                    st.rerun()

                if minus:

                    remove_from_cart(item["id"])
                    st.rerun()

                if st.button(
                    "🗑️ Remove",
                    key=f"delete_{item['id']}",
                    use_container_width=True
                ):

                    delete_from_cart(item["id"])
                    st.rerun()

                item_total = (
                    float(item["price"])
                    * int(item["quantity"])
                )

                st.write(
                    f"Product total: "
                    f"**{money(item_total)}**"
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # CART SUMMARY
        # ----------------------------------------------------

        st.divider()

        subtotal = cart_subtotal()

        st.markdown(
            f"""
            <div class="order-box">
                <h3>Cart Summary</h3>
                <p>
                    Items:
                    <strong>{cart_count()}</strong>
                </p>
                <p class="big-total">
                    Total: {money(subtotal)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2)

        with col_a:

            if st.button(
                "← Continue Shopping",
                use_container_width=True
            ):

                st.session_state.page = "Store"
                st.rerun()

        with col_b:

            if st.button(
                "Proceed to Checkout →",
                use_container_width=True
            ):

                st.session_state.page = "Checkout"
                st.rerun()# ============================================================
# CHECKOUT PAGE
# ============================================================

elif st.session_state.page == "Checkout":

    st.title("💳 Checkout")

    if not st.session_state.cart:

        st.warning(
            "Your cart is empty. Add a product before checking out."
        )

        if st.button(
            "Go to Store",
            use_container_width=True
        ):

            st.session_state.page = "Store"
            st.rerun()

        st.stop()


    # ========================================================
    # ORDER SUMMARY
    # ========================================================

    st.subheader("Order Summary")

    for item in st.session_state.cart:

        item_total = (
            float(item["price"])
            * int(item["quantity"])
        )

        st.write(
            f"**{item['name']}** × "
            f"{item['quantity']} — "
            f"{money(item_total)}"
        )

    total = cart_subtotal()

    st.markdown(
        f"""
        <div class="order-box">
            <div class="big-total">
                Total: {money(total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CUSTOMER INFORMATION
    # ========================================================

    st.subheader("Customer Information")

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
        placeholder="Enter your complete delivery address"
    )

    country = st.text_input(
        "Country",
        placeholder="Nigeria"
    )

    state = st.text_input(
        "State",
        placeholder="Lagos"
    )

    customer_email = st.text_input(
        "Email",
        value=getattr(
            st.session_state.user,
            "email",
            ""
        )
    )


    # ========================================================
    # PAYMENT METHOD
    # ========================================================

    st.subheader("Payment Method")

    payment_method = st.selectbox(
        "Choose payment method",
        [
            "Bank Transfer",
            "Gift Card"
        ]
    )


    # ========================================================
    # BANK TRANSFER
    # ========================================================

    if payment_method == "Bank Transfer":

        st.markdown(
            """
            <div class="payment-box">
                <h3>🏦 Bank Transfer</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"**Bank:** "
            f"{PAYMENT_SETTINGS['bank_name']}"
        )

        st.write(
            f"**Account Number:** "
            f"{PAYMENT_SETTINGS['account_number']}"
        )

        st.write(
            f"**Account Name:** "
            f"{PAYMENT_SETTINGS['account_name']}"
        )

        st.info(
            "After making the transfer, place your order. "
            "On the confirmation page you will be able "
            "to send your payment proof directly to the "
            "store email."
        )


    # ========================================================
    # GIFT CARD
    # ========================================================

    elif payment_method == "Gift Card":

        st.markdown(
            """
            <div class="payment-box">
                <h3>🎁 Gift Card</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            PAYMENT_SETTINGS[
                "gift_card_instructions"
            ]
        )

        st.write(
            PAYMENT_SETTINGS[
                "gift_card_extra_instructions"
            ]
        )

        st.info(
            "After placing your order, use the "
            "'Send Gift Card Proof' button on the "
            "confirmation page to open your email app."
        )


    # ========================================================
    # PLACE ORDER
    # ========================================================

    st.divider()

    st.subheader("Place Order")

    st.warning(
        "Your order will be recorded as received. "
        "Payment will NOT be automatically verified."
    )

    if st.button(
        "✅ Confirm Order",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )
            st.stop()

        if not phone.strip():

            st.error(
                "Please enter your phone number."
            )
            st.stop()

        if not address.strip():

            st.error(
                "Please enter your delivery address."
            )
            st.stop()

        if not country.strip():

            st.error(
                "Please enter your country."
            )
            st.stop()

        if not state.strip():

            st.error(
                "Please enter your state."
            )
            st.stop()

        if not customer_email.strip():

            st.error(
                "Please enter your email."
            )
            st.stop()

        if not st.session_state.cart:

            st.error(
                "Your cart is empty."
            )
            st.stop()


        # ----------------------------------------------------
        # CREATE UNIQUE ORDER IDs
        # ----------------------------------------------------

        order_id = str(uuid.uuid4())

        order_code = (
            "ORD-"
            + uuid.uuid4().hex[:8].upper()
        )


        # ----------------------------------------------------
        # ORDER STATUS
        # ----------------------------------------------------

        order_status = "Received"


        # ----------------------------------------------------
        # DATABASE ORDER ROW
        #
        # IMPORTANT:
        # The database uses order_id, not id.
        # country/customer_email are intentionally not
        # inserted because the current orders table does
        # not contain those columns.
        # ----------------------------------------------------

        order_row = {

            "order_id": order_id,

            "user_id": str(
                st.session_state.user.id
            ),

            "full_name": full_name.strip(),

            "phone": phone.strip(),

            "address": address.strip(),

            "payment_method": payment_method,

            "total": float(total),

            "status": order_status,
        }


        # ----------------------------------------------------
        # INSERT ORDER
        # ----------------------------------------------------

        try:

            order_response = (
                supabase
                .table("orders")
                .insert(order_row)
                .execute()
            )

        except Exception as e:

            st.error(
                f"Could not create order: {e}"
            )

            st.stop()


        # ----------------------------------------------------
        # INSERT ORDER ITEMS
        #
        # PRODUCT NAME IS SAVED HERE TOO.
        # ----------------------------------------------------

        order_items = []

        for item in st.session_state.cart:

            order_items.append(
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
                    ),
                }
            )


        try:

            supabase \
                .table("order_items") \
                .insert(order_items) \
                .execute()

        except Exception as e:

            # The main order was created, but its items
            # could not be saved.

            st.error(
                "The order was created, but the "
                f"order items could not be saved: {e}"
            )

            st.stop()


        # ----------------------------------------------------
        # SEND OWNER EMAIL
        #
        # The email contains:
        # - Order number
        # - Customer details
        # - PRODUCT NAME
        # - Quantity
        # - Unit price
        # - Product total
        # - Payment method
        # - Grand total
        # ----------------------------------------------------

        email_sent, email_error = send_order_email(
            order_code=order_code,
            full_name=full_name.strip(),
            customer_email=customer_email.strip(),
            phone=phone.strip(),
            address=address.strip(),
            country=country.strip(),
            state=state.strip(),
            payment_method=payment_method,
            total=total,
            cart_items=st.session_state.cart,
        )


        # ----------------------------------------------------
        # SAVE ORDER INFORMATION TO SESSION
        # ----------------------------------------------------

        st.session_state.last_order = {

            "order_id": order_id,

            "order_code": order_code,

            "full_name": full_name.strip(),

            "email": customer_email.strip(),

            "phone": phone.strip(),

            "address": address.strip(),

            "country": country.strip(),

            "state": state.strip(),

            "payment_method": payment_method,

            "total": float(total),

            "status": order_status,

            "items": [
                {
                    "name": item["name"],
                    "quantity": int(
                        item["quantity"]
                    ),
                    "price": float(
                        item["price"]
                    ),
                }
                for item in st.session_state.cart
            ],
        }


        # ----------------------------------------------------
        # CLEAR CART
        # ----------------------------------------------------

        st.session_state.cart = []

        st.session_state.page = "Confirmation"


        # ----------------------------------------------------
        # EMAIL RESULT
        # ----------------------------------------------------

        if email_sent:

            st.success(
                "Order placed successfully!"
            )

        else:

            st.warning(
                "Your order was saved, but the store "
                "notification email could not be sent."
            )

            if email_error:

                st.caption(
                    f"Email error: {email_error}"
                )

        st.rerun()


# ============================================================
# CONFIRMATION PAGE
# ============================================================

elif st.session_state.page == "Confirmation":

    st.title("✅ Order Confirmed")

    order = st.session_state.last_order

    if not order:

        st.info(
            "There is no recent order to display."
        )

        if st.button(
            "Go to Store",
            use_container_width=True
        ):

            st.session_state.page = "Store"
            st.rerun()

        st.stop()


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    st.markdown(
        f"""
        <div class="success-box">
            <h2>🎉 Thank you for your order!</h2>
            <p>
                Your order has been received.
            </p>
            <p>
                <strong>Order Number:</strong>
                {order["order_code"]}
            </p>
            <p>
                <strong>Status:</strong>
                {order["status"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CUSTOMER DETAILS
    # ========================================================

    st.subheader("Customer Details")

    st.write(
        f"**Name:** {order['full_name']}"
    )

    st.write(
        f"**Email:** {order['email']}"
    )

    st.write(
        f"**Phone:** {order['phone']}"
    )

    st.write(
        f"**Address:** {order['address']}"
    )

    st.write(
        f"**Country:** {order['country']}"
    )

    st.write(
        f"**State:** {order['state']}"
    )


    # ========================================================
    # ORDERED PRODUCTS
    # ========================================================

    st.subheader("📦 Products Ordered")

    for item in order["items"]:

        item_total = (
            float(item["price"])
            * int(item["quantity"])
        )

        st.markdown(
            f"""
            <div class="order-box">

            <h3>{item["name"]}</h3>

            <p>
                Quantity:
                <strong>{item["quantity"]}</strong>
            </p>

            <p>
                Unit Price:
                <strong>{money(item["price"])}</strong>
            </p>

            <p>
                Product Total:
                <strong>{money(item_total)}</strong>
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # TOTAL
    # ========================================================

    st.markdown(
        f"""
        <div class="order-box">
            <p>
                Payment Method:
                <strong>{order["payment_method"]}</strong>
            </p>

            <p class="big-total">
                Order Total:
                {money(order["total"])}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )    # ========================================================
    # PAYMENT PROOF INSTRUCTIONS
    # ========================================================

    st.subheader("📎 Send Payment Proof")

    if order["payment_method"] == "Bank Transfer":

        st.markdown(
            """
            <div class="payment-box">

            <h3>🏦 Bank Transfer Proof</h3>

            <p>
            After making your bank transfer, take a
            screenshot or photo of your payment receipt.
            </p>

            <p>
            Then tap the button below to open your email
            app and attach the payment proof.
            </p>

            <p>
            <strong>
            Payment is not considered verified until
            the store checks it.
            </strong>
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        email_subject = quote(
            f"Payment Proof - {order['order_code']}"
        )

        email_body = quote(
            f"""Hello Quantum Store,

I am sending the payment proof for my order.

Order Number: {order['order_code']}

Name: {order['full_name']}

Email: {order['email']}

Payment Method: Bank Transfer

Order Total: {money(order['total'])}

I have attached my payment receipt.

Thank you."""
        )

        mailto_link = (
            f"mailto:{STORE_EMAIL}"
            f"?subject={email_subject}"
            f"&body={email_body}"
        )

        st.markdown(
            f"""
            <a href="{mailto_link}"
               target="_blank"
               style="
               display:block;
               text-align:center;
               background:#2563eb;
               color:white;
               padding:15px;
               border-radius:10px;
               text-decoration:none;
               font-weight:700;
               font-size:17px;
               margin-top:10px;
               ">
               📎 Send Bank Transfer Proof
            </a>
            """,
            unsafe_allow_html=True
        )


    elif order["payment_method"] == "Gift Card":

        st.markdown(
            """
            <div class="payment-box">

            <h3>🎁 Gift Card Proof</h3>

            <p>
            Take a clear photo of the gift card.
            </p>

            <p>
            Make sure the relevant gift card details
            can be clearly seen.
            </p>

            <p>
            Tap the button below to open your email app
            and attach the photo.
            </p>

            <p>
            <strong>
            Payment is not considered verified until
            the store checks it.
            </strong>
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        email_subject = quote(
            f"Gift Card Proof - {order['order_code']}"
        )

        email_body = quote(
            f"""Hello Quantum Store,

I am sending the gift card proof for my order.

Order Number: {order['order_code']}

Name: {order['full_name']}

Email: {order['email']}

Payment Method: Gift Card

Order Total: {money(order['total'])}

I have attached a clear photo of my gift card.

Thank you."""
        )

        mailto_link = (
            f"mailto:{STORE_EMAIL}"
            f"?subject={email_subject}"
            f"&body={email_body}"
        )

        st.markdown(
            f"""
            <a href="{mailto_link}"
               target="_blank"
               style="
               display:block;
               text-align:center;
               background:#2563eb;
               color:white;
               padding:15px;
               border-radius:10px;
               text-decoration:none;
               font-weight:700;
               font-size:17px;
               margin-top:10px;
               ">
               📎 Send Gift Card Proof
            </a>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # IMPORTANT PAYMENT NOTICE
    # ========================================================

    st.markdown(
        """
        <div class="warning-box">

        <strong>⚠️ Important</strong>

        <p>
        Sending a payment screenshot, receipt, or gift-card
        photo does not automatically mean that payment has
        been verified.
        </p>

        <p>
        The store should check the payment before changing
        the order status to Payment Confirmed.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # ORDER STATUS
    # ========================================================

    st.subheader("Order Status")

    st.write(
        f"**Current status:** {order['status']}"
    )

    st.caption(
        "Typical order statuses: Received → "
        "Payment Under Review → Payment Confirmed → "
        "Processing → Completed"
    )


    # ========================================================
    # BUTTONS
    # ========================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🛍️ Continue Shopping",
            use_container_width=True
        ):

            st.session_state.page = "Store"
            st.rerun()

    with col2:

        if st.button(
            "🛒 View Cart",
            use_container_width=True
        ):

            st.session_state.page = "Cart"
            st.rerun()


# ============================================================
# FALLBACK
# ============================================================

else:

    st.session_state.page = "Store"
    st.rerun()