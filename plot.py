import plotly.graph_objects as go
# import analysis
from itertools import cycle


def add_baseline(fig, baseline=0, signal=None):
    """
Add an horizontal baseline to a given plotly Figure.
    @param fig: go.Figure object.
    @param baseline: the value of the baseline
            integer, or string indicates one method from {"Walter"}.
    @param signal: the signal for computing the baseline, mandatory if
                    baseline argument == "Walter
    """
    if baseline == "Walter":
        baseline = analysis.walter_baseline(signal)
    fig.add_shape(
        type="line",
        x0=-500,
        y0=baseline,
        x1=1500,
        y1=baseline,
        line=dict(
            color="black",
            width=1,
            dash="dash"))


def add_stimulus(fig, time):
    """
Add a vertical line to a given fig that will represent a stimuli in the trial
    @param fig: go.Figure object
    @param time: time of the stimuli (int)
    """
    fig.add_shape(
        type="line",
        x0=time,
        y0=-13,
        x1=time,
        y1=13,
        line=dict(
            color="brown",
            width=1,
            dash="dash"))


def add_component(fig,comp, stimulus_time):
    """

    @param stimulus_time: e.g 0 or 600
    @param fig:
    @param comp: str like N100
    """
    time = float(comp[1:])+stimulus_time
    # instead of if else statements
    sign = {"N":-1, "P":1}[comp[0]]
    fig.add_trace(go.Scatter(
        x=[time],
        y=[sign*7],
        mode="text",
        text=[comp],
        hoverinfo='skip',
        showlegend=False
    ))


def init_trial(stimuli_times=[0], baseline=0, signal=None,
               components=None, **kwargs):
    """
Initialization of a figure representing a trial
    @param components: lst of tuples [(0,N100), (0,P200)]
    @param stimuli_times: list or tuple for adding vertical lines which will
                            represent the stimuli's time in the trial.
    @param baseline: integer or a method {"Walter"} for horizontal baseline
    @param signal: mandatory if baseline is "Walter"
    @return: go.Figure object
    """
    fig = go.Figure()
    # can be changed by the user later, out of the function, or by sending kwargs
    fig.update_layout(template="plotly_white",
                      xaxis_title="time (ms)",
                      yaxis_title="signal",
                      **kwargs)

    add_baseline(fig, baseline, signal)
    for t in stimuli_times:
        add_stimulus(fig, t)

    if components is not None:
        for s, c in components:
            add_component(fig,c,s)

    return fig


def go_signal(signal, timeline, **kwargs):
    return go.Scatter(x=timeline, y=signal, **kwargs)

# TODO: move all this file's functions to a Python Class
#  in order to let the user insert a default timeline
def add_signal(fig, timeline, sig, color=cycle(["royalblue",
                                    "firebrick",
                                    "green",
                                    "gold"]), **kwargs):
    sig_color = next(color)

    gos = go_signal(sig, timeline=timeline,
                    showlegend=True, line_color=sig_color, **kwargs)
    fig.add_trace(gos)
