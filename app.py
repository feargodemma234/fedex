import streamlit as st
from supabase import create_client, Client
import requests
import uuid
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CONFIG
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
FORMSPREE_ENDPOINT = st.secrets.get("FORMSPREE_ENDPOINT", "")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# SAMPLE PRODUCTS
# These appear even when the Supabase products table is empty.
# ============================================================

SAMPLE_PRODUCTS = [
    {
        "id": "sample-001",
        "name": "Wireless Headphones",
        "description": "Comfortable wireless headphones with clear sound and a modern design.",
        "price": 49.99,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    },
    {
        "id": "sample-002",
        "name": "Mechanical Keyboard",
        "description": "Responsive mechanical keyboard suitable for gaming, school and work.",
        "price": 69.99,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3"
    },
    {
        "id": "sample-003",
        "name": "Smart Watch",
        "description": "Modern smartwatch with notifications, fitness features and a bright display.",
        "price": 89.99,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"
    },
    {
        "id": "sample-004",
        "name": "USB-C Hub",
        "description": "Compact USB-C hub with multiple ports for everyday devices.",
        "price": 34.99,
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761"
    },
    {
        "id": "sample-005",
        "name": "Bluetooth Speaker",
        "description": "Portable Bluetooth speaker designed for music at home or on the go.",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1"
    },
    {
        "id": "sample-006",
        "name": "Laptop Stand",
        "description": "Adjustable laptop stand for a cleaner and more comfortable workspace.",
        "price": 29.99,
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46"
    }
]

# ============================================================
# SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "user" not in st.session_state:
    st.session_state.user = None

if "order_submitting" not in st.session_state:
    st.session_state.order_submitting = False

if "last_order" not in st.session_state:
    st.session_state.last_order = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #777;
        margin-bottom: 25px;
    }

    .product-card {
        border: 1px solid #ddd;
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 15px;
    }

    .price {
        font-size: 22px;
        font-weight: 700;
    }

    .order-box {
        border: 1px solid #ddd;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .success-box {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #22aa66;
        background: #f1fff7;
    }

    @media (max-width: 700px) {
        .main-title {
            font-size: 28px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTH HELPERS
# ============================================================

def get_current_user():
    try:
        response = supabase.auth.get_user()

        if response and response.user:
            return response.user

    except Exception:
        pass

    return None


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.cart = {}
    st.session_state.page = "Store"
    st.session_state.last_order = None
    st.rerun()


# ============================================================
# LOAD USER
# ============================================================

if st.session_state.user is None:
    st.session_state.user = get_current_user()


# ============================================================
# ADMIN
# ============================================================

ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "")


def is_admin():
    if not st.session_state.user:
        return False

    if not ADMIN_EMAIL:
        return False

    return (
        st.session_state.user.email.lower().strip()
        == ADMIN_EMAIL.lower().strip()
    )


# ============================================================
# PRODUCT FUNCTIONS
# ============================================================

def get_products():
    products = []

    try:
        response = (
            supabase
            .table("products")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        if response.data:
            products = response.data

    except Exception:
        products = []

    # Sample products are always available.
    # Database products are added before them.
    database_ids = {str(p["id"]) for p in products}

    for sample in SAMPLE_PRODUCTS:
        if sample["id"] not in database_ids:
            products.append(sample)

    return products


def get_product_by_id(product_id):
    products = get_products()

    for product in products:
        if str(product["id"]) == str(product_id):
            return product

    return None


# ============================================================
# CART FUNCTIONS
# ============================================================

def add_to_cart(product_id):
    product_id = str(product_id)

    if product_id in st.session_state.cart:
        st.session_state.cart[product_id] += 1
    else:
        st.session_state.cart[product_id] = 1


def remove_from_cart(product_id):
    product_id = str(product_id)

    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]


def decrease_quantity(product_id):
    product_id = str(product_id)

    if product_id not in st.session_state.cart:
        return

    st.session_state.cart[product_id] -= 1

    if st.session_state.cart[product_id] <= 0:
        del st.session_state.cart[product_id]


def cart_items():
    items = []

    for product_id, quantity in st.session_state.cart.items():

        product = get_product_by_id(product_id)

        if product:
            item = {
                "id": str(product["id"]),
                "name": product["name"],
                "description": product.get("description", ""),
                "price": float(product["price"]),
                "image_url": product.get("image_url"),
                "quantity": quantity,
                "subtotal": float(product["price"]) * quantity
            }

            items.append(item)

    return items


def cart_total():
    return sum(
        item["subtotal"]
        for item in cart_items()
    )


def cart_count():
    return sum(
        st.session_state.cart.values()
    )


# ============================================================
# STORE SETTINGS
# ============================================================

def get_store_settings():

    try:
        response = (
            supabase
            .table("store_settings")
            .select("*")
            .eq("id", 1)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:
        pass

    return {
        "bank_name": "",
        "account_name": "",
        "account_number": "",
        "bank_instructions": "",
        "gift_card_instructions": ""
    }


# ============================================================
# NAVIGATION
# ============================================================

def navigation():

    user = st.session_state.user

    cols = st.columns(5)

    with cols[0]:
        if st.button("🏠 Store", use_container_width=True):
            st.session_state.page = "Store"
            st.rerun()

    with cols[1]:
        if st.button(
            f"🛒 Cart ({cart_count()})",
            use_container_width=True
        ):
            st.session_state.page = "Cart"
            st.rerun()

    with cols[2]:
        if user:
            if st.button("📦 My Orders", use_container_width=True):
                st.session_state.page = "Orders"
                st.rerun()

    with cols[3]:
        if user and is_admin():
            if st.button("⚙️ Admin", use_container_width=True):
                st.session_state.page = "Admin"
                st.rerun()

    with cols[4]:
        if user:
            if st.button("Logout", use_container_width=True):
                logout()
        else:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛍️ My Store</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Quality products. Simple shopping.</div>',
    unsafe_allow_html=True
)

navigation()

st.divider()


# ============================================================
# AUTH PAGE
# ============================================================

def auth_page():

    st.header("🔐 Account")

    tab1, tab2 = st.tabs([
        "Login",
        "Create Account"
    ])

    # ---------------- LOGIN ----------------

    with tab1:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:
                st.error("Please enter your email and password.")
                return

            try:

                response = supabase.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password
                })

                if response.user:

                    st.session_state.user = response.user
                    st.session_state.page = "Store"

                    st.success("Login successful!")

                    st.rerun()

            except Exception as e:

                error_text = str(e).lower()

                if "email not confirmed" in error_text:
                    st.error(
                        "Please confirm your email before logging in."
                    )
                else:
                    st.error(
                        "Login failed. Check your email and password."
                    )

    # ---------------- SIGNUP ----------------

    with tab2:

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
            type="primary",
            use_container_width=True
        ):

            if not signup_email:
                st.error("Enter your email.")
                return

            if not signup_password:
                st.error("Enter a password.")
                return

            if signup_password != signup_confirm:
                st.error("Passwords do not match.")
                return

            if len(signup_password) < 6:
                st.error(
                    "Password must be at least 6 characters."
                )
                return

            try:

                response = supabase.auth.sign_up({
                    "email": signup_email.strip(),
                    "password": signup_password
                })

                st.success(
                    "Account created! Check your email and "
                    "click the confirmation link."
                )

                if response.user:
                    st.info(
                        "After confirming your email, return here "
                        "and log in."
                    )

            except Exception as e:
                st.error(f"Signup failed: {e}")


# ============================================================
# STORE PAGE
# ============================================================

def store_page():

    st.header("🛍️ Products")

    products = get_products()

    if not products:
        st.warning("No products available.")
        return

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search by product name..."
    )

    if search:
        search_lower = search.lower()

        products = [
            p for p in products
            if search_lower in p["name"].lower()
            or search_lower in p.get("description", "").lower()
        ]

    if not products:
        st.info("No products matched your search.")
        return

    columns = st.columns(3)

    for index, product in enumerate(products):

        with columns[index % 3]:

            st.markdown(
                '<div class="product-card">',
                unsafe_allow_html=True
            )

            image_url = product.get("image_url")

            if image_url:
                st.image(
                    image_url,
                    use_container_width=True
                )

            st.subheader(product["name"])

            st.write(
                product.get("description", "")
            )

            st.markdown(
                f'<div class="price">${float(product["price"]):,.2f}</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "🛒 Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):

                add_to_cart(product["id"])

                st.success(
                    f"{product['name']} added to cart."
                )

                st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# CART PAGE
# ============================================================

def cart_page():

    st.header("🛒 Your Cart")

    items = cart_items()

    if not items:
        st.info("Your cart is empty.")

        if st.button("Continue Shopping"):
            st.session_state.page = "Store"
            st.rerun()

        return

    for item in items:

        col1, col2, col3, col4, col5 = st.columns(
            [1, 3, 1, 1, 1]
        )

        with col1:
            if item["image_url"]:
                st.image(
                    item["image_url"],
                    width=80
                )

        with col2:
            st.write(f"**{item['name']}**")
            st.write(
                f"${item['price']:,.2f} each"
            )

        with col3:
            if st.button(
                "➖",
                key=f"minus_{item['id']}"
            ):
                decrease_quantity(item["id"])
                st.rerun()

        with col4:
            st.write(
                f"**{item['quantity']}**"
            )

        with col5:
            if st.button(
                "➕",
                key=f"plus_{item['id']}"
            ):
                add_to_cart(item["id"])
                st.rerun()

        if st.button(
            "Remove",
            key=f"remove_{item['id']}"
        ):
            remove_from_cart(item["id"])
            st.rerun()

        st.divider()

    total = cart_total()

    st.subheader(
        f"Total: ${total:,.2f}"
    )

    if not st.session_state.user:
        st.warning(
            "Please log in before checking out."
        )

        if st.button("Login"):
            st.session_state.page = "Login"
            st.rerun()

        return

    if st.button(
        "Proceed to Checkout →",
        type="primary",
        use_container_width=True
    ):
        st.session_state.page = "Checkout"
        st.rerun()


# ============================================================
# CHECKOUT PAGE
# ============================================================

def checkout_page():

    if not st.session_state.user:
        st.warning("Please login first.")
        st.session_state.page = "Login"
        st.rerun()

    items = cart_items()

    if not items:
        st.warning("Your cart is empty.")
        st.session_state.page = "Store"
        st.rerun()

    st.header("💳 Checkout")

    st.subheader("Customer Information")

    full_name = st.text_input(
        "Full Name"
    )

    phone = st.text_input(
        "Phone Number"
    )

    address = st.text_area(
        "Delivery Address"
    )

    country = st.text_input(
        "Country",
        value="Nigeria"
    )

    state = st.text_input(
        "State"
    )

    contact_email = st.text_input(
        "Contact Email (optional)",
        value=st.session_state.user.email or ""
    )

    st.subheader("Payment")

    payment_method = st.radio(
        "Choose payment method",
        [
            "Bank Transfer",
            "Gift Card"
        ]
    )

    settings = get_store_settings()

    if payment_method == "Bank Transfer":

        st.info(
            f"""
Bank: {settings.get('bank_name', '')}

Account Name: {settings.get('account_name', '')}

Account Number: {settings.get('account_number', '')}

{settings.get('bank_instructions', '')}
"""
        )

    else:

        st.info(
            settings.get(
                "gift_card_instructions",
                ""
            )
        )

    proof = st.file_uploader(
        "Upload Payment Proof",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]
    )

    if proof:
        st.image(
            proof,
            caption="Payment proof preview",
            use_container_width=True
        )

    st.subheader("Order Summary")

    for item in items:
        st.write(
            f"{item['name']} × {item['quantity']} "
            f"— ${item['subtotal']:,.2f}"
        )

    total = cart_total()

    st.markdown(
        f"### Total: ${total:,.2f}"
    )

    if st.session_state.order_submitting:
        st.warning("Submitting order...")
        return

    if st.button(
        "✅ Confirm Order",
        type="primary",
        use_container_width=True
    ):

        if not full_name.strip():
            st.error("Enter your full name.")
            return

        if not phone.strip():
            st.error("Enter your phone number.")
            return

        if not address.strip():
            st.error("Enter your delivery address.