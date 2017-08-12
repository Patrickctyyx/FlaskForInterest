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
    help='Title is required!'
)
post_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help='Text is required!'
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
    help="Auth Token is required to create posts!"
)

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('username', type=str, required=True)
user_post_parser.add_argument('password', type=str, required=True)


post_put_parser = reqparse.RequestParser()
post_put_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to edit posts!"
)
post_put_parser.add_argument(
    'title',
    type=str
)
post_put_parser.add_argument(
    'text',
    type=str
)
post_put_parser.add_argument(
    'tags',
    type=str,
    action='append'
)

post_delete_parser = reqparse.RequestParser()
post_delete_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to delete posts!"
)

comment_get_parser = reqparse.RequestParser()
comment_get_parser.add_argument(
    'page',
    type=int,
    location=['args', 'header'],
    required=False
)
comment_get_parser.add_argument(
    'comment_id',
    type=int
)
comment_get_parser.add_argument(
    'user_id',
    type=int
)

comment_post_parser = reqparse.RequestParser()
comment_post_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to edit comment!"
)
comment_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help='Text is required!'
)

comment_put_parser = reqparse.RequestParser()
comment_put_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to edit comment!"
)
comment_put_parser.add_argument(
    'text',
    type=str
)
comment_put_parser.add_argument(
    'comment_id',
    type=int,
    required=True
)

comment_delete_parser = reqparse.RequestParser()
comment_delete_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to edit comment!"
)
comment_delete_parser.add_argument(
    'comment_id',
    type=int,
    required=True
)

contact_post_parser = reqparse.RequestParser()
contact_post_parser.add_argument(
    'c_name',
    type=str,
    required=True,
    help='Name is required!'
)
contact_post_parser.add_argument(
    'c_email',
    type=str,
    required=True,
    help='Email is required!'
)
contact_post_parser.add_argument(
    'c_text',
    type=str,
    required=True,
    help='Text is required!'
)
