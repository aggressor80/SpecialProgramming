import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    t = np.linspace(0, 2 * np.pi, 1000)
    h_signal = amplitude * np.sin(frequency * t + phase)
    noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))

    if show_noise:
        noise_signal = h_signal + noise
    else:
        noise_signal = h_signal

    return t, h_signal, noise_signal


app = Dash(__name__)


start_params = {
    "amplitude": 1.0,
    "frequency": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_covariance": 0.5,
    "show_noise": True
}

app.layout = html.Div([
    html.H1("Гармоніка з шумом"),

    dcc.Graph(id="harmonic-plot"),

    html.Div([
        html.Label("Амплітуда:"),
        dcc.Slider(id="amplitude_slider", min=0, max=10, marks=None, value=start_params["amplitude"],
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Частота:"),
        dcc.Slider(id="frequency_slider", min=0.1, max=10, marks=None, value=start_params["frequency"],
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Фаза:"),
        dcc.Slider(id="phase_slider", min=0, max=2 * np.pi, marks=None, value=start_params["phase"],
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Середнє шуму:"),
        dcc.Slider(id="noise_mean_slider", min=-2, max=2, marks=None, value=start_params["noise_mean"],
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Дисперсія шуму:"),
        dcc.Slider(id="noise_covariance_slider", min=0, max=1, marks=None, value=start_params["noise_covariance"],
                   tooltip={"placement": "bottom", "always_visible": True})
    ]),

    html.Div([
        dcc.Checklist(
            id="show_noise_checkbox",
            options=[{"label": "Показати шум", "value": "show_noise"}],
            value=["show_noise"] if start_params["show_noise"] else []
        )
    ]),

    html.Div([
        html.Button("Скинути", id="reset_button", n_clicks=0)])
])

@app.callback(
    Output("harmonic-plot", "figure"),
    [
        Input("amplitude_slider", "value"),
        Input("frequency_slider", "value"),
        Input("phase_slider", "value"),
        Input("noise_mean_slider", "value"),
        Input("noise_covariance_slider", "value"),
        Input("show_noise_checkbox", "value")
    ]
)

def update_graph(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    t, h_signal, noise_signal = harmonic_with_noise(
        amplitude, frequency, phase, noise_mean, noise_covariance,
        show_noise="show_noise" in show_noise
    )

    figure = {
        "data": [
            go.Scatter(x=t, y=h_signal, mode="lines")
        ] + (
            [go.Scatter(x=t, y=noise_signal, mode="lines")] if "show_noise" in show_noise else []
        ),
        "layout": go.Layout(
            xaxis={"title": "Час"},
            yaxis={"title": "Амплітуда"},
            hovermode="closest"
        )
    }
    return figure

@app.callback(
    [
        Output("amplitude_slider", "value"),
        Output("frequency_slider", "value"),
        Output("phase_slider", "value"),
        Output("noise_mean_slider", "value"),
        Output("noise_covariance_slider", "value"),
        Output("show_noise_checkbox", "value")
    ],
    [Input("reset_button", "n_clicks")],
    prevent_initial_call=True
)
def reset_values(n_clicks):
    return (
        start_params["amplitude"],
        start_params["frequency"],
        start_params["phase"],
        start_params["noise_mean"],
        start_params["noise_covariance"],
        ["show_noise"] if start_params["show_noise"] else []
    )


if __name__ == "__main__":
    app.run_server(debug=True)