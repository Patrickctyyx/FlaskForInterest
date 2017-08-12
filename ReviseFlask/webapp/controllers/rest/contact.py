from flask_restful import Resource
from webapp.models import db, Contact
from .parser import contact_post_parser


class ContactApi(Resource):
    def post(self):
        args = contact_post_parser.parse_args()
        new_contact = Contact()
        new_contact.name = args['c_name']
        new_contact.text = args['c_text']
        new_contact.email = args['c_email']

        db.session.add(new_contact)
        db.session.commit()

        return new_contact.id, 201
