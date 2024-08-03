from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import ObjectId
import hashlib
import datetime
import jwt
import os

client = MongoClient('mongodb+srv://test:sparta@cluster0.evhvrqa.mongodb.net/?retryWrites=true&w=majority')
db = client.dbams
app = Flask(__name__)

def format_price(value):
    return f"{value:,.0f}"

app.jinja_env.filters['format_price'] = format_price

SECRET_KEY = 'SPARTA'

def is_logged_in():
    token_receive = request.cookies.get("mytoken")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False
    return False

def get_user_info():
    token_receive = request.cookies.get("mytoken")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            return user_info
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return None
    return None

def is_admin(user_info):
    return user_info and user_info.get("role") == "admin"

@app.route('/register')
def register():
    if is_logged_in():
        return redirect('/')
    return render_template("register.html")

@app.route('/login')
def login():
    if is_logged_in():
        user_info = get_user_info()
        if is_admin(user_info):
            return redirect(url_for('dashboard'))
        return redirect('/')
    return render_template("login.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    username_receive = request.form["username_give"]

    existing_user = db.user.find_one({"username": username_receive})
    if existing_user:
        msg = f"An account with id {username_receive} already exists!"
        return jsonify({"result": "failure", "msg": msg})

    password_receive = request.form["password_give"]
    role_receive = request.form.get("role_give")

    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    db.user.insert_one({
        "username": username_receive, 
        "password": password_hash, 
        "role": role_receive
    })

    return jsonify({"result": "success"})

@app.route("/api/login", methods=["POST"])
def api_login():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    result = db.user.find_one({
        "username": username_receive, 
        "password": pw_hash
    }, {"role": 1})

    if result:
        role_user = result.get("role", None)

        payload = {
            "id": username_receive,
            "role": role_user,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60),
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        if role_user == "admin":
            return jsonify({
                "result": "success",
                "token": token,
                "redirect": url_for('dashboard')  # Redirect to admin dashboard
            })
        else:
            return jsonify({
                "result": "success",
                "token": token
            })
    else:
        return jsonify({
            "result": "fail", 
            "msg": "your username or password is incorrect"
        })

@app.route('/logout')
def logout():
    response = redirect('/')
    response.set_cookie('mytoken', expires=0)
    return response

@app.route('/')
def index():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)
    
    if logged_in and is_admin_flag:
        return redirect(url_for('dashboard'))  # Redirect to admin dashboard if logged in as admin

    product_list = db.product.find()
    return render_template("index.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list)

@app.route('/shop')
def shop():
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)

    product_list = db.product.find()
    return render_template("shop.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, product_list=product_list)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    user_info = get_user_info()
    if not user_info or not is_admin(user_info):
        return redirect(url_for("index"))

    return render_template("adminDashboard.html", user_info=user_info, is_admin=True, logged_in=True)

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

    today = datetime.datetime.now()
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

    doc = {
        'product_name': name_receive,
        'product_price': price_receive,
        'product_stock': stock_receive,
        'image': picture_name,
        'image2': picture_name2,
        'description': deskripsi_receive,
        'like_counts': 0
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

    today = datetime.datetime.now()
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

@app.route("/update_like", methods=["POST"])
def update_like():
    id_receive = request.form.get('id_give')
    like_receive = int(request.form.get('like_give'))

    db.product.update_one({'_id': ObjectId(id_receive)}, {'$set': {'like_counts': like_receive}})
    return jsonify({'result': 'success', 'msg': 'Like updated'})

@app.route('/detail/<id_product>', methods=['GET'])
def detail(id_product):
    logged_in = is_logged_in()
    user_info = get_user_info()
    is_admin_flag = is_admin(user_info)
    testimonials = db.testimonial.find({"product_id": ObjectId(id_product)})  # Fetch testimonials for the specific product

    info_product = db.product.find_one({'_id': ObjectId(id_product)})

    return render_template("detail.html", user_info=user_info, is_admin=is_admin_flag, logged_in=logged_in, info_product=info_product, testimonials=testimonials)

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
            shipping_method = request.form.get("shipping-method")
            card_name = request.form.get("card-name")
            card_number = request.form.get("card-number")
            expiry_date = request.form.get("expiry-date")
            cvv = request.form.get("cvv")

            # Get the cart items
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_checkout = sum(item["product_price"] * item["quantity"] for item in cart_items)

            # Add shipping cost
            if shipping_method == "Regular":
                total_checkout += 50000
            elif shipping_method == "Express":
                total_checkout += 100000

            today = datetime.now()
            mytime = today.strftime("%Y-%m-%d %H-%M-%S")


            # Create order document
            order = {
                "user_id": user_info["_id"],
                "full_name": full_name,
                "telephone": telephone,
                "address": address,
                "city": city,
                "country": country,
                "postcode": postcode,
                "shipping_method": shipping_method,
                "payment_info": {
                    "card_name": card_name,
                    "card_number": card_number,
                    "expiry_date": expiry_date,
                    "cvv": cvv
                },
                "items": cart_items,
                "total_checkout": total_checkout,
                "order_date": mytime,
                "status": "In Progress"
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
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                is_admin = user_info.get("role") == "admin"
                logged_in = True
                role = user_info.get("role")
            else:
                is_admin = False
                logged_in = False
        else:
            user_info = None
            is_admin = False
            logged_in = False

        if not logged_in:
            return jsonify({"result": "failure", "msg": "User not logged in"}), 403

        if role not in ["admin"]:
            return jsonify({"result": "failure", "msg": "User not authorized"}), 403

        status_give = request.form.get("status_give")
        if ObjectId.is_valid(order_id):
            db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": status_give}}
            )
            return jsonify({"result": "success", "msg": "Order status updated"})
        else:
            return jsonify({"result": "failure", "msg": "Invalid order ID"}), 400

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

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

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    query = request.args.get('q')
    product_list = db.product.find({"product_name": {"$regex": query, "$options": "i"}})

    return render_template("shop.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, product_list=product_list, query=query)

@app.route('/add_testimonial', methods=['POST'])
def add_testimonial():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        testimonial_receive = request.form["testimonial"]
        product_id = request.form["product_id"]  # Retrieve product_id from form

        db.testimonial.insert_one({
            "user_id": payload["id"],
            "product_id": ObjectId(product_id),  # Convert product_id to ObjectId if it's a string
            "testimonial": testimonial_receive,
            "created_at": datetime.datetime.now()
        })

        return redirect(url_for('detail', id_product=product_id))  # Redirect to detail page of the product

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('index'))
    
@app.route('/about')
def about():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    return render_template("about.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in)

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
    


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
