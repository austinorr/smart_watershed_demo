from flask import render_template
from . import home


@home.route('/home/')
@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template("index.html", title='Home')
