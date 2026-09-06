import streamlit as st
from supabase import create_client, Client
import uuid
import smtplib
from email.message import EmailMessage
from urllib.parse import quote


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DARK UI
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #07111f;
        color: #f5f7fa;
    }

    [data-testid="stSidebar"] {
        background: #0b1728;
    }

    [data-testid="stHeader"] {
        background: #07111f;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, label, span, div {
        color: #e6edf5;
    }

    .product-card {
        background: #0d1b2e;
        border: 1px solid #20334d;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 20px;
        min-height: 390px;
    }

    .product-name {
        color: #ffffff;
        font-size: 20px;
        font-weight: 700;
        margin-top: 10px;
    }

    .product-description {
        color: #b9c6d6;
        font-size: 14px;
        margin-top: 6px;
        min-height: 45px;
    }

    .price {
        color: #6ee7b7;
        font-size: 21px;
        font-weight: 700;
        margin-top: 10px;
    }

    .order-box {
        background: #0d1b2e;
        border: 1px solid #20334d;
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
    }

    .success-box {
        background: #09271d;
        border: 1px solid #1e7a58;
        border-radius: 15px;
        padding: 20px;
    }

    .warning-box {
        background: #2b2110;
        border: 1px solid #8a6a20;
        border-radius: 15px;
        padding: 20px;
    }

    .small-text {
        color: #aebccd;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SECRETS
# =========================================================

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

STORE_EMAIL = "quantumindustries258@gmail.com"


# =========================================================
# SUPABASE
# =========================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "Supabase settings are missing. Add SUPABASE_URL and SUPABASE_KEY to secrets."
    )
    st.stop()


supabase = get_supabase()


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

if "last_order" not in st.session_state:
    st.session_state.last_order = None


# =========================================================
# AUTH CALLBACK
# =========================================================

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
                    "Email confirmed successfully!"
                )

                st.rerun()

        except Exception:
            pass


# =========================================================
# RESTORE SESSION
# =========================================================

def restore_session():

    if st.session_state.access_token:

        try:

            response = supabase.auth.get_user(
                st.session_state.access_token
            )

            if response and response.user:

                st.session_state.user = response.user
                return True

        except Exception:
            pass

    return False


restore_session()


# =========================================================
# LOGOUT
# =========================================================

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

    st.rerun()


# =========================================================
# SAMPLE PRODUCTS
# =========================================================

SAMPLE_PRODUCTS = [

    {
        "id": "sample-1",
        "name": "Quantum Wireless Headphones",
        "description": "Premium wireless headphones with clear sound and comfortable design.",
        "price": 39.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"
    },

    {
        "id": "sample-2",
        "name": "Quantum Smart Watch",
        "description": "Modern smartwatch with fitness tracking and notifications.",
        "price": 59.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80"
    },

    {
        "id": "sample-3",
        "name": "Quantum Sneakers",
        "description": "Comfortable everyday sneakers with a modern design.",
        "price": 49.99,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80"
    },

    {
        "id": "sample-4",
        "name": "Quantum Backpack",
        "description": "Durable backpack suitable for school, work and travel.",
        "price": 34.99,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"
    },

    {
        "id": "sample-5",
        "name": "Quantum Smartphone",
        "description": "Sleek modern smartphone for everyday use.",
        "price": 299.99,
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"
    },

    {
        "id": "sample-6",
        "name": "Quantum Laptop",
        "description": "Powerful laptop for school, work and entertainment.",
        "price": 699.99,
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"
    }

]


# =========================================================
# LOAD PRODUCTS
# =========================================================

def load_products():

    try:

        response = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        database_products = response.data or []

        products = []

        for product in database_products:

            product_id = (
                product.get("id")
                or product.get("product_id")
            )

            name = product.get("name")

            if not product_id or not name:
                continue

            products.append(
                {
                    "id": str(product_id),

                    "name": name,

                    "description": (
                        product.get("description")
                        or ""
                    ),

                    "price": float(
                        product.get("price") or 0
                    ),

                    "image": (
                        product.get("image")
                        or product.get("image_url")
                        or ""
                    )
                }
            )

        if products:
            return products

    except Exception:
        pass

    return SAMPLE_PRODUCTS


products = load_products()


# =========================================================
# PRODUCT HELPERS
# =========================================================

def get_product(product_id):

    for product in products:

        if str(product["id"]) == str(product_id):
            return product

    return None


def add_to_cart(product_id):

    product_id = str(product_id)

    if product_id in st.session_state.cart:

        st.session_state.cart[product_id] += 1

    else:

        st.session_state.cart[product_id] = 1


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


def get_cart_items():

    items = []

    for product_id, quantity in st.session_state.cart.items():

        product = get_product(product_id)

        if product:

            item = product.copy()

            item["quantity"] = quantity

            items.append(item)

    return items


def cart_total():

    total = 0

    for item in get_cart_items():

        total += (
            float(item["price"])
            * int(item["quantity"])
        )

    return total


def money(value):

    return f"${float(value):,.2f}"


# =========================================================
# EMAIL ORDER TO OWNER
# =========================================================

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


    items_text = ""

    for item in cart_items:

        line_total = (
            float(item["price"])
            * int(item["quantity"])
        )

        items_text += (
            f"- {item['name']} | "
            f"Qty: {item['quantity']} | "
            f"Price: {money(line_total)}\n"
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


IMPORTANT
---------

Payment has NOT been verified.

The customer must send their payment proof
to the store email separately.

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

        return False, str(e)


# =========================================================
# AUTH PAGE
# =========================================================

def authentication_page():

    st.title("🛒 Quantum Store")

    st.write(
        "Create an account or login to continue."
    )

    tab1, tab2 = st.tabs(
        ["Login", "Create Account"]
    )


    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

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
            use_container_width=True
        ):

            if not email or not password:

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
                                "email": email.strip(),
                                "password": password
                            }
                        )
                    )

                    if response and response.session:

                        st.session_state.user = (
                            response.user
                        )

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

                    else:

                        st.error(
                            "Login failed."
                        )

                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )


    # -----------------------------------------------------
    # SIGN UP
    # -----------------------------------------------------

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

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )


        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not signup_email:

                st.error(
                    "Enter your email."
                )

            elif not signup_password:

                st.error(
                    "Enter a password."
                )

            elif signup_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    response = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": signup_email.strip(),
                                "password": signup_password
                            }
                        )
                    )

                    st.success(
                        "Account created! "
                        "Check your email and confirm your account."
                    )

                except Exception as e:

                    st.error(
                        f"Could not create account: {e}"
                    )


# =========================================================
# REQUIRE LOGIN
# =========================================================

if not st.session_state.user:

    authentication_page()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("Quantum Store")

    st.write(
        f"Logged in as:"
    )

    st.caption(
        st.session_state.user.email
    )

    st.divider()


    if st.button(
        "🛍️ Store",
        use_container_width=True
    ):

        st.session_state.page = "Store"
        st.rerun()


    if st.button(
        f"🛒 Cart ({sum(st.session_state.cart.values())})",
        use_container_width=True
    ):

        st.session_state.page = "Cart"
        st.rerun()


    if st.button(
        "📦 Checkout",
        use_container_width=True
    ):

        st.session_state.page = "Checkout"
        st.rerun()


    st.divider()


    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout()


# =========================================================
# STORE
# =========================================================

if st.session_state.page == "Store":

    st.title("🛍️ Our Products")

    st.write(
        "Choose a product and add it to your cart."
    )

    cols = st.columns(3)


    for index, product in enumerate(products):

        with cols[index % 3]:

            st.markdown(
                '<div class="product-card">',
                unsafe_allow_html=True
            )


            if product.get("image"):

                st.image(
                    product["image"],
                    use_container_width=True
                )


            st.markdown(
                f"""
                <div class="product-name">
                    {product['name']}
                </div>

                <div class="product-description">
                    {product['description']}
                </div>

                <div class="price">
                    {money(product['price'])}
                </div>
                """,
                unsafe_allow_html=True
            )


            if st.button(
                "Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):

                add_to_cart(product["id"])

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

    st.title("🛒 Your Cart")


    items = get_cart_items()


    if not items:

        st.info(
            "Your cart is empty."
        )

        if st.button("Continue Shopping"):

            st.session_state.page = "Store"
            st.rerun()

    else:

        for item in items:

            col1, col2, col3, col4 = st.columns(
                [2, 3, 1, 1]
            )


            with col1:

                if item.get("image"):

                    st.image(
                        item["image"],
                        width=120
                    )


            with col2:

                st.subheader(
                    item["name"]
                )

                st.write(
                    money(item["price"])
                )


            with col3:

                st.write(
                    f"Quantity: {item['quantity']}"
                )

                plus = st.button(
                    "+",
                    key=f"plus_{item['id']}"
                )

                minus = st.button(
                    "-",
                    key=f"minus_{item['id']}"
                )

                if plus:

                    add_to_cart(item["id"])
                    st.rerun()

                                if minus:

                    remove_from_cart(item["id"])
                    st.rerun()


            with col4:

                if st.button(
                    "Remove",
                    key=f"remove_{item['id']}"
                ):

                    delete_from_cart(item["id"])
                    st.rerun()


            st.divider()


        st.subheader(
            f"Total: {money(cart_total())}"
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

    st.title("📦 Checkout")

    items = get_cart_items()

    if not items:

        st.warning("Your cart is empty.")

        if st.button("Go to Store"):

            st.session_state.page = "Store"
            st.rerun()

        st.stop()


    st.subheader("Order Summary")

    for item in items:

        line_total = (
            float(item["price"])
            * int(item["quantity"])
        )

        st.write(
            f"**{item['name']}** × "
            f"{item['quantity']} — "
            f"{money(line_total)}"
        )


    st.divider()


    total = cart_total()

    st.subheader(
        f"Total: {money(total)}"
    )


    st.divider()


    st.subheader("Customer Information")


    full_name = st.text_input(
        "Full Name"
    )

    customer_email = st.text_input(
        "Email",
        value=st.session_state.user.email
    )

    phone = st.text_input(
        "Phone Number"
    )

    address = st.text_area(
        "Delivery Address"
    )

    country = st.text_input(
        "Country"
    )

    state = st.text_input(
        "State"
    )


    st.subheader("Payment Method")


    payment_method = st.selectbox(
        "Choose payment method",
        [
            "Bank Transfer",
            "Gift Card"
        ]
    )


    if payment_method == "Bank Transfer":

        st.info(
            "After placing your order, you will be able "
            "to send your payment proof directly to the store email."
        )


    elif payment_method == "Gift Card":

        st.info(
            "After placing your order, send your "
            "payment proof to the store email."
        )


    st.divider()


    if st.button(
        "Confirm Order",
        use_container_width=True,
        type="primary"
    ):

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


        # =================================================
        # CREATE ORDER IDs
        # =================================================

        order_id = str(
            uuid.uuid4()
        )

        order_code = (
            "ORD-"
            + uuid.uuid4().hex[:8].upper()
        )

        order_status = "Received"


        # =================================================
        # ORDER ROW
        # =================================================

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

            "status": order_status
        }


        # =================================================
        # SAVE ORDER
        # =================================================

        try:

            order_response = (
                supabase
                .table("orders")
                .insert(order_row)
                .execute()
            )

            if not order_response.data:

                st.error(
                    "Could not create order."
                )

                st.stop()

        except Exception as e:

            st.error(
                f"Could not create order: {e}"
            )

            st.stop()


        # =================================================
        # SAVE ORDER ITEMS
        # =================================================

        order_items = []

        for item in items:

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
                    )
                }
            )


        try:

            (
                supabase
                .table("order_items")
                .insert(order_items)
                .execute()
            )

        except Exception as e:

            st.warning(
                "The order was created, but the "
                f"order items could not be saved: {e}"
            )


        # =================================================
        # SEND ORDER EMAIL
        # =================================================

        email_sent = False
        email_error = None


        if SMTP_EMAIL and SMTP_APP_PASSWORD:

            email_sent, email_error = send_order_email(

                order_code,

                full_name,

                customer_email,

                phone,

                address,

                country,

                state,

                payment_method,

                total,

                items
            )


        # =================================================
        # SAVE LAST ORDER
        # =================================================

        st.session_state.last_order = {

            "order_id": order_id,

            "order_code": order_code,

            "full_name": full_name,

            "email": customer_email,

            "payment_method": payment_method,

            "total": total,

            "email_sent": email_sent,

            "email_error": email_error
        }


        # =================================================
        # CLEAR CART
        # =================================================

        st.session_state.cart = {}

        st.session_state.page = "Confirmation"

        st.rerun()


# =========================================================
# ORDER CONFIRMATION
# =========================================================

elif st.session_state.page == "Confirmation":

    order = st.session_state.last_order


    if not order:

        st.warning(
            "No recent order found."
        )

        if st.button("Back to Store"):

            st.session_state.page = "Store"
            st.rerun()

        st.stop()


    st.title("✅ Order Received")


    st.markdown(
        f"""
        <div class="success-box">

        <h3>Thank you, {order['full_name']}!</h3>

        <p>
        Your order has been received successfully.
        </p>

        <p>
        <strong>Order Number:</strong>
        {order['order_code']}
        </p>

        <p>
        <strong>Total:</strong>
        {money(order['total'])}
        </p>

        <p>
        <strong>Payment Method:</strong>
        {order['payment_method']}
        </p>

        <p>
        <strong>Status:</strong>
        Payment Under Review
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("")


    st.subheader(
        "📧 Send Your Payment Proof"
    )


    st.write(
        "After making your payment, attach your payment "
        "screenshot or proof to an email and send it directly "
        "to our store email."
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

Payment Method: {order['payment_method']}

Order Total: {money(order['total'])}

I have attached my payment proof.

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
               padding:14px;
               border-radius:10px;
               text-decoration:none;
               font-weight:700;
               margin-top:10px;
           ">
           📎 Send Proof of Payment
        </a>
        """,
        unsafe_allow_html=True
    )


    st.write("")


    st.info(
        f"""
        **Send the payment proof to:**

        {STORE_EMAIL}

        Tap **Send Proof of Payment** to open your
        email app, then attach your payment screenshot
        and send it.
        """
    )


    st.warning(
        "Payment is not automatically verified. "
        "The store must check the proof before confirming payment."
    )


    if order["email_sent"]:

        st.success(
            "Your order details were sent to the store."
        )

    else:

        st.warning(
            "The order was saved, but the store notification "
            "email could not be sent automatically."
        )

        if order["email_error"]:

            st.caption(
                f"Email error: {order['email_error']}"
            )


    st.divider()


    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True
    ):

        st.session_state.page = "Store"

        st.session_state.last_order = None

        st.rerun()

              