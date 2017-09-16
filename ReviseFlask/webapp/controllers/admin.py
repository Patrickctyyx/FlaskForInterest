from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import login_required, current_user
from webapp.forms import CKTextAreaField
from webapp.extensions import admin_permission


class CustomView(BaseView):
    @expose('/')
    @login_required
    @admin_permission.require(http_exception=403)
    def index(self):
        return self.render('admin/custom.html')

    @expose('/second_page')
    @login_required
    @admin_permission.require(http_exception=403)
    def second_page(self):
        return self.render('admin/second_page.html')


class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and admin_permission.can()


class PostView(CustomModelView):
    # 不知道为什么一直无效
    form_overrides = dict(text=CKTextAreaField)
    column_searchable_list = ('text', 'title')
    column_filters = ('publish_time', )

    create_template = 'admin/post_edit.html'
    edit_modal = 'admin/post_edit.html'


class CustomFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and admin_permission.can()
