import time

from flask import (
    render_template,
    request,
    jsonify,
    make_response,
    flash,
    url_for,
    redirect,
)
import pandas
import numpy
import altair as alt
from altair.utils.data import MaxRowsError


from . import timeseries


@timeseries.route("/timeseries/", methods=["GET"])
def timeseries_ui():
    """
    Render the homepage template on the / route
    """

    return render_template("timeseries.html", title="Timeseries Builder")


@timeseries.route("/timeseries/api", methods=["GET"])
def timeseries_builder():
    """
    Render the homepage template on the / route
    """

    chart_spec = None
    chart_status = None
    msg = None

    response = {"spec": chart_spec, "chart_status": chart_status, "message": msg}

    if not request.args:
        response["message"] = "No data in request"
        return make_response(jsonify(response), 200)

    else:
        kwargs = {k: float(v) for k, v in request.args.items()}

        delay = kwargs.get("delay", 0)
        if delay > 0:
            time.sleep(delay)
        data = build_timeseries(**kwargs)

        try:
            chart_spec = make_chart(data).to_json()
            chart_status = "SUCCESS"
        except MaxRowsError:
            chart_status = "FAILURE"
            msg = "max data exceeded. Default max is 5000 data points"

        response = {"spec": chart_spec, "chart_status": chart_status, "message": msg}

        return make_response(jsonify(response), 200)


def build_timeseries(
    *,
    start=0,
    stop=100,
    n_points=100,
    amplitude=1,
    frequency=1,
    offset=0,
    noise=0,
    trend=0,
    **kwargs
):
    x = numpy.linspace(start, stop, int(n_points))
    source = pandas.DataFrame(
        {
            "x": x,
            "y": (
                offset
                + (trend * x)
                + (noise * numpy.random.uniform(-1, 1, size=x.shape))
                + amplitude * numpy.sin(x * frequency * 2 * numpy.pi)
            ),
        }
    )

    return source


def make_chart(src):
    brush = alt.selection(type="interval", encodings=["x", "y"])
    color = alt.Color("y:O", legend=None)

    line = (
        alt.Chart(src)
        .mark_line(interpolate="natural", color="lightblue", size=2)
        .encode(x=alt.X("x", title="Days"), y=alt.Y("y", title="Flowrate cfs"))
    )

    points = (
        alt.Chart(src)
        .mark_point()
        .encode(
            x="x",
            y="y",
            color=alt.condition(brush, color, alt.value("lightgray")),
            tooltip=[
                alt.Tooltip("y:Q", format=".2f", title="Flowrate"),
                alt.Tooltip("x:Q", format=".1f", title="Day"),
            ],
        )
        .add_selection(brush)
    )

    avg_line = (
        alt.Chart(src)
        .mark_rule(color="grey", opacity=0.5)
        .encode(y="mean(y):Q", size=alt.SizeValue(3),)
        .transform_filter(brush)
    )

    fit_line = line.transform_regression("x", "y").mark_line(color="firebrick")

    text = (
        alt.Chart(src)
        .mark_text(align="left", baseline="middle", x="width", dx=7,)
        .encode(y="mean(y):Q", text=alt.Text("mean(y):Q", format=".2f"))
        .transform_filter(brush)
    )

    return avg_line + line + points + fit_line + text
