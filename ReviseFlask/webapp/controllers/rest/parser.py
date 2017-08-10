from flask_restful import reqparse

post_get_parser = reqparse.RequestParser()
post_get_parser.add_argument(
    'page',
    type=int,
    location=['args', 'header'],
    required=False
)
post_get_parser.add_argument(
    'user',
    type=str,
    location=['json', 'args', 'headers']
)

post_post_parser = reqparse.RequestParser()
post_post_parser.add_argument(
    'title',
    type=str,
    required=True,
    help='标题不可少！'
)
post_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help='正文不可少！'
)
post_post_parser.add_argument(
    'tags',
    type=str,
    action='append'
)
post_post_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Token 是发表动态时必须的！"
)

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('username', type=str, required=True)
user_post_parser.add_argument('password', type=str, required=True)

