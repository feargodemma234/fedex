import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Veyra",
    page_icon="🛍️",
    layout="wide"
)

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "cart" not in st.session_state:
    st.session_state.cart = {}


# ---------------- HELPERS ----------------

def money(x):
    return f"₦{float(x):,.2f}"


def total():
    return sum(
        x["price"] * x["quantity"]
        for x in st.session_state.cart.values()
    )


def count():
    return sum(
        x["quantity"]
        for x in st.session_state.cart.values()
    )


def products():
    try:
        return sb.table("products").select("*").execute().data or []
    except:
        return []


# ---------------- LOGIN ----------------

if not st.session_state.logged_in:

    st.title("🛍️ Veyra")
    st.subheader("Welcome")

    login, signup = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # LOGIN
    with login:

        email = st.text_input(
            "Email",
            key="email_login"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="password_login"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    result = sb.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password
                    })

                    if result.user:

                        # SAVE USER
                        st.session_state.user = result.user

                        # SAVE LOGIN STATUS
                        st.session_state.logged_in = True

                        # OPEN STORE
                        st.session_state.page = "Store"

                        st.success(
                            "✅ Login successful!"
                        )

                        st.rerun()

                except Exception as e:

                    error = str(e).lower()

                    if "not confirmed" in error:

                        st.error(
                            "📧 Please confirm your email first."
                        )

                    else:

                        st.error(
                            "❌ Login failed. Check your email "
                            "and password."
                        )


    # SIGN UP
    with signup:

        email = st.text_input(
            "Email",
            key="email_signup"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="password_signup"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="password_confirm"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Enter your email and password."
                )

            elif password != confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    result = sb.auth.sign_up({
                        "email": email.strip(),
                        "password": password
                    })

                    if result.user:

                        st.success(
                            "✅ Account created!"
                        )

                        st.info(
                            "📧 Check your email and click "
                            "the confirmation link."
                        )

                except Exception as e:

                    st.error(str(e))

    st.stop()


# ---------------- SIDEBAR ----------------

st.sidebar.title("🛍️ Veyra")

st.sidebar.write(
    f"👤 {st.session_state.user.email}"
)

pages = [
    "Store",
    "Cart",
    "My Orders"
]

page = st.sidebar.radio(
    "Menu",
    pages
)

st.sidebar.divider()

st.sidebar.write(
    f"🛒 {count()} items"
)

st.sidebar.write(
    f"💰 {money(total())}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    try:
        sb.auth.sign_out()
    except:
        pass

    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.cart = {}

    st.rerun()


# ---------------- STORE ----------------

if page == "Store":

    st.title("🛍️ Veyra Store")

    data = products()

    search = st.text_input(
        "🔎 Search products"
    ).lower()

    categories = sorted(
        set(
            p.get("category")
            for p in data
            if p.get("category")
        )
    )

    category = st.selectbox(
        "Category",
        ["All"] + categories
    )

    data = [
        p for p in data
        if (
            not search
            or search in p.get("name", "").lower()
            or search in p.get("description", "").lower()
        )
        and (
            category == "All"
            or p.get("category") == category
        )
    ]

    if not data:

        st.info(
            "No products available yet."
        )

    cols = st.columns(3)

    for i, p in enumerate(data):

        with cols[i % 3]:

            if p.get("image_url"):

                st.image(
                    p["image_url"],
                    use_container_width=True
                )

            st.subheader(
                p.get("name", "Product")
            )

            st.write(
                p.get("description", "")
            )

            st.write(
                f"### {money(p.get('price', 0))}"
            )

            if st.button(
                "🛒 Add to Cart",
                key=f"add_{p['id']}",
                use_container_width=True
            ):

                pid = str(p["id"])

                if pid not in st.session_state.cart:

                    st.session_state.cart[pid] = {
                        "id": p["id"],
                        "name": p["name"],
                        "price": float(p["price"]),
                        "quantity": 1
                    }

                else:

                    st.session_state.cart[pid]["quantity"] += 1

                st.rerun()


# ---------------- CART ----------------

elif page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info("Your cart is empty.")

    else:

        for pid, item in list(
            st.session_state.cart.items()
        ):

            a, b, c, d = st.columns(
                [4, 1, 1, 2]
            )

            with a:
                st.write(
                    f"**{item['name']}**"
                )

            with b:
                st.write(
                    f"× {item['quantity']}"
                )

            with c:

                if st.button(
                    "➖",
                    key=f"minus_{pid}"
                ):

                    item["quantity"] -= 1

                    if item["quantity"] <= 0:
                        del st.session_state.cart[pid]

                    st.rerun()

            with d:

                item_total = (
                    item["price"]
                    * item["quantity"]
                )

                st.write(
                    f"**{money(item_total)}**"
                )

        st.divider()

        st.subheader(
            f"🧾 TOTAL: {money(total())}"
        )

        if st.button(
            "📦 Place Order",
            type="primary",
            use_container_width=True
        ):

            try:

                order = sb.table(
                    "orders"
                ).insert({
                    "user_id": st.session_state.user.id,
                    "total": total(),
                    "status": "pending",
                    "payment_status": "unpaid"
                }).execute().data[0]

                items = [

                    {
                        "order_id": order["id"],
                        "product_id": x["id"],
                        "quantity": x["quantity"],
                        "price": x["price"]
                    }

                    for x in st.session_state.cart.values()
                ]

                sb.table(
                    "order_items"
                ).insert(items).execute()

                st.session_state.cart = {}

                st.success(
                    "🎉 Order created!"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))


# ---------------- ORDERS ----------------

elif page == "My Orders":

    st.title("📦 My Orders")

    try:

        orders = sb.table(
            "orders"
        ).select("*").eq(
            "user_id",
            st.session_state.user.id
        ).order(
            "created_at",
            desc=True
        ).execute().data or []

        if not orders:

            st.info(
                "You have no orders yet."
            )

        for order in orders:

            with st.expander(
                f"Order #{order['id']}"
            ):

                st.write(
                    f"Total: {money(order['total'])}"
                )

                st.write(
                    f"Status: {order['status']}"
                )

                st.write(
                    f"Payment: {order['payment_status']}"
                )

    except Exception as e:

        st.error(str(e))