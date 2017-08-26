[原作者：李辉](http://note.youdao.com/)

# 第一个Flask小玩具——猜数字

## 后端亮点
- 使用了session

```Python
app.config['SECRET_KEY'] = 'TYTS,SN!'  # 设置密钥
session['number'] = random.randint(0, 100)  # session以dict储存
session['times'] = 10
```
- 使用flask_wtf
    - 用类来定义表单
    - 验证器很容易设置
    
## 前端亮点
- 使用了flask_bootstrap
- 直接引用bootstrap模板

```
{% extends "bootstrap/base.html" %}
```
- [flask_bootstrap文档](http://flask-bootstrap-zh.readthedocs.io/zh/latest/index.html)
    - 高度模块化，连标题都是块
    - 引用js也只用super()一下
    - 有现成的表单模板
- 结合Flask的flash()，报错十分容易，这个应该是表单模板的功劳

## 不得不说我的前端太差了orz