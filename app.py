import os
import re
import uuid
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import requests
import streamlit as st
from supabase import create_client, Client


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NovaShop",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #f7f8fc;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .product-card {
        background: white;
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        border: 1px solid #eeeeee;
    }

    .product-name {
        font-size: 20px;
        font-weight: 700;
        margin-top: 8px;
    }

    .product-description {
        color: #6b7280;
        min-height: 50px;
    }

    .price {
        font-size: 22px;
        font-weight: 800;
        margin: 8px 0;
    }

    .cart-total {
        font-size: 28px;
        font-weight: 800;
    }

    .order-success {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        padding: 25px;
        border-radius: 15px;
    }

    .warning-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        padding: 18px;
        border-radius: 12px;
    }

    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 18px;
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .main-title {
            font-size: 30px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONFIGURATION
# ============================================================

def get_secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_ANON_KEY = get_secret("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = get_secret("SUPABASE_SERVICE_ROLE_KEY")
FORMSPREE_ENDPOINT = get_secret("FORMSPREE_ENDPOINT")

APP_URL = get_secret(
    "APP_URL",
    "http://localhost:8501"
).rstrip("/")

ADMIN_EMAIL = get_secret("ADMIN_EMAIL", "").strip().lower()

PAYMENT_PROOF_BUCKET = get_secret(
    "PAYMENT_PROOF_BUCKET",
    "payment-proofs"
)

PRODUCT_IMAGE_BUCKET = get_secret(
    "PRODUCT_IMAGE_BUCKET",
    "product-images"
)


# ============================================================
# SUPABASE CLIENTS
# ============================================================

@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY are missing."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY
    )


@st.cache_resource
def get_admin_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is missing."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY
    )


try:
    supabase = get_supabase_client()
except Exception as exc:
    st.error(f"Supabase configuration error: {exc}")
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():
    defaults = {
        "page": "store",
        "cart": {},
        "checkout_data": {},
        "payment_method": None,
        "payment_proof_path": None,
        "last_order": None,
        "signup_success": False,
        "login_message": None,
        "order_submitting": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

SAMPLE_PRODUCTS = [
    {
        "id": "sample-headphones",
        "name": "Wireless Headphones",
        "description": "Comfortable wireless headphones with clear sound and long battery life.",
        "price": 49.99,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-keyboard",
        "name": "Mechanical Keyboard",
        "description": "Compact mechanical keyboard suitable for work, gaming and everyday typing.",
        "price": 69.99,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-mouse",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse designed for comfortable daily use.",
        "price": 29.99,
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-backpack",
        "name": "Travel Backpack",
        "description": "Durable everyday backpack with compartments for your laptop and accessories.",
        "price": 54.99,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-watch",
        "name": "Smart Watch",
        "description": "Modern smartwatch with notifications, activity tracking and a bright display.",
        "price": 89.99,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sample-speaker",
        "name": "Bluetooth Speaker",
        "description": "Portable Bluetooth speaker with powerful audio for home or travel.",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
    },
]


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

    st.session_state.cart = {}
    st.session_state.checkout_data = {}
    st.session_state.payment_method = None
    st.session_state.payment_proof_path = None
    st.session_state.last_order = None
    st.session_state.page = "store"

    st.rerun()


def is_admin(user):
    if not user:
        return False

    if not ADMIN_EMAIL:
        return False

    return (user.email or "").lower() == ADMIN_EMAIL


# ============================================================
# AUTH PAGES
# ============================================================

def signup_page():
    st.markdown(
        '<div class="main-title">Create your account</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Create an account to start shopping.</div>',
        unsafe_allow_html=True
    )

    with st.form("signup_form"):
        email = st.text_input(
            "Email",
            placeholder="you@example.com"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if submitted:

        if not email or not password or not confirm_password:
            st.error("Please complete all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        if len(password) < 6:
            st.error("Password must contain at least 6 characters.")
            return

        try:
            response = supabase.auth.sign_up(
                {
                    "email": email.strip(),
                    "password": password,
                    "options": {
                        "email_redirect_to": APP_URL
                    }
                }
            )

            if response.user:
                st.success(
                    "Account created. Check your email and press the confirmation link."
                )

                st.info(
                    "After confirming your email, return to the website and log in."
                )

        except Exception as exc:
            message = str(exc)

            if "already registered" in message.lower():
                st.error(
                    "An account with this email already exists."
                )
            else:
                st.error(
                    f"Could not create account: {message}"
                )

    st.divider()

    if st.button(
        "Already have an account? Log in",
        use_container_width=True
    ):
        st.session_state.page = "login"
        st.rerun()


def login_page():
    st.markdown(
        '<div class="main-title">Welcome back</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Log in to continue shopping.</div>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="you@example.com"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Log In",
            use_container_width=True
        )

    if submitted:

        if not email or not password:
            st.error("Enter your email and password.")
            return

        try:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email.strip(),
                    "password": password
                }
            )

            if response.user:
                st.session_state.page = "store"
                st.session_state.login_message = None
                st.rerun()

        except Exception as exc:
            message = str(exc)

            if (
                "email not confirmed" in message.lower()
                or "email_not_confirmed" in message.lower()
            ):
                st.error(
                    "Your email has not been confirmed. Check your email and press the confirmation link before logging in."
                )

            elif (
                "invalid login credentials" in message.lower()
                or "invalid_credentials" in message.lower()
            ):
                st.error(
                    "Invalid email or password."
                )

            else:
                st.error(
                    f"Login failed: {message}"
                )

    st.divider()

    if st.button(
        "Create a new account",
        use_container_width=True
    ):
        st.session_state.page = "signup"
        st.rerun()


# ============================================================
# PRODUCT HELPERS
# ============================================================

def get_products():
    try:
        response = (
            supabase
            .table("products")
            .select(
                "id,name,description,price,image_url,is_active"
            )
            .eq("is_active", True)
            .order("name")
            .execute()
        )

        database_products = response.data or []

        normalized = []

        for product in database_products:
            normalized.append(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "description": product.get("description", ""),
                    "price": float(product["price"]),
                    "image_url": product.get("image_url", ""),
                }
            )

        # Always show samples if database has no products.
        if not normalized:
            return SAMPLE_PRODUCTS

        # Samples remain available even if DB contains custom products.
        existing_ids = {
            str(product["id"])
            for product in normalized
        }

        for sample in SAMPLE_PRODUCTS:
            if sample["id"] not in existing_ids:
                normalized.append(sample)

        return normalized

    except Exception as exc:
        st.warning(
            f"Could not load database products. Showing sample products instead. "
            f"Database error: {exc}"
        )

        return SAMPLE_PRODUCTS


def get_product_by_id(product_id):
    products = get_products()

    for product in products:
        if str(product["id"]) == str(product_id):
            return product

    return None


# ============================================================
# CART
# ============================================================

def add_to_cart(product):
    product_id = str(product["id"])

    if product_id not in st.session_state.cart:
        st.session_state.cart[product_id] = 1
    else:
        st.session_state.cart[product_id] += 1

    st.toast(f"{product['name']} added to cart!")


def change_quantity(product_id, amount):
    if product_id not in st.session_state.cart:
        return

    new_quantity = (
        st.session_state.cart[product_id] + amount
    )

    if new_quantity <= 0:
        del st.session_state.cart[product_id]
    else:
        st.session_state.cart[product_id] = new_quantity


def remove_from_cart(product_id):
    st.session_state.cart.pop(
        product_id,
        None
    )


def cart_items():
    result = []

    for product_id, quantity in st.session_state.cart.items():
        product = get_product_by_id(product_id)

        if product:
            result.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "subtotal": product["price"] * quantity
                }
            )

    return result


def cart_total():
    return sum(
        item["subtotal"]
        for item in cart_items()
    )


# ============================================================
# STORE
# ============================================================

def store_page():
    user = get_current_user()

    st.markdown(
        '<div class="main-title">NovaShop 🛍️</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Modern products. Simple shopping.</div>',
        unsafe_allow_html=True
    )

    products = get_products()

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search..."
    )

    filtered_products = products

    if search:
        search_lower = search.lower()

        filtered_products = [
            product
            for product in products
            if (
                search_lower in product["name"].lower()
                or search_lower in product["description"].lower()
            )
        ]

    if not filtered_products:
        st.info("No products found.")
        return

    columns = st.columns(3)

    for index, product in enumerate(filtered_products):

        with columns[index % 3]:

            st.markdown(
                '<div class="product-card">',
                unsafe_allow_html=True
            )

            if product.get("image_url"):
                st.image(
                    product["image_url"],
                    use_container_width=True
                )

            st.markdown(
                f'<div class="product-name">{product["name"]}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="product-description">{product["description"]}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="price">${product["price"]:,.2f}</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):
                add_to_cart(product)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# ============================================================
# CART PAGE
# ============================================================

def cart_page():
    st.title("🛒 Your Cart")

    items = cart_items()

    if not items:
        st.info("Your cart is empty.")

        if st.button("Continue Shopping"):
            st.session_state.page = "store"
            st.rerun()

        return

    for item in items:

        product = item["product"]
        product_id = str(product["id"])

        col1, col2, col3, col4, col5 = st.columns(
            [2.5, 1, 1.2, 1.2, 0.8]
        )

        with col1:
            st.write(f"**{product['name']}**")

        with col2:
            st.write(
                f"${product['price']:,.2f}"
            )

        with col3:

            minus_col, quantity_col, plus_col = st.columns(3)

            with minus_col:
                if st.button(
                    "−",
                    key=f"minus_{product_id}"
                ):
                    change_quantity(product_id, -1)
                    st.rerun()

            with quantity_col:
                st.write(
                    item["quantity"],
                    unsafe_allow_html=True
                )

            with plus_col:
                if st.button(
                    "+",
                    key=f"plus_{product_id}"
                ):
                    change_quantity(product_id, 1)
                    st.rerun()

        with col4:
            st.write(
                f"${item['subtotal']:,.2f}"
            )

        with col5:
            if st.button(
                "🗑️",
                key=f"remove_{product_id}"
            ):
                remove_from_cart(product_id)
                st.rerun()

    st.divider()

    total = cart_total()

    st.markdown(
        f'<div class="cart-total">Total: ${total:,.2f}</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Continue Shopping",
            use_container_width=True
        ):
            st.session_state.page = "store"
            st.rerun()

    with col2:
        if st.button(
            "Proceed to Checkout",
            type="primary",
            use_container_width=True
        ):
            st.session_state.page = "checkout"
            st.rerun()


# ============================================================
# CHECKOUT
# ============================================================

def checkout_page():
    if not cart_items():
        st.warning("Your cart is empty.")
        st.session_state.page = "store"
        st.rerun()

    st.title("Checkout")

    user = get_current_user()

    account_email = (
        user.email
        if user
        else ""
    )

    st.subheader("Customer Information")

    with st.form("customer_form"):

        full_name = st.text_input(
            "Full name *",
            value=st.session_state.checkout_data.get(
                "full_name",
       