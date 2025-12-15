from flask import Flask, render_template, jsonify, request, send_file, Response
import io
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Record
from db_utils import init_db, get_all_records, query_aggregates
from analysis import records_to_dataframe, timeseries_aggregate, moving_average

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize DB
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/charts')
def charts_page():
    return render_template('charts.html')


@app.route('/api/records')
def api_records():
    records = get_all_records()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/aggregate')
def api_aggregate():
    group_by = request.args.get('group_by', 'category')
    return jsonify(query_aggregates(group_by))


@app.route('/api/timeseries')
def api_timeseries():
    records = get_all_records()
    df = records_to_dataframe(records)
    freq = request.args.get('freq', 'D')
    ts = timeseries_aggregate(df, freq)
    return jsonify(ts.to_dict(orient='records'))


@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'no file uploaded'}), 400

    df = pd.read_csv(file)
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])

    with app.app_context():
        for _, row in df.iterrows():
            rec = Record(
                category=row['category'],
                subcategory=row.get('subcategory'),
                value=float(row['value']),
                recorded_at=row['recorded_at'].to_pydatetime()
            )
            db.session.add(rec)
        db.session.commit()

    return jsonify({'status': 'ok', 'rows': len(df)})


# -------------------------
# STEP 10 – EXCEL EXPORT
# -------------------------
@app.route('/export/excel')
def export_excel():
    records = get_all_records()
    df = records_to_dataframe(records)

    pivot = df.pivot_table(
        index='recorded_at',
        columns='category',
        values='value',
        aggfunc='sum',
        fill_value=0
    )

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pivot.to_excel(writer, sheet_name='Pivot')

    output.seek(0)
    return send_file(
        output,
        download_name='report.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# -------------------------
# STEP 9 (Part 2) – STATIC PNG (Matplotlib)
# -------------------------
@app.route('/static_timeseries.png')
def static_ts_png():
    records = get_all_records()
    df = records_to_dataframe(records)
    ts = timeseries_aggregate(df, 'D')

    plt.figure(figsize=(8, 4))
    plt.plot(ts['recorded_at'], ts['value'])
    plt.title('Daily Value')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return Response(buf.getvalue(), mimetype='image/png')


# -------------------------
# STEP 9 – Interactive Plotly Chart
# -------------------------
@app.route('/api/plotly_timeseries')
def api_plotly_ts():
    records = get_all_records()
    df = records_to_dataframe(records)
    freq = request.args.get('freq', 'D')
    ts = timeseries_aggregate(df, freq)

    fig = px.line(ts, x='recorded_at', y='value', title='Timeseries')
    return fig.to_json()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
