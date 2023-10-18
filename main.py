from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests, os

url = "https://api.themoviedb.org/3/search/movie"

headers = {
    "accept": "application/json",
    "Authorization": os.environ["authorization_movie_database"]
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["config_for_flask"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
Bootstrap5(app)

# create the extension
db = SQLAlchemy()
db.init_app(app)


class movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(750), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500))
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()

new_book = movie(
    title="Avatar The Way of Water",
    year=2022,
    description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    rating=7.3,
    ranking=9,
    review="I liked the water.",
    img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg")

with app.app_context():
    try:
        db.session.add(new_book)
        db.session.commit()
    except:
        pass

with app.app_context():
    result = db.session.execute(db.select(movie).order_by(desc(movie.id)))
    ml = result.scalars().all()


class ratingform(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 7.5")
    review = StringField(label="Your Review")
    submit_1 = SubmitField(label="Done")


class addmovie(FlaskForm):
    movie = StringField(label="Movie")
    submit = SubmitField()


@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(movie).order_by(desc(movie.rating)))
        ml = result.scalars().all()

    for i in range(len(ml)):
        ml[i].ranking = i + 1
    db.session.commit()
    return render_template("index.html", mv=ml)


@app.route("/update", methods=["POST", "GET"])
def update():
    form = ratingform()
    if form.validate_on_submit():
        with app.app_context():
            book_to_update = db.session.execute(
                db.select(movie).where(movie.id == int(request.args.get("id")))).scalar()
            book_to_update.rating = float(request.form["rating"])
            book_to_update.review = request.form["review"]
            db.session.commit()
            return redirect(url_for("home"))
    return render_template("add.html", form_l=form)


@app.route("/delte", methods=["POST", "GET"])
def delete():
    with app.app_context():
        book_to_update = db.session.execute(db.select(movie).where(movie.id == int(request.args.get("id")))).scalar()
        db.session.delete(book_to_update)
        db.session.commit()

    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def adds():
    if request.method == "POST":
        para = {
            "query": request.form["movie"]}
        response = requests.get(url, headers=headers, params=para)

        result = response.json()["results"]

        return render_template("select.html", rt=result)

    mv = addmovie()
    return render_template("add.html", form_l=mv)


@app.route('/srch', methods=["POST", "GET"])
def srch():
    form = ratingform()

    print(request.method, request.args.get("id"))

    response = requests.get(f"https://api.themoviedb.org/3/movie/{request.args.get('id')}?language=en-US",
                            headers=headers).json()

    mov = "https://image.tmdb.org/t/p/w500"
    img = f"{mov}{response['poster_path']}"
    new_book = movie(
        title=str(response["original_title"]),
        year=int(response["release_date"].split("-")[0]),
        description=response["overview"],
        img_url=img,
    )
    if request.method == "POST":
        print("done", request.form.to_dict())
        with app.app_context():
            book_to_update = db.session.execute(
                db.select(movie).where(movie.title == response["original_title"])).scalar()
            book_to_update.rating = float(request.form["rating"])
            book_to_update.review = request.form["review"]
            db.session.commit()
            return redirect(url_for("home"))

    try:
        with app.app_context():
            db.session.add(new_book)
            db.session.commit()
        print("went")
    except:
        pass
    return render_template("add.html", form_l=form)


@app.route("/update_n", methods=["POST", "GET"])
def update_n():
    form = ratingform()
    print(request.method, request.args.get("id"))


if __name__ == '__main__':
    app.run(debug=True)
