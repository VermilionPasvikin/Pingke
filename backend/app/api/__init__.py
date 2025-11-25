# API模块初始化文件
from flask_restful import Api
import os

# 创建Flask-RESTful Api对象，将在app/__init__.py中与Flask应用实例关联
# 注意：不设置prefix参数，因为我们在路由注册时已经包含了/api前缀
api = Api()

# 注意：各个API模块会在app/__init__.py中被导入，以避免循环导入问题