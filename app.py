import streamlit as st
from supabase import create_client

# ================= CONFIG =================

st.set_page_config(
    page_title="Veyra",
    page_icon="🛍️",
    layout="wide"
)

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Store"


# ================= HELPERS =================

def money(n):
    return f"₦{float(n):,.2f}"


def get_user():
    try:
        return sb.auth.get_user().user
    except:
        return None


def get_products():
    try:
        return sb.table("products").select("*").execute().data or []
    except:
        return []


def is_owner():
    u = get_user()

    if not u:
        return False

    try:
        p = sb.table("profiles").select("role").eq(
            "id", u.id
        ).maybe_single().execute().data

        return p and p.get("role") == "owner"

    except:
        return False


def cart_total():
    return sum(
        item["price"] * item["quantity"]
        for item in st.session_state.cart.values()
    )


def cart_count():
    return sum(
        item["quantity"]
        for item in st.session_state.cart.values()
    )


# ================= AUTH =================

u = get_user()

if not u:

    st.title("🛍️ Veyra")
    st.write("Welcome to Veyra")

    login, signup = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # -------- LOGIN --------

    with login:

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

                    result = sb.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    if result.user:

                        st.session_state.page = "Store"

                        st.success(
                            "✅ Login successful!"
                        )

                        st.rerun()

                except Exception as e:

                    if "not confirmed" in str(e).lower():

                        st.error(
                            "📧 Please confirm your email first."
                        )

                    else:

                        st.error(
                            "❌ Incorrect email or password."
                        )


    # -------- SIGN UP --------

    with signup:

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Enter an email and password."
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

                    sb.auth.sign_up({
                        "email": email,
                        "password": password
                    })

                    st.success(
                        "✅ Account created!"
                    )

                    st.info(
                        "📧 Check your email and confirm "
                        "your account, then log in."
                    )

                except Exception as e:

                    st.error(str(e))

    st.stop()


# ================= SIDEBAR =================

st.sidebar.title("🛍️ Veyra")

pages = [
    "Store",
    "Cart",
    "My Orders"
]

if is_owner():

    pages += [
        "Owner Dashboard",
        "Analytics"
    ]

page = st.sidebar.radio(
    "Menu",
    pages,
    index=(
        pages.index(st.session_state.page)
        if st.session_state.page in pages
        else 0
    )
)

st.session_state.page = page

st.sidebar.write(
    f"🛒 Cart: {cart_count()} items"
)

st.sidebar.write(
    f"💰 Total: {money(cart_total())}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    sb.auth.sign_out()

    st.session_state.cart = {}

    st.session_state.page = "Store"

    st.rerun()


# ================= STORE =================

if page == "Store":

    st.title("🛍️ Veyra Store")

    data = get_products()

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

    cols = st.columns(3)

    for i, p in enumerate(data):

        with cols[i % 3]:

            if p.get("image_url"):

                st.image(
                    p["image_url"],
                    use_container_width=True
                )

            st.subheader(
                p["name"]
            )

            st.write(
                p.get("description", "")
            )

            st.write(
                f"### {money(p['price'])}"
            )

            st.caption(
                f"Stock: {p.get('stock', 0)}"
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

                    st.session_state.cart[
                        pid
                    ]["quantity"] += 1

                st.rerun()


# ================= CART =================

elif page == "Cart":

    st.title("🛒 Your Cart")

    cart = st.session_state.cart

    if not cart:

        st.info(
            "Your cart is empty."
        )

    else:

        st.subheader(
            "Items in your cart"
        )

        for pid, item in list(cart.items()):

            col1, col2, col3, col4 = st.columns(
                [4, 1, 1, 2]
            )

            with col1:

                st.write(
                    f"**{item['name']}**"
                )

                st.write(
                    money(item["price"])
                    + " each"
                )

            with col2:

                st.write(
                    f"Qty: {item['quantity']}"
                )

            with col3:

                if st.button(
                    "➖",
                    key=f"minus_{pid}"
                ):

                    item["quantity"] -= 1

                    if item["quantity"] <= 0:

                        del cart[pid]

                    st.rerun()

            with col4:

                item_total = (
                    item["price"]
                    * item["quantity"]
                )

                st.write(
                    f"**{money(item_total)}**"
                )

        st.divider()

        # AUTOMATIC TOTAL

        subtotal = cart_total()

        st.subheader(
            f"🧾 Cart Total: {money(subtotal)}"
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
                    "user_id": u.id,
                    "total": subtotal,
                    "status": "pending",
                    "payment_status": "unpaid"
                }).execute().data[0]

                items = [

                    {
                        "order_id": order["id"],
                        "product_id": item["id"],
                        "quantity": item["quantity"],
                        "price": item["price"]
                    }

                    for item in cart.values()

                ]

                sb.table(
                    "order_items"
                ).insert(
                    items
                ).execute()

                st.session_state.cart = {}

                st.success(
                    f"🎉 Order created! "
                    f"Total: {money(subtotal)}"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Order failed: {e}"
                )


# ================= ORDERS =================

elif page == "My Orders":

    st.title("📦 My Orders")

    orders = sb.table(
        "orders"
    ).select("*").eq(
        "user_id",
        u.id
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
                f"Total: **{money(order['total'])}**"
            )

            st.write(
                f"Status: **{order['status']}**"
            )

            st.write(
                f"Payment: **{order['payment_status']}**"
            )


# ================= OWNER DASHBOARD =================

elif page == "Owner Dashboard":

    st.title("👑 Owner Dashboard")

    with st.form("add_product"):

        name = st.text_input(
            "Product name"
        )

        description = st.text_area(
            "Description"
        )

        price = st.number_input(
            "Price (NGN)",
            min_value=0.0,
            step=100.0
        )

        category = st.text_input(
            "Category"
        )

        image = st.text_input(
            "Image URL"
        )

        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1
        )

        add = st.form_submit_button(
            "➕ Add Product"
        )

    if add:

        try:

            sb.table(
                "products"
            ).insert({
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "image_url": image,
                "stock": stock
            }).execute()

            st.success(
                "✅ Product added!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                str(e)
            )


# ================= ANALYTICS =================

elif page == "Analytics":

    st.title("📊 Sales Analytics")

    orders = sb.table(
        "orders"
    ).select(
        "total,payment_status"
    ).execute().data or []

    paid = [
        o for o in orders
        if o.get("payment_status") == "paid"
    ]

    revenue = sum(
        float(o["total"])
        for o in paid
    )

    a, b, c = st.columns(3)

    a.metric(
        "💰 Revenue",
        money(revenue)
    )

    b.metric(
        "📦 Orders",
        len(orders)
    )

    c.metric(
        "✅ Paid Orders",
        len(paid)
    )