from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import certifi
import os
from bson import ObjectId
from bs4 import BeautifulSoup
from collections import defaultdict

import os
from os.path import join, dirname
from dotenv import load_dotenv

ca = certifi.where()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
app = Flask(__name__)

# Utility functions
def format_price(value):
    return f"{value:,.0f}"

app.jinja_env.filters['format_price'] = format_price
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"
SECRET_KEY = os.getenv("SECRET_KEY", "SPARTA")  # Ideally load this from an environment variable
TOKEN_KEY = "mytoken"
articles_per_page = 3

@app.route('/api/chart-data', methods=['GET'])
def chart_data():
    # Fetch user registration data
    user_data = db.user.find({}, {"registration_date": 1})
    user_count_per_month = defaultdict(int)
    
    for user in user_data:
        # Check if 'registration_date' exists in the document
        if 'registration_date' in user:
            reg_date = datetime.strptime(user['registration_date'], "%Y-%m-%d")
            month_year = reg_date.strftime("%Y-%m")
            user_count_per_month[month_year] += 1

    # Fetch total purchases per month
    order_data = db.orders.find({}, {"order_date": 1, "total_checkout": 1})
    purchase_count_per_month = defaultdict(int)

    for order in order_data:
        # Check if 'order_date' exists in the document
        if 'order_date' in order:
            order_date = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
            month_year = order_date.strftime("%Y-%m")
            purchase_count_per_month[month_year] += order["total_checkout"]

    # Fetch total number of products sold per month
    product_count_per_month = defaultdict(int)

    for order in order_data:
        # Check if 'order_date' and 'items' exist in the document
        if 'order_date' in order and 'items' in order:
            order_date = datetime.strptime(order['order_date'], "%Y-%m-%d %H:%M:%S")
            month_year = order_date.strftime("%Y-%m")
            for item in order['items']:
                product_count_per_month[month_year] += item['quantity']

    return jsonify({
        "user_count_per_month": user_count_per_month,
        "purchase_count_per_month": purchase_count_per_month,
        "product_count_per_month": product_count_per_month
    })



def truncate_html(html, word_limit):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text().split()
    if len(text) > word_limit:
        truncated_text = ' '.join(text[:word_limit]) + '...'
        return truncated_text
    return html

def is_logged_in():
    token_receive = request.cookies.get(TOKEN_KEY)
    if not token_receive:
        return False
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        return True
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return False

def get_user_info():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({'username': payload.get('id')})
        return user_info
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return None

def is_admin(user_info):
    return user_info and user_info.get('level') == 1

# Routes
@app.route('/auth_login')
def auth_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        count_unread = db.notif.count_documents(
            {'to':payload['id'], 'from':{'$ne':payload['id']}, 'read': False})
        data_user = {
            'username': user_info['username'],
            'profilename': user_info['profile_name'],
            'level': user_info['level'],
            'profile_icon': user_info['profile_pic_real']
        }
        return jsonify({"result": "success", "data": data_user, "notif":count_unread})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<postcreator>')
def auth_login_detail(postcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == postcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<commentcreator>')
def auth_login_comment(commentcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == commentcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/login')
def page_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})

        print(user_info)

        return redirect(url_for("home", msg="Anda sudah login!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('login.html')


@app.route('/register/check_dup', methods=["POST"])
def check_dup():
    username_receive = request.form.get("username_give")
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route('/register', methods=["POST"])
def register():
    username_receive = request.form.get("username_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    emailcheck = bool(db.user.find_one({'email': email_receive}))

    data_user = {
        "username": username_receive,
        "email": email_receive,
        "password": password_receive,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_icon.png",
        "profile_info": "",
        "blocked": False,
        "level": 2
    }

    if emailcheck == False:
        db.user.insert_one(data_user)
        return jsonify({"result": "success", "data": email_receive})
    else:
        return jsonify({"result": "fail", "msg": 'Maaf, email yang anda gunakan sudah terdaftar!'})


@app.route('/login', methods=["POST"])
def login():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    result = db.user.find_one(
        {
            "email": email_receive,
            "password": password_receive,
        }
    )
 

    if result:
        data_user = {
        'profilename': result['profile_name'],
        'level': result['level']
        }
        if result['blocked'] == True:
            data_block = db.blocklist.find_one({'user':result['username']})
            data_user['reasonblock'] = data_block['reason']
            data_user['userblock'] = data_block['user']
            return jsonify(
            {
                "result": "fail",
                "data": data_user,
                "status":"block"
            }
            )
        else:
            payload = {
                "id": result['username'],
                # the token will be valid for 24 hours
                 "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify(
            {
                "result": "success",
                "token": token,
                "data": data_user,
            }
            )

    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Kami tidak dapat menemukan akun anda, silakan cek email dan password anda!",
                "status":"Not Found"
            }
        )

@app.route('/')
def index():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)
    
    if logged_in and is_admin_flag:
        return redirect(url_for('dashboard'))  # Redirect to admin dashboard if logged in as admin
    
    page = int(request.args.get('page', 1))
    start_index = (page - 1) * articles_per_page
    end_index = start_index + articles_per_page
    
    articles = list(db.articles.find().sort('tanggal_upload', -1).skip(start_index).limit(articles_per_page))
    for article in articles:
        article['keterangan_artikel_truncated'] = truncate_html(article['keterangan_artikel'], 10)
    total_articles = db.articles.count_documents({})
    total_pages = (total_articles + articles_per_page - 1) // articles_per_page

    for article in articles:
        if 'tanggal_upload' in article and isinstance(article['tanggal_upload'], str):
            article['tanggal_upload'] = datetime.strptime(article['tanggal_upload'], '%Y-%m-%d %H:%M:%S')

    product_list = db.product.find()
    return render_template("index.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list, articles=articles, page=page, total_pages=total_pages)

@app.route('/shop')
def shop():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)

    product_list = db.product.find()
    return render_template("shop.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list)

@app.route('/dashboard')
def dashboard():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        if(user_login['level'] == 1):
            return render_template('adminDashboard.html')
        else:
            return redirect(url_for("index", msg="Anda tidak diizinkan masuk halaman dashboard!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index", msg="Anda belum login!"))

@app.route('/addproduct', methods=['GET'])
def addproduct():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    return render_template("addProduct.html", user_info=user_info, is_admin=True, logged_in=True)

@app.route('/add_product', methods=['POST'])
def posting():
    name_receive = request.form.get('name_give')
    price_receive = int(request.form.get('price_give'))
    stock_receive = int(request.form.get('stock_give'))
    deskripsi_receive = request.form.get('deskripsi_give')
    kategori_receive = request.form.get('category_give')

    print(f"Received category: {kategori_receive}")  # Debugging line

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

    if 'file_give' in request.files:
        file = request.files.get('file_give')
        file_name = secure_filename(file.filename)
        picture_name = file_name.split(".")[0]
        ekstensi = file_name.split(".")[1]
        picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
        file_path = f'./static/product_pics/{picture_name}'
        file.save(file_path)
    else:
        picture_name = "default.jpg"

    if 'file_give2' in request.files:
        file2 = request.files.get('file_give2')
        file2_name = secure_filename(file2.filename)
        picture_name2 = file2_name.split(".")[0]
        ekstensi2 = file2_name.split(".")[1]
        picture_name2 = f"{picture_name2}[{name_receive}]-{mytime}.{ekstensi2}"
        file2_path = f'./static/product_pics/{picture_name2}'
        file2.save(file2_path)
    else:
        picture_name2 = "default2.jpg"

    if 'file_give3' in request.files:
        file3 = request.files.get('file_give3')
        file3_name = secure_filename(file3.filename)
        picture_name3 = file3_name.split(".")[0]
        ekstensi3 = file3_name.split(".")[1]
        picture_name3 = f"{picture_name3}[{name_receive}]-{mytime}.{ekstensi3}"
        file3_path = f'./static/product_pics/{picture_name3}'
        file3.save(file3_path)
    else:
        picture_name3 = "default3.jpg"

    if 'file_give4' in request.files:
        file4 = request.files.get('file_give4')
        file4_name = secure_filename(file4.filename)
        picture_name4 = file4_name.split(".")[0]
        ekstensi4 = file4_name.split(".")[1]
        picture_name4 = f"{picture_name4}[{name_receive}]-{mytime}.{ekstensi4}"
        file4_path = f'./static/product_pics/{picture_name4}'
        file4.save(file4_path)
    else:
        picture_name4 = "default4.jpg"

    doc = {
        'product_name': name_receive,
        'product_price': price_receive,
        'product_stock': stock_receive,
        'kategori': kategori_receive,
        'image': picture_name,
        'image2': picture_name2,
        'image3': picture_name3,
        'image4': picture_name4,
        'description': deskripsi_receive,
    }
    db.product.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': 'Product added!'
    })

@app.route('/editproduct/<id_product>', methods=['GET'])
def editproduct(id_product):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    info_product = db.product.find_one({'_id': ObjectId(id_product)})
    return render_template("editProduct.html", info_product=info_product)

@app.route('/edit_product/<id_product>', methods=['PUT'])
def edit(id_product):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    name_receive = request.form.get('name_give')
    price_receive = int(request.form.get('price_give'))
    stock_receive = int(request.form.get('stock_give'))
    deskripsi_receive = request.form.get('deskripsi_give')

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

    if 'file_give' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama = data_lama['image']
        if gambar_lama != "default.jpg":
            os.remove(f'./static/product_pics/{gambar_lama}')

        file = request.files.get('file_give')
        file_name = secure_filename(file.filename)
        picture_name = file_name.split(".")[0]
        ekstensi = file_name.split(".")[1]
        picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
        file_path = f'./static/product_pics/{picture_name}'
        file.save(file_path)

        doc = {
            'product_name': name_receive,
            'product_price': price_receive,
            'product_stock': stock_receive,
            'image': picture_name,
            'description': deskripsi_receive,
        }

    else:
        doc = {
            'product_name': name_receive,
            'product_price': price_receive,
            'product_stock': stock_receive,
            'description': deskripsi_receive,
        }

    if 'file_give2' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama2 = data_lama.get('image2', 'default2.jpg')
        if gambar_lama2 != "default2.jpg":
            os.remove(f'./static/product_pics/{gambar_lama2}')

        file2 = request.files.get('file_give2')
        file2_name = secure_filename(file2.filename)
        picture_name2 = file2_name.split(".")[0]
        ekstensi2 = file2_name.split(".")[1]
        picture_name2 = f"{picture_name2}[{name_receive}]-{mytime}.{ekstensi2}"
        file2_path = f'./static/product_pics/{picture_name2}'
        file2.save(file2_path)

        doc['image2'] = picture_name2
    
    if 'file_give3' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama3 = data_lama.get('image3', 'default3.jpg')
        if gambar_lama3 != "default3.jpg":
            os.remove(f'./static/product_pics/{gambar_lama3}')

        file3 = request.files.get('file_give3')
        file3_name = secure_filename(file3.filename)
        picture_name3 = file3_name.split(".")[0]
        ekstensi3 = file3_name.split(".")[1]
        picture_name3 = f"{picture_name3}[{name_receive}]-{mytime}.{ekstensi3}"
        file3_path = f'./static/product_pics/{picture_name3}'
        file3.save(file3_path)

        doc['image3'] = picture_name3

    if 'file_give4' in request.files:
        data_lama = db.product.find_one({'_id': ObjectId(id_product)})
        gambar_lama4 = data_lama.get('image4', 'default4.jpg')
        if gambar_lama4 != "default4.jpg":
            os.remove(f'./static/product_pics/{gambar_lama4}')

        file4 = request.files.get('file_give4')
        file4_name = secure_filename(file4.filename)
        picture_name4 = file4_name.split(".")[0]
        ekstensi4 = file4_name.split(".")[1]
        picture_name4 = f"{picture_name4}[{name_receive}]-{mytime}.{ekstensi4}"
        file4_path = f'./static/product_pics/{picture_name4}'
        file4.save(file4_path)

        doc['image4'] = picture_name4

    db.product.update_one({'_id': ObjectId(id_product)}, {'$set': doc})
    return jsonify({
        'result': 'success',
        'msg': 'Product updated'
    })

@app.route('/manageproduct', methods=['GET'])
def manageproduct():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    product_list = db.product.find()
    return render_template("manageProduct.html", user_info=user_info, is_admin=True, logged_in=True, product_list=product_list)

@app.route('/delete_product/<string:id_delete>', methods=['DELETE'])
def delete_product(id_delete):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    try:
        info_product = db.product.find_one({'_id': ObjectId(id_delete)})
        image = info_product['image']
        if image != "default.jpg":
            os.remove(f'./static/product_pics/{image}')

        db.product.delete_one({'_id': ObjectId(id_delete)})
        return jsonify({'result': 'success', 'msg': 'Product Deleted'})
    except Exception as e:
        return jsonify({'result': 'fail', 'msg': str(e)})



@app.route('/detail/<id_product>', methods=['GET'])
def detail(id_product):
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)

    info_product = db.product.find_one({'_id': ObjectId(id_product)})


    return render_template("detail.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, info_product=info_product)


@app.route('/cart')
def cart():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False
    cart_items = []

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"
            # Fetch the cart items for the logged-in user
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_payment = sum(item["product_price"] * item["quantity"] for item in cart_items)
    return render_template("cart.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, cart_items=cart_items, total_payment=total_payment)

@app.route('/checkout')
def checkout():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False
    cart_items = []

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"
            # Fetch the cart items for the logged-in user
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_checkout = sum(item["product_price"] * item["quantity"] for item in cart_items)
    return render_template("checkout.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, cart_items=cart_items, total_checkout=total_checkout)


@app.route('/place_order', methods=['POST'])
def place_order():
    from datetime import datetime
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            # Get the form data
            full_name = request.form.get("full-name")
            telephone = request.form.get("telephone")
            address = request.form.get("address")
            city = request.form.get("city")
            country = request.form.get("country")
            postcode = request.form.get("postcode")

            # Get the cart items
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_checkout = sum(item["product_price"] * item["quantity"] for item in cart_items)

            # Add shipping cost if necessary

            today = datetime.now()
            mytime = today.strftime("%Y-%m-%d %H:%M:%S")

            # Create order document
            order = {
                "user_id": user_info["_id"],
                "full_name": full_name,
                "telephone": telephone,
                "address": address,
                "city": city,
                "country": country,
                "postcode": postcode,
                "items": cart_items,
                "total_checkout": total_checkout,
                "order_date": mytime,
                "status": "Menunggu Pembayaran"
            }

            # Insert the order into the database
            db.orders.insert_one(order)

            # Clear the cart
            db.cart.delete_many({"user_id": user_info["_id"]})

            # Update the product stock
            for item in cart_items:
                db.product.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {"$inc": {"product_stock": -item["quantity"]}}
                )

            # Update the user's transaction count (jumlah_transaksi)
            db.user.update_one(
                {"_id": user_info["_id"]},
                {"$inc": {"jumlah_pembelian": 1}}
            )

            return redirect(url_for("orders"))
        else:
            return redirect(url_for("login"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))



@app.route('/orders')
def orders():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False
    orders = []

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"
            # Fetch the orders for the logged-in user
            orders_cursor = db.orders.find({"user_id": user_info["_id"]})
            orders = list(orders_cursor)  # Convert cursor to a list
    return render_template("orders.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, orders=orders)

@app.route('/manageorder', methods=['GET'])
def manage_order_get():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    
    orders = list(db.orders.find())
    return render_template('manage_order.html', orders=orders, user_info=user_info, is_admin=True, logged_in=True)

@app.route('/update_order_status/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    new_status = request.form.get('status_give')
    if new_status:
        result = db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": new_status}})
        if result.modified_count > 0:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail", "msg": "Order not found or status unchanged."})
    return jsonify({"result": "fail", "msg": "No status provided."})

@app.route('/delete_order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    # Allow deletion regardless of the order status
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count > 0:
        return jsonify({"result": "success"})
    return jsonify({"result": "fail", "msg": "Order not found."})


@app.route('/confirm_msg', methods=["POST"])
def confirm_msg():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        id_receive = request.form["id_give"]
        type_receive = request.form["type_give"]
        data = db.saran.find_one({'_id': ObjectId(id_receive)})
        print(data)
        if type_receive == 'show':
            db.saran.update_one({"_id": ObjectId(id_receive)}, {
                            "$set": {'show': True}})
        elif type_receive == 'delete':
            db.saran.delete_one({'_id': ObjectId(id_receive)})
        return jsonify({"result": "success", "msg": "Post updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("admin_dashboard"))

@app.route('/api/cart/mine/items', methods=['POST'])
def add_to_cart():
    from datetime import datetime
    token_receive = request.cookies.get("mytoken")
    if not token_receive:
        return redirect(url_for('login'))

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            product_id = request.form.get('product_id')
            product_name = request.form.get('product_name')
            product_price = int(request.form.get('product_price'))
            product_image = request.form.get('product_image')
            qty = int(request.form.get('qty'))

            # Get the product from the database
            product = db.product.find_one({"_id": ObjectId(product_id)})

            if not product:
                return jsonify({"result": "fail", "msg": "Product not found"})
            
            # Calculate the total quantity in the cart for this product
            existing_cart_item = db.cart.find_one({
                "user_id": user_info["_id"],
                "product_id": product_id
            })
            if existing_cart_item:
                new_qty = existing_cart_item["quantity"] + qty
            else:
                new_qty = qty

            # Check if the requested quantity exceeds the available stock
            if new_qty > product["product_stock"]:
                return jsonify({"result": "fail", "msg": "Quantity exceeds available stock"})

            today = datetime.now()
            mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

            if existing_cart_item:
                # Update the quantity of the existing product in the cart
                db.cart.update_one(
                    {"_id": existing_cart_item["_id"]},
                    {"$set": {"quantity": new_qty, "timestamp": mytime}}
                )
            else:
                # Add the new product to the cart
                db.cart.insert_one({
                    "user_id": user_info["_id"],
                    "product_id": product_id,
                    "product_name": product_name,
                    "product_price": product_price,
                    "product_image": product_image,
                    "quantity": qty,
                    "timestamp": mytime
                })
            return redirect(url_for('cart'))
        else:
            return jsonify({"result": "fail", "msg": "User not found"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token invalid"})

@app.route('/delete_cart_item/<string:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            db.cart.delete_one({"_id": ObjectId(item_id), "user_id": user_info["_id"]})
            return jsonify({"result": "success", "msg": "Item deleted from cart"})
        else:
            return jsonify({"result": "fail", "msg": "User not found"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token invalid"})
    
@app.route('/search', methods=['GET'])
def search():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    query = request.args.get('q')
    product_list = db.product.find({"product_name": {"$regex": query, "$options": "i"}})

    return render_template("shop.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, product_list=product_list, query=query)
    
@app.route('/about')
def about():
    token_receive = request.cookies.get("mytoken")
    data = list(db.saran.find({}))
    print(data)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        return render_template('about.html', user_login=user_login, datasaran=data)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('about.html', datasaran=data)

@app.route('/post_saran', methods=['POST'])
def post_saran():
    username_receive = request.form['username_give']
    message_receive = request.form['message_give']
    time = datetime.now().strftime("%m%d%H%M%S")
    doc= {
        'msgid': f'msgid-{username_receive}-{time}',
        'username': username_receive,
        'message': message_receive,
        'show': False
    }
    db.saran.insert_one(doc)
    return jsonify({"result": "success", "msg": "Saran terkirim!"})

@app.route('/get_user')
def get_user():
    datauser = list(db.user.find({'level':2}))
    for data in datauser:
        data["_id"] = str(data["_id"])
        data['count_post'] = db.posts.count_documents(
            {"username": data['username']})
    return jsonify({"result": "success", "msg":"berhasil", "data": datauser})

@app.route('/get_pesan')
def get_pesan():
    datapesan = list(db.saran.find({}))
    for data in datapesan:
        data["_id"] = str(data["_id"])

    return jsonify({"result": "success", "msg":"berhasil", "data": datapesan})

@app.route('/contact')
def contact():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    return render_template("contact.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in)

@app.route('/mark_as_best_product/<product_id>', methods=['POST'])
def mark_as_best_product(product_id):
    try:
        result = db.product.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'is_best_product': True}}
        )
        if result.modified_count > 0:
            return jsonify({'result': 'success', 'msg': 'Product marked as Best Product!'})
        else:
            return jsonify({'result': 'failure', 'msg': 'Product not found or already marked as Best Product.'})
    except Exception as e:
        return jsonify({'result': 'error', 'msg': str(e)})

@app.route('/remove_best_product/<product_id>', methods=['POST'])
def remove_best_product(product_id):
    try:
        result = db.product.update_one(
            {'_id': ObjectId(product_id)},
            {'$unset': {'is_best_product': ""}}
        )
        if result.modified_count > 0:
            return jsonify({'result': 'success', 'msg': 'Best Product status removed!'})
        else:
            return jsonify({'result': 'failure', 'msg': 'Product not found or not marked as Best Product.'})
    except Exception as e:
        return jsonify({'result': 'error', 'msg': str(e)})
    
@app.route('/manageuser', methods=['GET'])
def manage_user():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    users = list(db.user.find())
    for user in users:
        print(user)  # Debug print to check the content of each user

    return render_template("manageUser.html", users=users, user_info=user_info, is_admin=True, logged_in=True)


@app.route('/edit_user/<username>', methods=['GET'])
def edit_user(username):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    user = db.user.find_one({"username": username})
    return render_template("editUser.html", user=user, user_info=user_info, is_admin=True, logged_in=True)

@app.route('/update_user/<username>', methods=['POST'])
def update_user(username):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    new_role = request.form.get('role_give')

    result = db.user.update_one(
        {"username": username},
        {"$set": {"role": new_role}}
    )

    if result.modified_count > 0:
        return jsonify({'result': 'success', 'msg': 'User updated successfully'})
    else:
        return jsonify({'result': 'fail', 'msg': 'User not found or no changes made'})

@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return jsonify({'result': 'fail', 'msg': 'Access denied'})

    try:
        result = db.user.delete_one({"username": username})
        if result.deleted_count > 0:
            return jsonify({'result': 'success', 'msg': 'User deleted successfully'})
        else:
            return jsonify({'result': 'fail', 'msg': 'User not found'})
    except Exception as e:
        return jsonify({'result': 'fail', 'msg': str(e)})
    
@app.route('/blockuser', methods=['POST'])
def blockuser():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        username_receive = request.form["username_give"]
        reason_receive = request.form["reason_give"]
        date_receive = request.form["date_give"]

        doc = {
            'from': username,
            'user': username_receive,
            'reason': reason_receive,
            'date': date_receive,
        }

        db.blocklist.insert_one(doc)
        db.user.update_one({"username": username_receive}, {"$set": {'blocked':True}})

        print(doc)
        return jsonify({"result": "success", "msg": "User blocked!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("dashboard"))

@app.route('/unblockuser', methods=['POST'])
def unblockuser():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        username_receive = request.form["username_give"]

        db.blocklist.delete_one({
            'user': username_receive,
        })

        db.user.update_one({"username": username_receive}, {"$set": {'blocked':False}})

        return jsonify({"result": "success", "msg": "User unblocked!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("dashboard"))
    
@app.route('/tambah_artikel', methods=['POST'])
def tambah_artikel():
    from datetime import datetime
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    nama_receive = request.form.get('nama_give')
    keterangan_gambar_receive = request.form.get('keterangan_gambar')
    keterangan_artikel_receive = request.form.get('keterangan_artikel')
    link_receive = request.form.get('link_give')

    # Get the current date and time
    current_date = datetime.now()

    if 'gambar_artikel' in request.files:
        file = request.files.get('gambar_artikel')
        file_name = secure_filename(file.filename)
        picture_name = f"{file_name.split('.')[0]}[{nama_receive}].{file_name.split('.')[1]}"
        file_path = f'./static/img_artikel/{picture_name}'
        file.save(file_path)
    else:
        picture_name = 'default.jpg'

    doc = {
        'nama_artikel': nama_receive,
        'keterangan_gambar': keterangan_gambar_receive,
        'keterangan_artikel': keterangan_artikel_receive,
        'gambar_artikel': picture_name,
        'tanggal_upload': current_date,
        'link' : link_receive,
    }
    db.articles.insert_one(doc)

    return redirect(url_for('artikel'))

@app.route('/artikel')
def artikel():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    
    articles = list(db.articles.find().sort('_id', -1))
    return render_template('artikel.html', articles=articles)

# Route for updating an article
@app.route('/update_artikel/<article_id>', methods=['POST'])
def update_artikel(article_id):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    # Retrieve the existing article
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        # Get the updated data from the form
        nama_receive = request.form.get('nama_give')
        keterangan_gambar_receive = request.form.get('keterangan_gambar')
        keterangan_artikel_receive = request.form.get('keterangan_artikel')
        link_receive = request.form.get('link_give')

        if 'gambar_artikel' in request.files:
            file = request.files.get('gambar_artikel')
            file_name = secure_filename(file.filename)
            picture_name = f"{file_name.split('.')[0]}[{nama_receive}].{file_name.split('.')[1]}"
            file_path = f'./static/img_artikel/{picture_name}'
            file.save(file_path)
        else:
            picture_name = article['gambar_artikel']

        # Update the article in the database
        db.articles.update_one(
            {'_id': ObjectId(article_id)},
            {
                '$set': {
                    'nama_artikel': nama_receive,
                    'keterangan_gambar': keterangan_gambar_receive,
                    'keterangan_artikel': keterangan_artikel_receive,
                    'gambar_artikel': picture_name,
                    'link' : link_receive
                }
            }
        )

        return redirect(url_for('artikel'))
    else:
        return "Artikel tidak ditemukan."

@app.route('/hapus_artikel/<article_id>', methods=['GET'])
def hapus_artikel(article_id):
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))
    
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        db.articles.delete_one({'_id': ObjectId(article_id)})

        image_path = os.path.join("static", "img_artikel", article['gambar_artikel'])
        if os.path.exists(image_path):
            os.remove(image_path)

        return redirect(url_for('artikel'))
    else:
        return "Artikel tidak ditemukan."

@app.route('/artikel/<article_id>')
def artikel_detail(article_id):
    article = db.articles.find_one({'_id': ObjectId(article_id)})

    if article:
        return render_template('detail_artikel.html', article=article)
    else:
        return "Artikel tidak ditemukan."
    
@app.route('/user/<username>')
def user(username):
    user_info = db.user.find_one(
        {"username": username},
        {"_id": False}
    )
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        print(user_login)
        if user_info['username'] == user_login['username']:
            return render_template("user-profile.html", user_info=user_info, user_login=user_login)
        else:
            return render_template("user-profile.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("user-profile.html", user_info=user_info)

@app.route("/update_profile", methods=["POST"])
def update_profile():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        fullname_receive = request.form["fullname_give"]
        email_receive = request.form["email_give"]
        job_receive = request.form["job_give"]
        phone_receive = request.form["phone_give"]
        address_receive = request.form["address_give"]
        bio_receive = request.form["bio_give"]
        new_doc = {
            "profile_name": fullname_receive,
            "email": email_receive,
            "profile_job": job_receive,
            "profile_phone": phone_receive,
            "profile_address": address_receive,
            "profile_info": bio_receive
        }
        if "file_give" in request.files:
            time = datetime.now().strftime("%m%d%H%M%S")
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/profilimg-{username}-{time}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.user.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))

@app.route("/reset_pass", methods=["POST"])
def reset_pass():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username_receive = request.form["username_give"]
        if username_receive == payload['id']:
            password_receive = request.form["passnew_give"]
            db.user.update_one({"username": payload["id"]}, {"$set": {'password':password_receive}})

        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))

    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
