import random
import datetime
from webapp.models import User, Tag, Post, db, Role


def generate_fake_posts():
    user = User.query.get(1)
    db.session.add(user)
    db.session.flush()
    tag_one = Tag('Python')
    tag_two = Tag('Flask')
    tag_three = Tag('SQLAlchemy')
    tag_four = Tag('Jinja')
    tag_list = [tag_one, tag_two, tag_three, tag_four]

    s = 'Example text'

    for i in range(100):
        new_post = Post('Post ' + str(i))
        new_post.user = user
        new_post.publish_time = datetime.datetime.now()
        new_post.text = s
        new_post.tags = random.sample(tag_list, random.randint(1, 3))
        db.session.add(new_post)

    db.session.commit()


def init_roles():
    role1 = Role('default')
    db.session.add(role1)
    role2 = Role('admin')
    db.session.add(role2)
    role3 = Role('poster')
    db.session.add(role3)
    db.session.commit()
