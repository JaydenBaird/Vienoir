from flask import Flask, render_template, request, redirect, flash, strip
import pymysql
from dynaconf import Dynaconf

app = Flask(__name__)
app.secret_key = conf.secret_key
conf = Dynaconf(
    settings_file = ["settings.toml"]
)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def__init__(self, id, username, email, first_name, last_name):
        self.id = id
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
def sign_up():

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]

        username = request.form['username']
        email = request.form['email']

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        conn = connectdb()

        cursor = conn.cursor()

        cursor.execute(f"""
            INSERT INTO `Customer`
                    ( `first_name`, `last_name`, `username`, `email`, `password` )
                VALUES
                    ('{first_name}', '{last_name}, '{username}', '{email}', '{password}' );
                """)
        cursor.close()
        return redirect("/signin")
    return render_template("signup.html.jinja")
@app.route("/signin, methods=["POST","GET"]")
def signin():
    if request.method == "POST":
        username = request.form['username'],strip()
        password = request.form['password']
        
        conn = connect_db
        cursor = conn.cursor

        cursor.execute(f"SELECT * FROM `Customer` WHERE `username` = '{username}")

        result = cursor.fetchone()

        if result is not None:
            flash("Your username or password is incorrect")
        elif password  != result["password"]:
            flash("Your username or password is incorrect")
        else:
            user = User(result["id"], result["username"], result["email"],result["first_name"], result["last_name"])

            flash_login.login_user(user)

            return redirect('/')

        return render_template("signin.html.jinja")
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect ('/')