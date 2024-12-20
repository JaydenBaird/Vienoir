from flask import Flask, render_template, request, redirect, flash,  abort
import pymysql
from dynaconf import Dynaconf
import flask_login
app = Flask(__name__)
conf = Dynaconf(
    settings_file = ["settings.toml"]
)
app.secret_key = conf.secret_key
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/signin"
class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True
    def __init__(self, user_id, username, email, first_name, last_name):
        self.id = user_id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
    def get_id(self):
        return str(self.id)
@login_manager.user_loader
def load_user(user_id):
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id}")
    result = cursor.fetchone()
    cursor.close()
    conn.cursor()
    if result is not None:
        return User(result["id"], result["username"], result["email"],result["first_name"], result["last_name"])
def connectdb():
    conn = pymysql.connect(
        host = "10.100.34.80",
        database = "jbaird_vienoir",
        user = "jbaird",
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn
@app.route("/")
def index ():
    return render_template("homepage.html.jinja")
app.route("/browse")
def product_browse():
    query = request.args.get("query")
    conn = connectdb()
    cursor = conn.cursor()
    if query is None:
        cursor.execute("SELECT * FROM `Product`;")
    else:
        cursor.execute(f"SELECT * FROM `Product` WHERE `name` LIKE '%{query}%' OR `description` LIKE '%{query}%';")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("browse.html.jinja", products = results, query = query)
@app.route("/product/<product_id>")
def product_page(product_id):
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `Product` WHERE `id` = {product_id};")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("product.html.jinja",product = result)
@app.route("/signup", methods = ["POST", "GET"])
@app.route("/product/<product_id>/cart", methods=["POST"])
@flask_login.login_required
def add_to_cart(product_id):
 conn = connectdb()
 cursor = conn.cursor()
 qty = request.form["qty"]
 Customer_id = flask_login.current_user.id
 cursor.execute(""""
 INSERT INTO `Customer`
    (`qty`, `Customer_id`, `Product_id`)
 VALUE
    ('qty', 'Customer_id', 'Product_id')
 """)
 cursor.close()
 conn.close()
 return redirect("/cart")
def signup():
    if flask_login.current_user.is_authenticated:
        return redirect ("/")
    else:
        if request.method == "POST":
            first_name = request.form["fname"]
            last_name = request.form["lname"]
            username = request.form["username"]
            password = request.form["pass"]
            confirmpassword = request.form["confirmpass"]
            email = request.form["email"]
            address = request.form["address"]
            conn = connectdb()
            cursor = conn.cursor()
            if len(password) < 8:
                flash("Password contains less than 8 characters")
            if confirmpassword != password:
                flash("The passwords don't match")
            else:
                try:
                    cursor.execute(f"""
                    INSERT INTO `Customer` 
                        (`first_name`, `last_name`, `username`, `password`, `email`, `address`)
                    VALUE
                        ('{first_name}', '{last_name}', '{username}', '{password}', '{email}', '{address}');
                    """)
                except pymysql.err.IntegrityError:
                    flash("Username/Email is already in use")
                else:    
                    return redirect("/signin") 
                finally:
                    cursor.close()
                    conn.close()
        return render_template("signup.html.jinja")
@app.route("/signin", methods=["POST","GET"])
def signin():
    if flask_login.current_user.is_authenticated:
        return redirect ("/")
    else:
        if request.method == "POST":
            username = request.form['username'].strip()
            password = request.form['password']
            conn = connectdb
            cursor = conn.cursor
            cursor.execute(f"SELECT * FROM `Customer` WHERE `username` = '{username}")
            result = cursor.fetchone()
            if result is not None:
                flash("Your username or password is incorrect")
            elif password  != result["password"]:
                flash("Your username or password is incorrect")
            else:
                user = User(result["id"], result["username"], result["email"],result["first_name"], result["last_name"])
                flask_login.login_user(user)
                return redirect('/')
            return render_template("signin.html.jinja")
        
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect ('/')
@app.route("/cart")
def cart():
    return "cart Page"