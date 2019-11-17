from flask import Flask, request, jsonify, render_template
from connections import connections
from datetime import datetime


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    source_city = request.args.get('from')
    destination_city = request.args.get('to')
    date_from = request.args.get('departure')
    date_to = request.args.get('return')

    date_from = datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%f%z')
    date_to = datetime.strptime(date_to, '%Y-%m-%dT%H:%M:%S.%f%z')

    con = connections()
    results = con.get_data(source_city,destination_city,convert_date(date_from))
    result_return = {}
    if date_to is not None:
        results.extend(con.get_data(destination_city, source_city, convert_date(date_to)))
    
    return jsonify(results=results)


def convert_date(date):
    return f'{date.year}-{date.month}-{date.day}'

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()