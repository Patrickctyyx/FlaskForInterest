from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from webapp.forms import CKTextAreaField


class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom.html')

    @expose('/second_page')
    def second_page(self):
        return self.render('admin/second_page.html')


class CustomModelView(ModelView):
    pass


class PostView(CustomModelView):
    # 不知道为什么一直无效
    form_overrides = dict(text=CKTextAreaField)
    column_searchable_list = ('text', 'title')
    column_filters = ('publish_time', )

    create_template = 'admin/post_edit.html'
    edit_modal = 'admin/post_edit.html'
