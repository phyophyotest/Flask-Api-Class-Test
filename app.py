from flask import Flask, render_template, redirect, request, flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///m.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = "asdfasdf2323"

UPLOAD_FOLDER = "./static/imgs"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return self.name


@app.route("/")
def home():
    context = {
        "title": "Home Page"
    }
    cat = Category.query.get(1)
    print(cat)
    return render_template("home.html", context=context)


@app.route("/posts")
def posts():
    context = {
        "title": "Category Home Page",
        "posts": Post.query.all(),
    }
    return render_template("posts.html", context=context)


@app.route("/post/create", methods=["POST", "GET"])
def postCreate():
    context = {
        "title": "Category Home Page",
        "cats": Category.query.all()
    }
    if request.method == "POST":
        filename = ""
        file = request.files['image']

        if file.filename == '':
            flash('No selected file')
            return redirect("/posts")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cat_id = request.form["cat_id"]
        title = request.form["title"]
        content = request.form["content"]
        post = Post(cat_id=cat_id, title=title,
                    content=content, image=filename)
        try:
            db.session.add(post)
            db.session.commit()
            return redirect("/posts")
        except:
            return render_template("post_create.html", context=context)
    else:
        return render_template("post_create.html", context=context)


@app.route("/cats")
def cats():
    cats = Category.query.all()
    context = {
        "title": "Category Home Page",
        "cats": cats
    }
    return render_template("cats.html", context=context)


@app.route("/cats/create", methods=["POST", "GET"])
def catCreate():
    context = {
        "title": "Category Create Page"
    }
    if request.method == "POST":
        name = request.form["name"]
        cat = Category(name=name)

        try:
            db.session.add(cat)
            db.session.commit()
            return redirect("/cats")
        except:
            return render_template("cat_create.html", context=context)
    else:
        return render_template("cat_create.html", context=context)


@app.route("/cats/edit/<int:id>", methods=["POST", "GET"])
def catEdit(id):
    cat = Category.query.get_or_404(id)
    context = {
        "title": "Category Edit Page",
        "cat": cat
    }
    if request.method == "POST":
        name = request.form["name"]
        cat.name = name
        try:
            db.session.commit()
            return redirect("/cats")
        except:
            return render_template("cat_edit.html", context=context)
    else:
        return render_template("cat_edit.html", context=context)


@app.route("/cats/delete/<int:id>")
def catDelete(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return redirect("/cats")


@app.route("/register", methods=["POST", "GET"])
def register():
    context = {
        "title": "User Register Page"
    }
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password = bcrypt.generate_password_hash(password)
        user = User(name=name, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            return render_template("register.html", context=context)
    else:
        return render_template("register.html", context=context)


@app.route("/login", methods=["POST", "GET"])
def login():
    context = {
        "title": "User Login Page"
    }
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user : 
            if bcrypt.check_password_hash(user.password, password):
                flash("Welcome Back")
                session["username"] =user.name
                session["email"] =user.email
                return redirect("/")
            else:
                print("Password Fail")
                return redirect("/login")
        else : 
            print("Email Error!")
            return redirect('/login')
    else:
        return render_template("login.html", context=context)
# Helpers Methods

@app.route("/logout")
def logout():
    session["username"] = ""
    session["email"] = ""
    return redirect("/login")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=True)
