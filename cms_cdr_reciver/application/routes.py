from application import app
from application.cms_reciver import cdr_receiver

@app.route('/cdr', methods=['POST'])
def cdr():
    return cdr_receiver()

app.secret_key = "Super_secret_key"