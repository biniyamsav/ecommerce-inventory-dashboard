from utils.styles import render_kpi_card


def metric_card(title, value, delta=None, delta_positive=True):
    render_kpi_card(title, value, delta=delta, delta_positive=delta_positive)
