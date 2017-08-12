from flask import abort
from flask_restful import Resource, fields, marshal_with
from webapp.models import db, Comment, Post, User
from .parser import comment_get_parser, comment_post_parser, comment_put_parser, comment_delete_parser


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
            Post.query.get_or_404(post_id)
            page = args['page'] or 1

            if args['user_id']:
                comments = Comment.query.filter_by(post_id=post_id, user_id=args['user_id']).paginate(page, 30)
            else:
                comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.date.desc()).paginate(page, 30)
            return comments.items
        if not args['comment_id']:
            abort(404)
        comment = Comment.query.get_or_404(args['comment_id'])
        return comment

    def post(self, post_id=None):
        Post.query.get_or_404(post_id)
        args = comment_post_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if not user:
            abort(401)

        new_comment = Comment()
        new_comment.text = args['text']
        new_comment.user_id = user.id
        new_comment.post_id = post_id

        db.session.add(new_comment)
        db.session.commit()
        return new_comment.id, 201

    def put(self):
        args = comment_put_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if not user:
            abort(401)

        comment = Comment.query.get_or_404(args['comment_id'])
        if user != comment.user:
            abort(403)

        if args['text']:
            comment.text = args['text']

        db.session.add(comment)
        db.session.commit()

        return comment.id, 201

    def delete(self):
        args = comment_delete_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if not user:
            abort(401)

        comment = Comment.query.get_or_404(args['comment_id'])
        if user != comment.user:
            abort(403)

        db.session.delete(comment)
        db.session.commit()

        return "", 204




