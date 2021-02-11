import os
import logging
from risk_manager import RiskManager

from flask import Flask

# Change the format of messages logged to Stackdriver
logger = logging.getLogger("__name__")
from flask import *
import pandas as pd

app = Flask(__name__)


@app.route("/calculate", methods=['POST'])
def calculate():
    symbols = request.json
    rm = RiskManager(symbols)
    id = rm.to_csv()
    print('id={}'.format(id))
    print('url={}'.format(str(url_for('show_tables', id=id))))
    response = app.response_class(
        response='go to link in 5 minutes: {}'.format(str(url_for('show_tables', id=id, _external=True))),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/results/<id>")
def show_tables(id):
    print(id)
    data = pd.read_csv('{}.csv'.format(id))
    data.set_index(['sym'], inplace=True)
    data.index.name = None
    # females = data.loc[data.Gender=='f']
    # males = data.loc[data.Gender=='m']
    return render_template('table_view.html', tables=[data.to_html(classes='female')],
                           titles=['symbol', 'test1', 'test2'])



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
