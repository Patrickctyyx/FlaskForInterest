import datetime
from flask import Flask, render_template, redirect, url_for, g, session, abort, Blueprint
from config import DevConfig
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask.views import View
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

blog_print = Blueprint(
    'blog',
    __name__,
    template_folder='template/blog',
    url_prefix='/blog'
)


tags = db.Table('post_tags',
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User \'{}\'>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text)
    publish_time = db.Column(db.DateTime, default=datetime.datetime.now)

    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Post \'{}\'>'.format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment \'{}\'>'.format(self.text[:15])


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Tag \'{}\'>'.format(self.title)


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])


def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_time.desc()
    ).limit(5).all()
    # 下面这个查询不是很理解，join 和 group_by 这两个的用法没怎么接触过
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).order_by('total DESC').limit(5).all()

    return recent, top_tags


@app.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/restricted')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')


@app.errorhandler(404)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('404.html', recent=recent, top_tags=top_tags), 404


@app.errorhandler(403)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('403.html', recent=recent, top_tags=top_tags), 403


@app.errorhandler(500)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('500.html', recent=recent, top_tags=top_tags), 500


@app.route('/')
def index():
    return redirect(url_for('blog.home'))


@blog_print.route('/')
@blog_print.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(
        Post.publish_time.desc()
    ).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'blog/home.html',
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@blog_print.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('.post', post_id=post_id))
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'blog/post.html',
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form
    )


@blog_print.route('/tag/<string:tag_name>')
@blog_print.route('/tag/<string:tag_name>/<int:page>')
def tag(tag_name, page=1):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_time.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'blog/tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@blog_print.route('/user/<string:username>')
@blog_print.route('/user/<string:username>/<int:page>')
def user(username, page=1):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_time.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'blog/user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


class GenericView(View):  # 定义视图类，减少重复
    def __init__(self, template):
        self.template = template
        super(GenericView, self).__init__()

    # 作用和普通视图函数相同
    def dispatch_request(self):
        page = 1
        posts = Post.query.order_by(
            Post.publish_time.desc()
        ).paginate(page, 10)
        recent, top_tags = sidebar_data()

        return render_template(
            self.template,
            posts=posts,
            recent=recent,
            top_tags=top_tags
        )


app.add_url_rule(
    # 第一个参数是 url
    '/test',
    view_func=GenericView.as_view(
        'test',  # 指定 endpoint
        template='home.html'
    )
)


# import random
# import datetime
#
# user = User('patrick')
# db.session.add(user)
# db.session.flush()
# tag_one = Tag('Python')
# tag_two = Tag('Flask')
# tag_three = Tag('SQLAlchemy')
# tag_four = Tag('Jinja')
# tag_list = [tag_one, tag_two, tag_three, tag_four]
#
# s = 'Example text'
#
# for i in range(100):
#     new_post = Post('Post ' + str(i))
#     new_post.user = user
#     new_post.text = s
#     new_post.tags = random.sample(tag_list, random.randint(1, 3))
#     db.session.add(new_post)
#
# db.session.commit()

app.register_blueprint(blog_print)

if __name__ == '__main__':
    app.run()
