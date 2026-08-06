from flask import Blueprint, render_template

work_bp = Blueprint('work', __name__, url_prefix='/work')

@work_bp.route('/', methods = ['GET'])
def work():
    return render_template('work.html')