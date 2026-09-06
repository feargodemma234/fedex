import streamlit as st
from supabase import create_client
import uuid
import urllib.parse

st.set_page_config(page_title="My Store", page_icon="🛒", layout="wide")

# ---------------- CONFIG ----------------
sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
STORE_EMAIL = st.secrets["STORE_EMAIL"]
ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"]

if "cart" not in st.session_state: st.session_state.cart = []
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "Home"

# ---------------- AUTH ----------------
def login():
    st.title("🛒 My Store")
    a,b = st.tabs(["Login","Create Account"])

    with a:
        e = st.text_input("Email", key="le")
        p = st.text_input("Password", type="password", key="lp")
        if st.button("Login"):
            try:
                r = sb.auth.sign_in_with_password({"email":e,"password":p})
                st.session_state.user = r.user
                st.rerun()
            except Exception as x: st.error(str(x))

    with b:
        n = st.text_input("Full name", key="sn")
        e = st.text_input("Email", key="se")
        p = st.text_input("Password", type="password", key="sp")
        if st.button("Create Account"):
            if len(p)<6: st.warning("Password must be at least 6 characters.")
            else:
                try:
                    sb.auth.sign_up({"email":e,"password":p,
                        "options":{"data":{"full_name":n}}})
                    st.success("Check your email to confirm your account.")
                except Exception as x: st.error(str(x))

if not st.session_state.user:
    try: st.session_state.user = sb.auth.get_user().user
    except: pass

if not st.session_state.user:
    login()
    st.stop()

USER = st.session_state.user
UID = str(USER.id)

# ---------------- PRODUCTS ----------------
def products():
    try:
        r = sb.table("products").select("*").execute()
        data = r.data or []

        # Add products automatically if database is empty
        if not data:
            samples = [
                {"id":str(uuid.uuid4()),"name":"Wireless Headphones",
                 "description":"Quality wireless headphones","price":25000,
                 "category":"Electronics","image_url":""},
                {"id":str(uuid.uuid4()),"name":"Smart Watch",
                 "description":"Modern smart watch","price":35000,
                 "category":"Electronics","image_url":""},
                {"id":str(uuid.uuid4()),"name":"Backpack",
                 "description":"Strong everyday backpack","price":18000,
                 "category":"Fashion","image_url":""},
                {"id":str(uuid.uuid4()),"name":"Sneakers",
                 "description":"Comfortable everyday sneakers","price":30000,
                 "category":"Fashion","image_url":""}
            ]
            sb.table("products").insert(samples).execute()
            data = samples
        return data
    except Exception as x:
        st.error("Could not load products.")
        st.code(str(x))
        return []

P = products()

# ---------------- CART ----------------
def add(p):
    for x in st.session_state.cart:
        if str(x["id"]) == str(p["id"]):
            x["quantity"] += 1
            return
    st.session_state.cart.append({
        "id":p["id"], "name":p["name"],
        "price":float(p["price"]), "quantity":1
    })

def total():
    return sum(x["price"]*x["quantity"] for x in st.session_state.cart)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🛒 My Store")
st.sidebar.write(USER.email)

for name in ["Home","Cart","Orders"]:
    if st.sidebar.button(name, use_container_width=True):
        st.session_state.page = name
        st.rerun()

if USER.email.lower() == ADMIN_EMAIL.lower():
    if st.sidebar.button("⚙️ Admin", use_container_width=True):
        st.session_state.page = "Admin"
        st.rerun()

if st.sidebar.button("Logout", use_container_width=True):
    sb.auth.sign_out()
    st.session_state.user = None
    st.session_state.cart = []
    st.rerun()

# ---------------- HOME ----------------
if st.session_state.page == "Home":
    st.title("🛍️ Products")
    search = st.text_input("🔎 Search")

    shown = [p for p in P if not search or
             search.lower() in p["name"].lower()]

    cols = st.columns(3)
    for i,p in enumerate(shown):
        with cols[i%3]:
            if p.get("image_url"): st.image(p["image_url"])
            st.subheader(p["name"])
            st.write(p.get("description",""))
            st.write(f"**₦{float(p['price']):,.2f}**")
            if st.button("🛒 Add to Cart", key="add"+str(p["id"])):
                add(p)
                st.success("Added!")

# ---------------- CART ----------------
elif st.session_state.page == "Cart":
    st.title("🛒 Cart")

    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        for x in st.session_state.cart:
            c1,c2,c3,c4 = st.columns([3,1,1,1])
            c1.write(f"**{x['name']}**")
            c2.write(f"₦{x['price']:,.2f}")
            c3.write(f"Qty: {x['quantity']}")
            if c4.button("❌",key="rm"+str(x["id"])):
                st.session_state.cart.remove(x)
                st.rerun()

        st.divider()
        st.subheader(f"Total: ₦{total():,.2f}")

        if st.button("Proceed to Checkout", type="primary"):
            st.session_state.page = "Checkout"
            st.rerun()

# ---------------- CHECKOUT ----------------
elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")

    if not st.session_state.cart:
        st.warning("Your cart is empty.")
        st.stop()

    st.subheader("Order Summary")
    for x in st.session_state.cart:
        st.write(
            f"**{x['name']}** × {x['quantity']} — "
            f"₦{x['price']*x['quantity']:,.2f}"
        )

    st.divider()
    st.subheader(f"Total: ₦{total():,.2f}")

    st.subheader("Your Information")
    name = st.text_input("Full name")
    phone = st.text_input("Phone number")
    address = st.text_area("Address")
    state = st.text_input("State")
    email = st.text_input("Email address", value=USER.email)

    if name and phone and address and state and email:
        st.success("Information complete.")

        method = st.radio(
            "Select payment method",
            ["Bank Transfer","Gift Card"]
        )

        st.subheader("Payment")

        if method == "Bank Transfer":
            st.info(
                "Bank Transfer\n\n"
                "Bank: YOUR BANK\n\n"
                "Account Name: YOUR STORE\n\n"
                "Account Number: 0000000000\n\n"
                "Replace these details with your real payment details."
            )
        else:
            st.info(
                "Gift Card\n\n"
                "Follow the store's gift-card payment instructions."
            )

        st.warning(
            "After making payment, tap the button below and "
            "attach your proof of payment in Gmail."
        )

        order_id = str(uuid.uuid4())

        subject = urllib.parse.quote(
            f"Payment Proof - Order {order_id}"
        )

        body = urllib.parse.quote(
            f"Hello,\n\n"
            f"I have completed payment for my order.\n\n"
            f"Order ID: {order_id}\n"
            f"Customer: {name}\n"
            f"Phone: {phone}\n"
            f"Payment method: {method}\n"
            f"Amount: ₦{total():,.2f}\n\n"
            f"Proof of payment is attached."
        )

        gmail = (
            f"https://mail.google.com/mail/?view=cm"
            f"&fs=1&to={STORE_EMAIL}"
            f"&su={subject}&body={body}"
        )

        st.link_button(
            "📧 Add Proof of Payment",
            gmail,
            use_container_width=True
        )

        if st.button("✅ Confirm Order", type="primary"):
            try:
                sb.table("orders").insert({
                    "id":order_id,
                    "user_id":UID,
                    "total_amount":total(),
                    "status":"Payment Pending",
                    "customer_name":name,
                    "phone":phone,
                    "address":f"{address}, {state}"
                }).execute()

                items = [{
                    "order_id":order_id,
                    "product_id":str(x["id"]),
                    "product_name":x["name"],
                    "quantity":x["quantity"],
                    "price":x["price"]
                } for x in st.session_state.cart]

                sb.table("order_items").insert(items).execute()

                st.session_state.cart = []
                st.success("🎉 Order created successfully!")
                st.info(f"Order ID: {order_id}")
                st.session_state.page = "Orders"

            except Exception as x:
                st.error("Could not create order.")
                st.code(str(x))
    else:
        st.info("Complete your name, phone, address, state and email to continue.")

# ---------------- ORDERS ----------------
elif st.session_state.page == "Orders":
    st.title("📦 My Orders")

    try:
        orders = sb.table("orders").select("*").eq(
            "user_id",UID
        ).execute().data or []

        if not orders:
            st.info("No orders yet.")

        for o in orders:
            with st.expander(
                f"Order {o['id']} — {o.get('status','Pending')}"
            ):
                st.write(f"**Total:** ₦{float(o['total_amount']):,.2f}")
                st.write(f"**Name:** {o.get('customer_name','')}")
                st.write(f"**Phone:** {o.get('phone','')}")
                st.write(f"**Address:** {o.get('address','')}")

                items = sb.table("order_items").select("*").eq(
                    "order_id",o["id"]
                ).execute().data or []

                st.write("### Products")
                for x in items:
                    st.write(
                        f"🛍️ **{x.get('product_name','Product')}** "
                        f"× {x.get('quantity',1)} — "
                        f"₦{float(x.get('price',0)):,.2f}"
                    )

    except Exception as x:
        st.error(str(x))

# ---------------- ADMIN ----------------
elif st.session_state.page == "Admin":
    if USER.email.lower() != ADMIN_EMAIL.lower():
        st.error("Admin access denied.")
        st.stop()

    st.title("⚙️ Admin Dashboard")

    tab1,tab2 = st.tabs(["Products","Orders"])

    with tab1:
        st.subheader("➕ Add Product")

        with st.form("newproduct"):
            n = st.text_input("Product name")
            d = st.text_area("Description")
            pr = st.number_input("Price",min_value=0.0)
            cat = st.text_input("Category")
            img = st.text_input("Image URL")

            if st.form_submit_button("Add Product"):
                try:
                    sb.table("products").insert({
                        "id":str(uuid.uuid4()),
                        "name":n,
                        "description":d,
                        "price":pr,
                        "category":cat or "Other",
                        "image_url":img
                    }).execute()
                    st.success("Product added!")
                    st.rerun()
                except Exception as x:
                    st.error(str(x))

        st.divider()
        st.subheader("Current Products")

        for p in products():
            st.write(
                f"**{p['name']}** — "
                f"₦{float(p['price']):,.2f}"
            )

    with tab2:
        st.subheader("Customer Orders")

        try:
            orders = sb.table("orders").select("*").execute().data or []

            for o in orders:
                with st.expander(
                    f"{o.get('customer_name','Customer')} — "
                    f"₦{float(o.get('total_amount',0)):,.2f}"
                ):
                    st.write(f"Order ID: {o['id']}")
                    st.write(f"Email: {o.get('email','Not stored')}")
                    st.write(f"Phone: {o.get('phone','')}")
                    st.write(f"Address: {o.get('address','')}")
                    st.write(f"Status: {o.get('status','Pending')}")

                    items = sb.table("order_items").select("*").eq(
                        "order_id",o["id"]
                    ).execute().data or []

                    st.write("### Products ordered")
                    for x in items:
                        st.write(
                            f"🛍️ {x.get('product_name','Product')} "
                            f"× {x.get('quantity',1)}"
                        )

                    status = st.selectbox(
                        "Update status",
                        ["Payment Pending","Processing",
                         "Shipped","Delivered","Cancelled"],
                        key="status"+str(o["id"])
                    )

                    if st.button("Update",key="upd"+str(o["id"])):
                        sb.table("orders").update(
                            {"status":status}
                        ).eq("id",o["id"]).execute()
                        st.success("Updated!")
                        st.rerun()

        except Exception as x:
            st.error(str(x))