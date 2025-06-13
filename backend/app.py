from flask import Flask,config
import config
from flask_cors import CORS
from flask import render_template
from flask_socketio import SocketIO
#这个包我装的是5.3.6

app = Flask(__name__)
app.config.from_object(config)
#CORS(app)  # 允许所有来源的跨域请求
CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources=r'/*')
#Flask 应用允许来自任何源的所有请求（即 /*）访问资源,如果想指定它只接受/api/***,则将resources=r'/api/*'

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


# 密钥，用于生成和验证令牌
app.config['SECRET_KEY'] = 'X5p@7z9K#m!2N$q4R%t6V&w8Y(a)c*e+f'