from flask import abort
from flask_restful import Resource, fields, marshal_with
from webapp.models import db, Comment, Post
from .parser import comment_get_parser


comment_field = {
    'name': fields.String(attribute=lambda x: x.user.username),
    'text': fields.String(),
    'date': fields.DateTime(dt_format='iso8601'),
    'post_id': fields.Integer()
}


class CommentApi(Resource):
    @marshal_with(comment_field)
    def get(self, post_id=None):
        args = comment_get_parser.parse_args()
        if post_id:
            post = Post.query.get_or_404(post_id)
            page = args['page'] or 1

            comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.date.desc()).paginate(page, 30)
            return comments.items
        if not args['comment_id']:
            abort(404)
        comment = Comment.query.get_or_404(args['comment_id'])
        return comment

    def post(self, post_id=None):
        post = Post.query.get_or_404(post_id)


