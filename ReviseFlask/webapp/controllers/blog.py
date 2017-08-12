import datetime
from flask import render_template, redirect, url_for, Blueprint, flash, abort
from flask_login import current_user, login_required
from sqlalchemy import func
from webapp.models import db, Post, Tag, Comment, User, tags
from webapp.forms import CommentForm, PostForm


blog_print = Blueprint(
    'blog',
    __name__,
    template_folder='../templates/blog',
    url_prefix='/blog'
)


def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_time.desc()
    ).limit(5).all()
    # 下面这个查询不是很理解，join 和 group_by 这两个的用法没怎么接触过
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).limit(5).all()

    return recent, top_tags


@blog_print.route('/')
@blog_print.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(
        Post.publish_time.desc()
    ).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'home.html',
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@blog_print.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash('请登录后提交评论')
            return redirect(url_for('main.login'))
        new_comment = Comment()
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.user_id = current_user.id
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('.post', post_id=post_id))
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'post.html',
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form
    )


@blog_print.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(title=form.title.data)
        new_post.text = form.text.data
        new_post.user_id = current_user.id

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('.post', post_id=new_post.id))

    return render_template('new_post.html', form=form)


@blog_print.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):

    post = Post.query.get_or_404(post_id)
    if post.user.id is not current_user.id or post.user.id is not 1:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        post.publish_time = datetime.datetime.now()

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('.post', post_id=post.id))

    form.text.data = post.text
    form.title.data = post.title

    return render_template('edit_post.html', form=form, post=post)


@blog_print.route('/tag/<string:tag_name>')
@blog_print.route('/tag/<string:tag_name>/<int:page>')
def tag(tag_name, page=1):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_time.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'tag.html',
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
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


