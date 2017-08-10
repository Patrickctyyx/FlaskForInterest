from flask import abort
from flask_restful import Resource, fields, marshal_with
from webapp.models import db, Post, User, Tag
from .fields import HTMLField
from .parser import post_get_parser, post_post_parser


nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String()
}


post_fields = {
    'author': fields.String(attribute=lambda x: x.user.username),
    'title': fields.String(),
    'text': HTMLField(),
    'tags': fields.List(fields.Nested(nested_tag_fields)),
    'publish_time': fields.DateTime(dt_format='iso8601')
}


class PostApi(Resource):
    @marshal_with(post_fields)  # 对象的属性会根据这个 dict 来转换
    def get(self, post_id=None):
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404)
            return post  # 返回的 post 的内容已经被转换格式了
        else:
            args = post_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)

                posts = user.posts.order_by(Post.publish_time.desc()).paginate(page, 30)
            else:
                posts = Post.query.order_by(Post.publish_time.desc()).paginate(page, 30)
            return posts.items

    def post(self, post_id=None):
        if post_id:
            abort(405)
        else:
            args = post_post_parser.parse_args(strict=True)

            user = User.verify_auth_token(args['token'])
            if not user:
                abort(401)

            new_post = Post(args['title'])
            new_post.text = args['text']

            if args['tags']:
                for item in args['tags']:
                    tag = Tag.query.filter_by(title=item).first()
                    if tag:
                        new_post.tags.append(tag)
                    else:
                        new_tag = Tag(title=item)
                        new_post.tags.append(new_tag)

            db.session.add(new_post)
            db.session.commit()
            return new_post.id, 201
