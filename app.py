from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///m.db"
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    password = db.Column(db.String(100), nullable=False)
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


if __name__ == "__main__":
    app.run(debug=True)
