from flask import render_template, redirect, url_for, Blueprint
from sqlalchemy import func

from webapp.models import db, Post, Tag, Comment, User, tags
from webapp.forms import CommentForm


blog_print = Blueprint(
    'blog',
    __name__,
    template_folder='template/blog',
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
    ).group_by(Tag).order_by('total DESC').limit(5).all()

    return recent, top_tags


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


@blog_print.errorhandler(404)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('404.html', recent=recent, top_tags=top_tags), 404


@blog_print.errorhandler(403)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('403.html', recent=recent, top_tags=top_tags), 403


@blog_print.errorhandler(500)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('500.html', recent=recent, top_tags=top_tags), 500

