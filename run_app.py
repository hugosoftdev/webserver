import os
#from api._01_manual_response_class import app
from endpoints import app
# from api._03_post_method import app
# from api._04_delete_method import app
# from api._05_flask_restful_simple import app


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
