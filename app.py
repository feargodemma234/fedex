import streamlit as st
import requests
from supabase import create_client

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="My Store",
    page_icon="🛍️",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
FORMSPREE_ENDPOINT = st.secrets.get("FORMSPREE_ENDPOINT", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# SAMPLE PRODUCTS
# -----------------------------
SAMPLE_PRODUCTS = [
    {
        "id": "sample-1",
        "name": "Wireless Headphones",
        "description": "Premium wireless headphones with clear sound.",
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
        "description": "Comfortable shoes for sports and everyday use.",
        "price": 59.99,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },
    {
        "id": "sample-4",
        "name": "Backpack",
        "description": "Durable backpack suitable for school and travel.",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62"
    },
    {
        "id": "sample-5",
        "name": "Gaming Mouse",
        "description": "Fast and accurate mouse for gaming and work.",
        "price": 29.99,
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db"
    },
    {
        "id": "sample-6",
        "name": "Bluetooth Speaker",
        "description": "Portable speaker with powerful sound.",
        "price": 44.99,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1"
    }
]

# -----------------------------
# SESSION STATE
# -----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# AUTH
# -----------------------------
def get_user():
    try:
        return supabase.auth.get_user().user
    except:
        return None


if st.session_state.user is None:
    st.session_state.user = get_user()


def login():
    email = st.session_state.login_email
    password = st.session_state.login_password

    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        st.session_state.user = result.user
        st.success("Login successful!")
        st.rerun()

    except Exception as e:
        st.error("Login failed. Check your email and password.")


def signup():
    email = st.session_state.signup_email
    password = st.session_state.signup_password
    confirm = st.session_state.signup_confirm

    if password != confirm:
        st.error("Passwords do not match.")
        return

    try:
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        st.success(
            "Account created! Check your email and confirm your account "
            "before logging in."
        )

    except Exception as e:
        st.error(str(e))


# -----------------------------
# LOGIN / SIGNUP PAGE
# -----------------------------
if not st.session_state.user:

    st.title("🛍️ My Store")
    st.write("Create an account or login to continue.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        st.text_input("Email", key="login_email")
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

    with signup_tab:
        st.text_input("Email", key="signup_email")
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


# -----------------------------
# LOAD PRODUCTS
# -----------------------------
def load_products():

    try:
        result = (
            supabase
            .table("products")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        products = result.data or []

        # Show sample products if database is empty
        if not products:
            return SAMPLE_PRODUCTS

        return products

    except Exception:
        return SAMPLE_PRODUCTS


products = load_products()

product_map = {
    str(product["id"]): product
    for product in products
}


# -----------------------------
# HEADER
# -----------------------------
st.title("🛍️ My Store")

user_email = st.session_state.user.email

col1, col2, col3 = st.columns([5, 2, 1])

with col1:
    st.write(f"Welcome, **{user_email}**")

with col2:
    if st.button(
        f"🛒 Cart ({sum(st.session_state.cart.values())})"
    ):
        st.session_state.page = "Cart"
        st.rerun()

with col3:
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.cart = {}
        st.rerun()


# -----------------------------
# SEARCH
# -----------------------------
search = st.text_input(
    "🔎 Search products",
    placeholder="Search for a product..."
)

if search:
    products = [
        p for p in products
        if search.lower() in p["name"].lower()
        or search.lower() in (p.get("description") or "").lower()
    ]


# -----------------------------
# NAVIGATION
# -----------------------------
if st.button("🏪 Store"):
    st.session_state.page = "Store"

if st.button("📦 My Orders"):
    st.session_state.page = "Orders"


# -----------------------------
# STORE
# -----------------------------
if st.session_state.page == "Store":

    st.subheader("Products")

    columns = st.columns(3)

    for i, product in enumerate(products):

        with columns[i % 3]:

            st.image(
                product.get("image_url", ""),
                use_container_width=True
            )

            st.subheader(product["name"])

            st.write(product.get("description", ""))

            st.write(
                f"**${float(product['price']):,.2f}**"
            )

            if st.button(
                "Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):

                pid = str(product["id"])

                st.session_state.cart[pid] = (
                    st.session_state.cart.get(pid, 0) + 1
                )

                st.success("Added to cart!")


# -----------------------------
# CART
# -----------------------------
elif st.session_state.page == "Cart":

    st.subheader("🛒 Your Cart")

    if not st.session_state.cart:

        st.info("Your cart is empty.")

        if st.button("Continue Shopping"):
            st.session_state.page = "Store"
            st.rerun()

    else:

        total = 0

        for pid, quantity in list(st.session_state.cart.items()):

            product = product_map.get(pid)

            if not product:
                continue

            price = float(product["price"])
            subtotal = price * quantity
            total += subtotal

            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

            with c1:
                st.write(f"**{product['name']}**")
                st.write(f"${price:.2f} each")

            with c2:
                st.write(f"Quantity: {quantity}")

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
                    if st.session_state.cart[pid] > 1:
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

        st.subheader(f"Total: ${total:,.2f}")

        if st.button(
            "Proceed to Checkout",
            use_container_width=True
        ):
            st.session_state.page = "Checkout"
            st.rerun()


# -----------------------------
# CHECKOUT
# -----------------------------
elif st.session_state.page == "Checkout":

    st.subheader("🧾 Checkout")

    if not st.session_state.cart:
        st.warning("Your cart is empty.")
        st.stop()

    total = sum(
        float(product_map[pid]["price"]) * quantity
        for pid, quantity in st.session_state.cart.items()
        if pid in product_map
    )

    st.write(f"### Total: ${total:,.2f}")

    with st.form("checkout_form"):

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

        payment_method = st.selectbox(
            "Payment Method",
            [
                "Bank Transfer",
                "Gift Card"
            ]
        )

        submitted = st.form_submit_button(
            "Confirm Order",
            use_container_width=True
        )

    if submitted:

        # Remove accidental spaces
        full_name = full_name.strip()
        phone = phone.strip()
        address = address.strip()
        country = country.strip()
        state = state.strip()
        customer_email = customer_email.strip()

        # Check required information
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
                "Please complete: " +
                ", ".join(missing)
            )

        else:

            try:

                import uuid

                order_number = (
                    "ORD-" +
                    uuid.uuid4().hex[:8].upper()
                )

                # Create order
                order = supabase.table("orders").insert({
                    "user_id": st.session_state.user.id,
                    "order_id": order_number,
                    "full_name": full_name,
                    "phone": phone,
                    "address": address,
                    "country": country,
                    "state": state,
                    "customer_email": customer_email,
                    "total": total,
                    "payment_method": payment_method,
                    "status": "Received"
                }).execute()

                order_db_id = order.data[0]["id"]

                # Create order items
                items = []

                for pid, quantity in st.session_state.cart.items():

                    product = product_map.get(pid)

                    if product:

                        items.append({
                            "order_id": order_db_id,
                            "product_id": str(product["id"]),
                            "product_name": product["name"],
                            "price": float(product["price"]),
                            "quantity": quantity
                        })

                if items:
                    supabase.table(
                        "order_items"
                    ).insert(items).execute()

                # Formspree notification
                if FORMSPREE_ENDPOINT:

                    message = f"""
New Order

Order ID: {order_number}

Customer: {full_name}
Email: {customer_email}
Phone: {phone}

Address:
{address}

Country: {country}
State: {state}

Payment Method:
{payment_method}

Total:
${total:,.2f}

Status:
Received
"""

                    try:

                        requests.post(
                            FORMSPREE_ENDPOINT,
                            data={
                                "message": message,
                                "email": customer_email
                            },
                            timeout=10
                        )

                    except:
                        pass

                # Clear cart
                st.session_state.cart = {}

                # Save order information
                st.session_state.order_number = order_number
                st.session_state.order_total = total

                # Go to success page
                st.session_state.page = "Success"

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not create order: {e}"
                )

# -----------------------------
# ORDER SUCCESS
# -----------------------------
elif st.session_state.page == "Success":

    st.success("🎉 Order placed successfully!")

    st.write(
        f"### Order ID: `{st.session_state.order_number}`"
    )

    st.write(
        f"Total: **${st.session_state.order_total:,.2f}**"
    )

    st.info(
        "Your order has been received. Payment has NOT been "
        "automatically verified."
    )

    if st.button("Back to Store"):
        st.session_state.page = "Store"
        st.rerun()


# -----------------------------
# MY ORDERS
# -----------------------------
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
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        orders = result.data or []

        if not orders:
            st.info("You haven't placed any orders yet.")

        for order in orders:

            with st.expander(
                f"{order['order_id']} — ${float(order['total']):,.2f}"
            ):

                st.write(
                    f"**Status:** {order.get('status', 'Received')}"
                )

                st.write(
                    f"**Payment:** {order.get('payment_method', '')}"
                )

                st.write(
                    f"**Date:** {order.get('created_at', '')}"
                )

    except Exception as e:
        st.error(f"Could not load orders: {e}")