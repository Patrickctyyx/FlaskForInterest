from flask import abort, current_app
from .parser import user_post_parser
from flask_restful import Resource
from webapp.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class AuthApi(Resource):
    def post(self):
        args = user_post_parser.parse_args()
        user = User.query.filter_by(
            username=args['username']
        ).one()

        if user.verify_password(args['password']):
            s = Serializer(
                current_app.config['SECRET_KEY'],
                expires_in=600
            )
            return {"token": s.dumps({'id': user.id}).decode('utf-8')}

        else:
            abort(401)
