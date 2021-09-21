from application import app
from application.cms_receiver import cdr_receiver

@app.route("/", methods=['GET', 'POST'])
@app.route('/cdr', methods=['POST'])
def cdr():
    return cdr_receiver()

app.secret_key = "Super_secret_key"