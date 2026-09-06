import streamlit as st
from supabase import create_client

# ---------------- CONFIG ----------------

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

if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- HELPERS ----------------

def money(n):
    return f"₦{float(n):,.2f}"


def user():
    try:
        return sb.auth.get_user().user
    except:
        return None


def products():
    try:
        return sb.table("products").select("*").execute().data or []
    except:
        return []


def owner():
    u = user()
    if not u:
        return False

    try:
        p = sb.table("profiles").select("role").eq(
            "id", u.id
        ).maybe_single().execute().data

        return p and p.get("role") == "owner"
    except:
        return False


# ---------------- AUTH ----------------

u = user()

if not u:

    st.title("🛍️ Veyra")

    login, signup = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    with login:

        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login", use_container_width=True):

            try:
                r = sb.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if r.user:
                    st.rerun()

            except Exception as e:
                st.error(str(e))


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

            if password != confirm:
                st.error("Passwords do not match.")

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
                        "Account created!"
                    )

                    st.info(
                        "Check your email to confirm your account."
                    )

                except Exception as e:
                    st.error(str(e))

    st.stop()


# ---------------- SIDEBAR ----------------

st.sidebar.title("🛍️ Veyra")

page = st.sidebar.radio(
    "Menu",
    [
        "Store",
        "Cart",
        "My Orders"
    ]
    + (
        ["Owner Dashboard", "Analytics"]
        if owner()
        else []
    )
)

st.sidebar.write(
    f"🛒 Cart: {sum(x['quantity'] for x in st.session_state.cart.values())}"
)

if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    sb.auth.sign_out()
    st.session_state.cart = {}
    st.rerun()


# ---------------- STORE ----------------

if page == "Store":

    st.title("🛍️ Veyra Store")

    data = products()

    search = st.text_input(
        "🔎 Search"
    ).lower()

    categories = sorted(
        set(
            x.get("category")
            for x in data
            if x.get("category")
        )
    )

    category = st.selectbox(
        "Category",
        ["All"] + categories
    )

    data = [
        x for x in data
        if (
            not search
            or search in x.get("name", "").lower()
            or search in x.get("description", "").lower()
        )
        and (
            category == "All"
            or x.get("category") == category
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

            st.subheader(p["name"])

            st.write(
                p.get("description", "")
            )

            st.write(
                f"### {money(p['price'])}"
            )

            if st.button(
                "🛒 Add",
                key=f"add{p['id']}",
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

    st.title("🛒 Cart")

    cart = st.session_state.cart

    if not cart:
        st.info("Your cart is empty.")
    else:

        total = 0

        for pid, item in list(cart.items()):

            col1, col2, col3 = st.columns(
                [4, 1, 1]
            )

            with col1:
                st.write(
                    f"**{item['name']}**"
                )
                st.write(
                    money(item["price"])
                )

            with col2:
                st.write(
                    f"Qty: {item['quantity']}"
                )

            with col3:

                if st.button(
                    "➖",
                    key=f"remove{pid}"
                ):

                    item["quantity"] -= 1

                    if item["quantity"] <= 0:
                        del cart[pid]

                    st.rerun()

            total += (
                item["price"]
                * item["quantity"]
            )

        st.divider()

        st.subheader(
            f"Total: {money(total)}"
        )

        if st.button(
            "📦 Place Order",
            type="primary",
            use_container_width=True
        ):

            try:

                order = sb.table("orders").insert({
                    "user_id": u.id,
                    "total": total,
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
                    for x in cart.values()
                ]

                sb.table("order_items").insert(
                    items
                ).execute()

                st.session_state.cart = {}

                st.success(
                    "Order created!"
                )

                st.info(
                    "Payment will be added next."
                )

                st.rerun()

            except Exception as e:
                st.error(str(e))


# ---------------- ORDERS ----------------

elif page == "My Orders":

    st.title("📦 My Orders")

    orders = sb.table("orders").select("*").eq(
        "user_id",
        u.id
    ).order(
        "created_at",
        desc=True
    ).execute().data or []

    if not orders:
        st.info("No orders yet.")

    for o in orders:

        with st.expander(
            f"Order #{o['id']}"
        ):

            st.write(
                f"Total: {money(o['total'])}"
            )

            st.write(
                f"Status: {o['status']}"
            )

            st.write(
                f"Payment: {o['payment_status']}"
            )


# ---------------- OWNER ----------------

elif page == "Owner Dashboard":

    st.title("👑 Owner Dashboard")

    with st.form("product"):

        name = st.text_input("Product name")
        description = st.text_area("Description")
        price = st.number_input(
            "Price",
            min_value=0.0
        )
        category = st.text_input("Category")
        image = st.text_input("Image URL")
        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1
        )

        add = st.form_submit_button(
            "Add Product"
        )

    if add:

        try:

            sb.table("products").insert({
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "image_url": image,
                "stock": stock
            }).execute()

            st.success(
                "Product added!"
            )

            st.rerun()

        except Exception as e:
            st.error(str(e))


# ---------------- ANALYTICS ----------------

elif page == "Analytics":

    st.title("📊 Sales Analytics")

    orders = sb.table("orders").select(
        "total,payment_status"
    ).execute().data or []

    paid = [
        x for x in orders
        if x["payment_status"] == "paid"
    ]

    revenue = sum(
        float(x["total"])
        for x in paid
    )

    a, b, c = st.columns(3)

    a.metric(
        "Revenue",
        money(revenue)
    )

    b.metric(
        "Orders",
        len(orders)
    )

    c.metric(
        "Paid Orders",
        len(paid)
    )