import streamlit as st
import requests
import uuid
from datetime import datetime
from supabase import create_client, Client


st.set_page_config(
    page_title="NovaStore",
    page_icon="🛍️",
    layout="centered",
)


# ============================================================
# SUPABASE
# ============================================================

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    FORMSPREE_ENDPOINT = st.secrets.get(
        "FORMSPREE_ENDPOINT",
        ""
    )

except Exception:
    st.error(
        "Missing Supabase or Formspree secrets."
    )
    st.stop()


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

DEFAULTS = {
    "access_token": None,
    "refresh_token": None,
    "user": None,
    "cart": {},
    "page": "Store",
    "order_confirmation": None,
    "auth_message": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# RESTORE SUPABASE SESSION
# ============================================================

if (
    st.session_state.access_token
    and st.session_state.refresh_token
):
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token,
        )
    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None


# ============================================================
# EMAIL CONFIRMATION / PKCE CALLBACK
# ============================================================

code = st.query_params.get("code")

if code:
    try:
        response = supabase.auth.exchange_code_for_session(
            {"auth_code": code}
        )

        if response and response.session:
            st.session_state.access_token = (
                response.session.access_token
            )
            st.session_state.refresh_token = (
                response.session.refresh_token
            )
            st.session_state.user = response.user

        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(
            f"Email confirmation could not be completed: {e}"
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_current_user():
    """Return the currently logged-in Supabase user."""
    if st.session_state.user:
        return st.session_state.user

    try:
        response = supabase.auth.get_user()

        if response and response.user:
            st.session_state.user = response.user
            return response.user

    except Exception:
        return None

    return None


def save_session(auth_response):
    """Save Supabase tokens into Streamlit session state."""
    if auth_response.session:
        st.session_state.access_token = (
            auth_response.session.access_token
        )

        st.session_state.refresh_token = (
            auth_response.session.refresh_token
        )

    if auth_response.user:
        st.session_state.user = auth_response.user


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None
    st.session_state.cart = {}
    st.session_state.page = "Store"
    st.session_state.order_confirmation = None

    st.rerun()


def money(value):
    return f"${float(value):,.2f}"


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

SAMPLE_PRODUCTS = [
    {
        "id": "sample-001",
        "name": "Wireless Headphones",
        "description": "Comfortable wireless headphones with clear sound.",
        "price": 39.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1505740420928-5e560c06d30e"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-002",
        "name": "Smart Watch",
        "description": "Modern smartwatch for everyday use.",
        "price": 59.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1523275335684-37898b6baf30"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-003",
        "name": "Portable Speaker",
        "description": "Compact Bluetooth speaker with powerful sound.",
        "price": 29.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1608043152269-423dbba4e7e1"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-004",
        "name": "Gaming Mouse",
        "description": "Responsive gaming mouse with ergonomic design.",
        "price": 24.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1527814050087-3793815479db"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-005",
        "name": "Laptop Backpack",
        "description": "Durable backpack suitable for laptops and accessories.",
        "price": 44.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1553062407-98eeb64c6a62"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    {
        "id": "sample-006",
        "name": "USB-C Hub",
        "description": "Multi-port USB-C hub for computers and tablets.",
        "price": 19.99,
        "image_url": (
            "https://images.unsplash.com/"
            "photo-1625842268584-8f3296236761"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
]


# ============================================================
# LOAD PRODUCTS
# ============================================================

def load_products():
    products = list(SAMPLE_PRODUCTS)

    try:
        response = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        database_products = response.data or []

        existing_ids = {
            str(product["id"])
            for product in products
        }

        for product in database_products:
            product_id = str(product.get("id", ""))

            if product_id not in existing_ids:
                products.append(
                    {
                        "id": product.get("id"),
                        "name": product.get(
                            "name",
                            "Unnamed Product",
                        ),
                        "description": product.get(
                            "description",
                            "",
                        ),
                        "price": float(
                            product.get("price", 0)
                        ),
                        "image_url": product.get(
                            "image_url",
                            "",
                        ),
                    }
                )

    except Exception:
        # Sample products still work if the products
        # table has an RLS/schema problem.
        pass

    return products


PRODUCTS = load_products()


# ============================================================
# CART FUNCTIONS
# ============================================================

def cart_count():
    return sum(st.session_state.cart.values())


def cart_total():
    total = 0

    product_map = {
        str(product["id"]): product
        for product in PRODUCTS
    }

    for product_id, quantity in st.session_state.cart.items():
        product = product_map.get(str(product_id))

        if product:
            total += float(product["price"]) * quantity

    return total


def add_to_cart(product_id):
    product_id = str(product_id)

    current = st.session_state.cart.get(
        product_id,
        0,
    )

    st.session_state.cart[product_id] = current + 1


def remove_from_cart(product_id):
    product_id = str(product_id)

    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]


def increase_quantity(product_id):
    product_id = str(product_id)

    st.session_state.cart[product_id] = (
        st.session_state.cart.get(product_id, 0) + 1
    )


def decrease_quantity(product_id):
    product_id = str(product_id)

    current = st.session_state.cart.get(
        product_id,
        0,
    )

    if current <= 1:
        st.session_state.cart.pop(
            product_id,
            None,
        )
    else:
        st.session_state.cart[product_id] = current - 1


# ============================================================
# HEADER
# ============================================================

st.title("🛍️ NovaStore")

user = get_current_user()

if user:
    email = getattr(user, "email", "") or ""

    st.caption(
        f"Logged in as {email} • 🛒 {cart_count()} item(s)"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "🛍️ Store",
            use_container_width=True,
        ):
            st.session_state.page = "Store"
            st.rerun()

    with col2:
        if st.button(
            "🛒 Cart",
            use_container_width=True,
        ):
            st.session_state.page = "Cart"
            st.rerun()

    with col3:
        if st.button(
            "🚪 Logout",
            use_container_width=True,
        ):
            logout()

else:
    st.caption("Shop our products and place your order securely.")


# ============================================================
# AUTH PAGE
# ============================================================

if not user:

    st.markdown("## 🔐 Account")

    login_tab, signup_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

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
            "🔐 Login",
            use_container_width=True,
        ):

            if not login_email or not login_password:
                st.error(
                    "Please enter your email and password."
                )

            else:
                try:
                    response = (
                        supabase
                        .auth
                        .sign_in_with_password(
                            {
                                "email": login_email,
                                "password": login_password,
                            }
                        )
                    )

                    save_session(response)

                    if response.user:
                        st.success(
                            "Login successful!"
                        )
                        st.rerun()

                except Exception as e:
                    error_text = str(e)

                    if (
                        "Email not confirmed"
                        in error_text
                    ):
                        st.warning(
                            "Your email has not been confirmed. "
                            "Check your inbox and press the "
                            "confirmation link."
                        )
                    else:
                        st.error(
                            f"Login failed: {error_text}"
                        )

    # --------------------------------------------------------
    # SIGN UP
    # --------------------------------------------------------

    with signup_tab:

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
            "📝 Create Account",
            use_container_width=True,
        ):

            if not signup_email:
                st.error(
                    "Please enter an email."
                )

            elif not signup_password:
                st.error(
                    "Please enter a password."
                )

            elif signup_password != signup_confirm:
                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:
                st.error(
                    "Password must contain at least 6 characters."
                )

            else:
                try:
                    response = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": signup_email,
                                "password": signup_password,
                            }
                        )
                    )

                    if response.user and not response.session:
                        st.success(
                            "Account created! "
                            "Check your email and confirm your "
                            "email address before logging in."
                        )

                    elif response.session:
                        save_session(response)
                        st.success(
                            "Account created successfully!"
                        )
                        st.rerun()

                    else:
                        st.success(
                            "Account created. "
                            "Check your email for confirmation."
                        )

                except Exception as e:
                    st.error(
                        f"Could not create account: {e}"
                    )

    st.stop()


# ============================================================
# EMAIL CONFIRMATION CHECK
# ============================================================

confirmed_at = getattr(
    user,
    "email_confirmed_at",
    None,
)

if confirmed_at is None:
    confirmed_at = getattr(
        user,
        "confirmed_at",
        None,
    )

if not confirmed_at:
    st.warning(
        "⚠️ Please confirm your email address before "
        "placing an order."
    )


# ============================================================
# STORE PAGE
# ============================================================

if st.session_state.page == "Store":

    st.markdown("## 🛍️ Products")

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search...",
        key="product_search",
    )

    filtered_products = PRODUCTS

    if search:
        search_lower = search.lower()

        filtered_products = [
            product
            for product in PRODUCTS
            if (
                search_lower
                in str(product["name"]).lower()
                or search_lower
                in str(
                    product.get(
                        "description",
                        "",
                    )
                ).lower()
            )
        ]

    if not filtered_products:
        st.info("No products found.")

    for product in filtered_products:

        st.markdown(
            '<div class="store-card">',
            unsafe_allow_html=True,
        )

        image_url = product.get(
            "image_url",
            "",
        )

        if image_url:
            st.image(
                image_url,
                use_container_width=True,
            )

        st.markdown(
            f'<div class="product-name">'
            f'{product["name"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="product-description">'
            f'{product.get("description", "")}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="price">'
            f'{money(product["price"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "🛒 Add to Cart",
            key=f"add_{product['id']}",
            use_container_width=True,
        ):
            add_to_cart(product["id"])
            st.success(
                f"{product['name']} added to cart."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# CART PAGE
# ============================================================

elif st.session_state.page == "Cart":

    st.markdown("## 🛒 Your Cart")

    if not st.session_state.cart:
        st.info(
            "Your cart is empty."
        )

        if st.button(
            "← Continue Shopping",
            use_container_width=True,
        ):
            st.session_state.page = "Store"
            st.rerun()

    else:

        product_map = {
            str(product["id"]): product
            for product in PRODUCTS
        }

        for product_id, quantity in list(
            st.session_state.cart.items()
        ):

            product = product_map.get(
                str(product_id)
            )

            if not product:
                continue

            st.markdown(
                '<div class="store-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"### {product['name']}"
            )

            line_total = (
                float(product["price"])
                * quantity
            )

            st.write(
                f"{money(product['price'])} × "
                f"{quantity} = "
                f"**{money(line_total)}**"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button(
                    "➖",
                    key=f"minus_{product_id}",
                ):
                    decrease_quantity(product_id)
                    st.rerun()

            with col2:
                st.write(
                    f"Qty: {quantity}"
                )

            with col3:
                if st.button(
                    "➕",
                    key=f"plus_{product_id}",
                ):
                    increase_quantity(product_id)
                    st.rerun()

            with col4:
                if st.button(
                    "🗑️",
                    key=f"remove_{product_id}",
                ):
                    remove_from_cart(product_id)
                    st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        total = cart_total()

        st.markdown(
            f"## Total: {money(total)}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "← Continue Shopping",
                use_container_width=True,
            ):
                st.session_state.page = "Store"
                st.rerun()

        with col2:
            if st.button(
                "💳 Checkout",
                use_container_width=True,
            ):
                st.session_state.page = "Checkout"
                st.rerun()


# ============================================================
# CHECKOUT PAGE
# ============================================================

elif st.session_state.page == "Checkout":

    st.markdown("## 💳 Checkout")

    if not st.session_state.cart:
        st.warning(
            "Your cart is empty."
        )

        if st.button(
            "← Back to Store",
            use_container_width=True,
        ):
            st.session_state.page = "Store"
            st.rerun()

    else:

        # ----------------------------------------------------
        # ORDER SUMMARY
        # ----------------------------------------------------

        st.markdown("### 🧾 Order Summary")

        product_map = {
            str(product["id"]): product
            for product in PRODUCTS
        }

        for product_id, quantity in (
            st.session_state.cart.items()
        ):

            product = product_map.get(
                str(product_id)
            )

            if product:
                line_total = (
                    float(product["price"])
                    * quantity
                )

                st.write(
                    f"**{product['name']}** × "
                    f"{quantity} — "
                    f"{money(line_total)}"
                )

        total = cart_total()

        st.markdown(
            f"### Total: {money(total)}"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # CUSTOMER INFORMATION
        # ----------------------------------------------------

        st.markdown("### 👤 Delivery Information")

        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="checkout_full_name",
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter your phone number",
            key="checkout_phone",
        )

        address = st.text_area(
            "Delivery Address",
            placeholder="Enter your full delivery address",
            key="checkout_address",
        )

        country = st.text_input(
            "Country",
            value="Nigeria",
            key="checkout_country",
        )

        state = st.text_input(
            "State",
            placeholder="Enter your state",
            key="checkout_state",
        )

        customer_email = st.text_input(
            "Email",
            value=getattr(
                user,
                "email",
                "",
            ) or "",
            key="checkout_email",
        )

        st.markdown("---")

        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------

        st.markdown("### 💰 Payment Method")

        payment_method = st.selectbox(
            "Choose payment method",
            [
                "Bank Transfer",
                "Gift Card",
            ],
            key="checkout_payment_method",
        )

        st.markdown("---")

        # ----------------------------------------------------
        # PAYMENT PROOF
        # ----------------------------------------------------

        st.markdown(
            "### 📎 Payment Proof"
        )

        payment_proof = st.file_uploader(
            "📷 Take Photo / Choose File",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            accept_multiple_files=False,
            key="checkout_payment_proof",
        )

        if payment_proof is not None:
            st.success(
                f"✅ File ready: {payment_proof.name}"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # CONFIRM ORDER
        # ----------------------------------------------------

        if st.button(
            "✅ Confirm Order",
            use_container_width=True,
            type="primary",
        ):

            # -----------------------------------------------
            # VALIDATION
            # -----------------------------------------------

            missing = []

            if not full_name.strip():
                missing.append("Full Name")

            if not phone.strip():
                missing.append("Phone Number")

            if not address.strip():
                missing.append("Delivery Address")

            if not country.strip():
                missing.append("Country")

            if not state.strip():
                missing.append("State")

            if not customer_email.strip():
                missing.append("Email")

            if payment_proof is None:
                missing.append("Payment Proof")

            if missing:
                st.error(
                    "Please complete: "
                    + ", ".join(missing)
                )
                st.stop()

            # -----------------------------------------------
            # GENERATE ORDER ID
            # -----------------------------------------------

            order_code = (
                "ORD-"
                + datetime.now().strftime("%Y%m%d")
                + "-"
                + uuid.uuid4().hex[:6].upper()
            )

            # -----------------------------------------------
            # PAYMENT PROOF FILE
            # -----------------------------------------------

            proof_bytes = (
                payment_proof.getvalue()
            )

            proof_name = payment_proof.name

            proof_type = (
                payment_proof.type
                or "application/octet-stream"
            )

            # -----------------------------------------------
            # CREATE ORDER MESSAGE
            # -----------------------------------------------

            item_lines = []

            for product_id, quantity in (
                st.session_state.cart.items()
            ):

                product = product_map.get(
                    str(product_id)
                )

                if product:
                    item_lines.append(
                        f"{product['name']} "
                        f"x {quantity} = "
                        f"{money(float(product['price']) * quantity)}"
                    )

            items_text = "\n".join(
                item_lines
            )

            form_message = f"""
NEW ORDER

Order ID:
{order_code}

Customer:
{full_name}

Phone:
{phone}

Email:
{customer_email}

Address:
{address}

Country:
{country}

State:
{state}

Payment Method:
{payment_method}

Total:
{money(total)}

Products:
{items_text}

Payment proof:
Attached as a file.

IMPORTANT:
Payment has NOT been automatically verified.
The order should remain under review until the owner
checks the payment proof.
"""

            # -----------------------------------------------
            # SEND TO FORMSPREE
            # -----------------------------------------------

            formspree_success = False
            formspree_error = ""

            if FORMSPREE_ENDPOINT:

                try:
                    response = requests.post(
    FORMSPREE_ENDPOINT,
    data={
        "subject": f"New Order {order_code}",
        "order_id": order_code,
        "customer": full_name,
        "email": customer_email,
        "phone": phone,
        "address": address,
        "country": country,
        "state": state,
        "payment_method": payment_method,
        "total": money(total),
        "message": form_message,
    },
    files={
        "payment_proof": (
            proof_name,
            proof_bytes,
            proof_type,
        )
    },
    headers={
        "Accept": "application/json"
    },
    timeout=30,
)

                    if 200 <= response.status_code < 300:
                        formspree_success = True
                    else:
                        formspree_error = (
                            f"Formspree returned "
                            f"{response.status_code}: "
                            f"{response.text[:500]}"
                        )

                except Exception as e:
                    formspree_error = str(e)

            else:
                formspree_error = (
                    "FORMSPREE_ENDPOINT is missing."
                )

            # -----------------------------------------------
            # SAVE ORDER TO SUPABASE
            # -----------------------------------------------

            database_success = False
            database_error = ""

            try:

                current_user = get_current_user()

                if not current_user:
                    raise Exception(
                        "You are no longer logged in."
                    )

                user_id = current_user.id

                # Keep this row compatible with the
                # columns normally used in the orders table.
                order_row = {
                    "user_id": user_id,
                    "order_id": order_code,
                    "full_name": full_name,
                    "phone": phone,
                    "address": address,
                    "state": state,
                    "total": total,
                    "payment_method": payment_method,
                    "payment_proof_path": proof_name,
                    "status": "Payment Under Review",
                }

                order_response = (
                    supabase
                    .table("orders")
                    .insert(order_row)
                    .execute()
                )

                if not order_response.data:
                    raise Exception(
                        "Supabase did not return the created order."
                    )

                created_order = (
                    order_response.data[0]
                )

                database_order_id = created_order.get(
                    "id"
                )

                if not database_order_id:
                    raise Exception(
                        "The created order has no database ID."
                    )

                # -------------------------------------------
                # SAVE ORDER ITEMS
                # -------------------------------------------

                order_items = []

                for product_id, quantity in (
                    st.session_state.cart.items()
                ):

                    product = product_map.get(
                        str(product_id)
                    )

                    if product:
                        order_items.append(
                            {
                                "order_id": database_order_id,
                                "product_id": str(
                                    product["id"]
                                ),
                                "product_name": product[
                                    "name"
                                ],
                                "price": float(
                                    product["price"]
                                ),
                                "quantity": quantity,
                            }
                        )

                if order_items:
                    (
                        supabase
                        .table("order_items")
                        .insert(order_items)
                        .execute()
                    )

                database_success = True

            except Exception as e:
                database_error = str(e)

            # -----------------------------------------------
            # SAVE RESULT
            # -----------------------------------------------

            st.session_state.order_confirmation = {
                "order_code": order_code,
                "total": total,
                "formspree_success": formspree_success,
                "formspree_error": formspree_error,
                "database_success": database_success,
                "database_error": database_error,
            }

            if database_success:
                st.session_state.cart = {}

            st.rerun()


# ============================================================
# ORDER CONFIRMATION
# ============================================================

confirmation = st.session_state.order_confirmation

if confirmation:

    st.markdown("---")
    st.markdown("## 🎉 Order Submitted")

    order_code = confirmation[
        "order_code"
    ]

    st.markdown(
        f"""
        <div class="success-box">
            <strong>Order ID:</strong> {order_code}<br>
            <strong>Total:</strong> {money(confirmation["total"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Your payment proof has been submitted for review. "
        "Payment is not considered confirmed until the store "
        "owner verifies it."
    )

    # --------------------------------------------------------
    # FORMSPREE RESULT
    # --------------------------------------------------------

    if confirmation["formspree_success"]:

        st.success(
            "✅ Order information and payment-proof file "
            "were sent to Formspree."
        )

    else:

        st.warning(
            "⚠️ The order was not successfully sent to "
            "Formspree."
        )

        if confirmation["formspree_error"]:
            st.code(
                confirmation["formspree_error"]
            )

    # --------------------------------------------------------
    # DATABASE RESULT
    # --------------------------------------------------------

    if confirmation["database_success"]:

        st.success(
            "✅ Order saved in Supabase."
        )

    else:

        st.error(
            "❌ Order could not be saved in Supabase."
        )

        if confirmation["database_error"]:
            st.code(
                confirmation["database_error"]
            )

    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True,
    ):
        st.session_state.order_confirmation = None
        st.session_state.page = "Store"
        st.rerun()