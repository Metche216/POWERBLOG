from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

ckeditor = CKEditor()

app = Flask(__name__)
#APP CONFIG
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor.init_app(app)


#NEW POST FORM
class NewPostForm(FlaskForm):
    title = StringField(label='title', validators=[DataRequired()])
    subtitle = StringField(label='subtitle', validators=[DataRequired()])
    author = StringField(label='author', validators=[DataRequired()])
    img_url = StringField(label='img_url', validators=[URL()])
    body = CKEditorField(label='body', validators=[DataRequired()])
    submit = SubmitField(label="Create")

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost,post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=["GET","POST"])
def new_post():
    if request.method == "POST":
        print("post request activated")
        today = date.today()
        formatted_date = today.strftime("%B %d, %Y")
        
        new_post = BlogPost(
            title = request.form.get('title'),
            subtitle = request.form.get('subtitle'),
            body = request.form.get('body'),
            author = request.form.get('author'),
            img_url = request.form.get('img_url'),
            date = formatted_date
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
        
    else:
        print("get request returned")
        blank_form = NewPostForm()
        
        return render_template('make-post.html',form=blank_form)

# TODO: edit_post() to change an existing blog post
@app.route("/edit_post/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    edit_post = db.get_or_404(BlogPost, id)
    form = NewPostForm(request.form, obj=edit_post)
    print(request.form)
    
        
    if form.validate_on_submit():
        print("validated")
        edit_post.title = form.title.data
        edit_post.subtitle = form.subtitle.data
        edit_post.author = form.author.data
        edit_post.body = form.body.data
        edit_post.img_url = form.img_url.data
    
        db.session.commit()
        return redirect(url_for('show_post',post_id=edit_post.id))
    else:
        form.submit.label.text = "Edit"
        return render_template('make-post.html', edit=True, form=form, post=edit_post)
    

# TODO: delete_post() to remove a blog post from the database
@app.route("/delete/<int:id>")
def delete_post(id):
    to_delete = db.get_or_404(BlogPost, id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
