from flask import render_template, request, jsonify, make_response, flash, url_for, redirect
import pandas
import numpy
import altair as alt
from altair.utils.data import MaxRowsError


from . import timeseries


@timeseries.route('/timeseries/', methods=['GET'])
def ts_builder():
    """
    Render the homepage template on the / route
    """
    if request.args:
        kwargs = {k: float(v) for k, v in request.args.items()}
        data = build_timeseries(**kwargs)

        chart_spec = None
        chart_status = None
        msg = None
        try:
            chart_spec = make_chart(data).to_json()
            chart_status = "SUCCESS"
        except MaxRowsError:
            chart_status = "FAILURE"
            msg = "max data exceeded. Default max is 5000 data points"


        response = {
            'spec': chart_spec,
            'chart_status': chart_status,
            'message': msg
        }

        return make_response(jsonify(response), 200)


    return render_template("timeseries.html", title='Timeseries Builder')


def build_timeseries(*, start=0, stop=100, n_points=100, amplitude=1, frequency=1, **kwargs):
    x = numpy.linspace(start, stop, int(n_points))
    source = pandas.DataFrame({
      'x': x,
      'f(x)': amplitude * numpy.sin(x*frequency*2*numpy.pi)
    })

    return source


def make_chart(src):
    brush = alt.selection(type='interval', encodings=['x'])
    color = alt.Color('f(x):O', legend=None)

    line = alt.Chart(src).mark_line(
        interpolate='natural',
        color='lightblue',
        size=2
    ).encode(
        x='x',
        y='f(x)',
    )

    points = alt.Chart(src).mark_point().encode(
        x='x',
        y='f(x)',
        color=alt.condition(brush, color, alt.value('lightgray')),
    ).add_selection(brush)

    return line + points
