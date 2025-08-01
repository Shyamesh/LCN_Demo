import dash
from dash import dcc, html, Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import numpy as np  # Make sure numpy is imported

# --- File and Metric Setup ---
cca_names = ["CUBIC", "BBRv1", "BBRv2", "BBRv3", "BBRv3 vs CUBIC"]

metric_labels = {
    "throughput_mbps": "Throughput (Mbps)",
    "rtt_ms": "RTT (ms)",
    "jitter_ms": "Jitter (ms)",
    "cwnd_bytes": "Congestion Window (Bytes)",
    "retransmits": "Retransmissions",
    "pacing_rate": "Pacing Rate (Mbps)",
    "delivery_rate": "Delivery Rate (Mbps)",
    "pacing_gain": "Pacing Gain",
    "inflight_data": "Data Inflight"
}

custom_colors = {
    "CUBIC": "darkred",
    "BBRv1": "purple",
    "BBRv2": "darkgreen",
    "BBRv3": "blue",
    "BBRv3 vs CUBIC":  "#c71585"
}

# --- Dash App ---
app = dash.Dash(__name__)
app.title = "TCP Metrics Visualizer"

# Load topology image (adjust this path to your image)
# topo_image_path = r"C:\Users\User\Documents\GitHub\LCN_Demo\home_security.jpeg"
topo_image_path = "./home_security.jpeg"

print("Checking image path:", topo_image_path)
print("File exists:", os.path.exists(topo_image_path))

topo_base64 = None
if os.path.exists(topo_image_path):
    with open(topo_image_path, "rb") as img_file:
        topo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

app.layout = html.Div(style={
    "fontFamily": "'Segoe UI', sans-serif",
    "background": "linear-gradient(135deg, #e0f7fa, #f1f8ff)",
    "minHeight": "100vh",
    "padding": "20px"
}, children=[

    html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px", "minHeight": "calc(100vh - 40px)"}, children=[

        html.Div([
            html.H3("Network Topology", style={"color": "#1a237e", "marginBottom": "10px", "textAlign": "center"}),
            html.Img(
                src=f"data:image/png;base64,{topo_base64}",
                style={"width": "100%", "height": "calc(100% -0px)", "objectFit": "contain", "borderRadius": "12px", "border": "2px solid #ccc"}
            ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f", "textAlign": "center"})
        ], style={
            "flex": "1",
            "padding": "20px",
            "backgroundColor": "#afe7cd",
            "borderRadius": "12px",
            "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)",
            "display": "flex",
            "flexDirection": "column",
            "height": "100%",
            "justifyContent": "flex-start",
            "alignItems": "center"
        }),

        html.Div([
            html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

            html.Div([
                html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="aqm-select",
                    options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "CAKE"]],
                    value="PFIFO",
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="direction-select",
                    options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
                    value="Upload",
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="scenario-select",
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="metric-select",
                    options=[{"label": label, "value": key} for key, label in metric_labels.items()],
                    value=["throughput_mbps", "rtt_ms"],
                    multi=True,
                    placeholder="Choose one or more metrics",
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Img(id="metric-plot", style={
                    "width": "100%",
                    "border": "2px solid #ccc",
                    "borderRadius": "12px",
                    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
                })
            ])
        ], style={
            "flex": "2",
            "padding": "20px",
            "backgroundColor": "#ffffff",
            "borderRadius": "12px",
            "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
        })
    ])
])

def load_data_for_aqm_direction(aqm_type, direction_type):
    current_available_flows = {}
    for name in cca_names:
        filename = f"{name}_{aqm_type}_{direction_type}.csv"
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)

                if "time_sec" in df.columns:
                    df["Time"] = df["time_sec"]
                else:
                    df["Time"] = df.index

                for col in ["pacing_rate", "delivery_rate"]:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.replace(r'[^\d\.]+', '', regex=True)
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                for col in ["pacing_gain", "inflight_data"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # Clip throughput_mbps at 10
                if "throughput_mbps" in df.columns:
                    series = df["throughput_mbps"]
                    df["throughput_mbps"] = np.minimum(series, 10)  # Clip at 10 Mbps

                df["label"] = name
                current_available_flows[name] = df
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
    return current_available_flows

@app.callback(
    Output("scenario-select", "options"),
    Output("scenario-select", "value"),
    Input("aqm-select", "value"),
    Input("direction-select", "value")
)
def set_scenario_options(aqm_selected, direction_selected):
    current_flows = load_data_for_aqm_direction(aqm_selected, direction_selected)
    current_flow_scenarios = {}

    for f1_name in cca_names:
        for f2_name in cca_names:
            if f1_name in current_flows and f2_name in current_flows:
                scenario_key = f"{f1_name} vs {f2_name}"
                current_flow_scenarios[scenario_key] = (current_flows[f1_name].copy(), current_flows[f2_name].copy())

    options = [{"label": k, "value": k} for k in sorted(current_flow_scenarios.keys())]
    default_value = options[0]["value"] if options else None
    return options, default_value

@app.callback(
    Output("metric-plot", "src"),
    Input("scenario-select", "value"),
    Input("aqm-select", "value"),
    Input("direction-select", "value"),
    Input("metric-select", "value")
)
def update_plot(scenario, aqm, direction, selected_metrics):
    current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

    if not scenario or not selected_metrics:
        return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

    f1_name, f2_name = scenario.split(" vs ")

    if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5,
                f"Data missing for '{scenario}' with AQM '{aqm}' and Direction '{direction}'.\n"
                "Please ensure CSV files like '{CCA}_{AQM}_{Direction}.csv' exist.",
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
                fontsize=20, color='red')
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=600)
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

    df1 = current_flows_for_plot[f1_name].copy()
    df2 = current_flows_for_plot[f2_name].copy()

    for df in [df1, df2]:
        for metric in selected_metrics:
            if metric in df.columns:
                df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()
            else:
                df[f"{metric}_smoothed"] = None
                print(f"Warning: Metric '{metric}' not found in CSV for {df['label'].iloc[0]}.")

    num_metrics = len(selected_metrics)
    fig, axs = plt.subplots(num_metrics, 1, figsize=(8, 4 * num_metrics), sharex=True)
    fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=20)

    if num_metrics == 1:
        axs = [axs]

    for i, metric in enumerate(selected_metrics):
        if f"{metric}_smoothed" in df1.columns and df1[f"{metric}_smoothed"] is not None and not df1[f"{metric}_smoothed"].isnull().all():
            axs[i].plot(df1["Time"], df1[f"{metric}_smoothed"],
                        label=df1["label"].iloc[0],
                        color=custom_colors.get(df1["label"].iloc[0], "black"),
                        linestyle="-", linewidth=2)

        if f"{metric}_smoothed" in df2.columns and df2[f"{metric}_smoothed"] is not None and not df2[f"{metric}_smoothed"].isnull().all():
            axs[i].plot(df2["Time"], df2[f"{metric}_smoothed"],
                        label=df2["label"].iloc[0],
                        color=custom_colors.get(df2["label"].iloc[0], "black"),
                        linestyle="-", linewidth=2)

        axs[i].set_ylabel(metric_labels.get(metric, metric), fontsize=20)
        axs[i].grid(True, linestyle='--', alpha=0.3)
        axs[i].legend(loc='upper right', fontsize=20)
        axs[i].tick_params(axis='both', which='major', labelsize=22)

    axs[-1].set_xlabel("Time (s)", fontsize=20)
    axs[-1].tick_params(axis='x', labelsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=600)
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

app.run(debug=True)





# import dash
# from dash import dcc, html, Input, Output
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# import base64
# import os

# # --- File and Metric Setup ---
# cca_names = ["CUBIC", "BBRv1", "BBRv2", "BBRv3", "BBRv3 vs CUBIC"]

# metric_labels = {
#     "throughput_mbps": "Throughput (Mbps)",
#     "rtt_ms": "RTT (ms)",
#     "jitter_ms": "Jitter (ms)",
#     "cwnd_bytes": "Congestion Window (Bytes)",
#     "retransmits": "Retransmissions",
#     "pacing_rate": "Pacing Rate (Mbps)",
#     "delivery_rate": "Delivery Rate (Mbps)",
#     "pacing_gain": "Pacing Gain",
#     "inflight_data": "Data Inflight"
# }

# custom_colors = {
#     "CUBIC": "darkred",
#     "BBRv1": "purple",
#     "BBRv2": "darkgreen",
#     "BBRv3": "blue",
#     "BBRv3 vs CUBIC":  "#c71585"
# }

# # --- Dash App ---
# app = dash.Dash(__name__)
# app.title = "TCP Metrics Visualizer"

# # Load topology image (adjust this path to your image)
# # topo_image_path = r"C:\Users\User\Documents\GitHub\LCN_Demo\home_security.jpeg"
# topo_image_path = "./home_security.jpeg"

# print("Checking image path:", topo_image_path)
# print("File exists:", os.path.exists(topo_image_path))


# topo_base64 = None
# if os.path.exists(topo_image_path):
#     with open(topo_image_path, "rb") as img_file:
#         topo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# app.layout = html.Div(style={
#     "fontFamily": "'Segoe UI', sans-serif",
#     "background": "linear-gradient(135deg, #e0f7fa, #f1f8ff)",
#     "minHeight": "100vh",
#     "padding": "20px"
# }, children=[

#     html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px", "minHeight": "calc(100vh - 40px)"}, children=[
        
#         # Left Panel: Network Topology
#         html.Div([
#             html.H3("Network Topology", style={"color": "#1a237e", "marginBottom": "10px", "textAlign": "center"}),
#             html.Img(
#                 src=f"data:image/png;base64,{topo_base64}",
#                 style={"width": "100%", "height": "calc(100% -0px)", "objectFit": "contain", "borderRadius": "12px", "border": "2px solid #ccc"}
#             ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f", "textAlign": "center"})
#         ], style={
#             "flex": "1",
#             "padding": "20px",
#             "backgroundColor": "#afe7cd",
#             "borderRadius": "12px",
#             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)",
#             "display": "flex",
#             "flexDirection": "column",
#             "height": "100%",
#             "justifyContent": "flex-start",
#             "alignItems": "center"
#         }),

#         # Right Panel: Controls and Plot
#         html.Div([
#             html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

#             html.Div([
#                 html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="aqm-select",
#                     options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "CAKE"]],
#                     value="PFIFO",
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="direction-select",
#                     options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
#                     value="Upload",
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="scenario-select",
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="metric-select",
#                     options=[{"label": label, "value": key} for key, label in metric_labels.items()],
#                     value=["throughput_mbps", "rtt_ms"],
#                     multi=True,
#                     placeholder="Choose one or more metrics",
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Img(id="metric-plot", style={
#                     "width": "100%",
#                     "border": "2px solid #ccc",
#                     "borderRadius": "12px",
#                     "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
#                 })
#             ])
#         ], style={
#             "flex": "2",
#             "padding": "20px",
#             "backgroundColor": "#ffffff",
#             "borderRadius": "12px",
#             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
#         })
#     ])
# ])

# # --- Helper function to load and clean data ---
# def load_data_for_aqm_direction(aqm_type, direction_type):
#     current_available_flows = {}
#     for name in cca_names:
#         filename = f"{name}_{aqm_type}_{direction_type}.csv"
#         if os.path.exists(filename):
#             try:
#                 df = pd.read_csv(filename)

#                 # Time column
#                 if "time_sec" in df.columns:
#                     df["Time"] = df["time_sec"]
#                 else:
#                     df["Time"] = df.index

#                 # Clean pacing_rate and delivery_rate: remove text, convert to float Mbps
#                 for col in ["pacing_rate", "delivery_rate"]:
#                     if col in df.columns:
#                         # Remove non-numeric characters and convert
#                         df[col] = df[col].astype(str).str.replace(r'[^\d\.]+', '', regex=True)
#                         df[col] = pd.to_numeric(df[col], errors='coerce')

#                 # Convert pacing_gain and inflight_data to numeric
#                 for col in ["pacing_gain", "inflight_data"]:
#                     if col in df.columns:
#                         df[col] = pd.to_numeric(df[col], errors='coerce')

#                 df["label"] = name
#                 current_available_flows[name] = df
#             except Exception as e:
#                 print(f"Error loading {filename}: {e}")
#                 continue
#     return current_available_flows

# # --- Callback to update scenario options ---
# @app.callback(
#     Output("scenario-select", "options"),
#     Output("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value")
# )
# def set_scenario_options(aqm_selected, direction_selected):
#     current_flows = load_data_for_aqm_direction(aqm_selected, direction_selected)
#     current_flow_scenarios = {}

#     for f1_name in cca_names:
#         for f2_name in cca_names:
#             if f1_name in current_flows and f2_name in current_flows:
#                 scenario_key = f"{f1_name} vs {f2_name}"
#                 current_flow_scenarios[scenario_key] = (current_flows[f1_name].copy(), current_flows[f2_name].copy())

#     options = [{"label": k, "value": k} for k in sorted(current_flow_scenarios.keys())]
#     default_value = options[0]["value"] if options else None
#     return options, default_value

# # --- Callback to update plot ---
# @app.callback(
#     Output("metric-plot", "src"),
#     Input("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value"),
#     Input("metric-select", "value")
# )
# def update_plot(scenario, aqm, direction, selected_metrics):
#     current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

#     if not scenario or not selected_metrics:
#         # Return empty image
#         return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

#     f1_name, f2_name = scenario.split(" vs ")

#     if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
#         fig, ax = plt.subplots(figsize=(4, 3))
#         ax.text(0.5, 0.5,
#                 f"Data missing for '{scenario}' with AQM '{aqm}' and Direction '{direction}'.\n"
#                 "Please ensure CSV files like '{CCA}_{AQM}_{Direction}.csv' exist.",
#                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#                 fontsize=20, color='red')
#         ax.axis('off')
#         buf = io.BytesIO()
#         plt.savefig(buf, format="png", bbox_inches='tight', dpi=600)
#         plt.close(fig)
#         buf.seek(0)
#         return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

#     df1 = current_flows_for_plot[f1_name].copy()
#     df2 = current_flows_for_plot[f2_name].copy()

#     for df in [df1, df2]:
#         for metric in selected_metrics:
#             if metric in df.columns:
#                 df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()
#             else:
#                 df[f"{metric}_smoothed"] = None
#                 print(f"Warning: Metric '{metric}' not found in CSV for {df['label'].iloc[0]}.")

#     num_metrics = len(selected_metrics)
#     fig, axs = plt.subplots(num_metrics, 1, figsize=(8,4 * num_metrics), sharex=True)
#     fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=20)

#     if num_metrics == 1:
#         axs = [axs]

#     for i, metric in enumerate(selected_metrics):
#         if f"{metric}_smoothed" in df1.columns and df1[f"{metric}_smoothed"] is not None and not df1[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df1["Time"], df1[f"{metric}_smoothed"],
#                         label=df1["label"].iloc[0],
#                         color=custom_colors.get(df1["label"].iloc[0], "black"),
#                         linestyle="-", linewidth=2)

#         if f"{metric}_smoothed" in df2.columns and df2[f"{metric}_smoothed"] is not None and not df2[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df2["Time"], df2[f"{metric}_smoothed"],
#                         label=df2["label"].iloc[0],
#                         color=custom_colors.get(df2["label"].iloc[0], "black"),
#                         linestyle="-", linewidth=2)

#         axs[i].set_ylabel(metric_labels.get(metric, metric), fontsize=20)
#         axs[i].grid(True, linestyle='--', alpha=0.3)
#         axs[i].legend(loc='upper right', fontsize=20)

#         axs[i].tick_params(axis='both', which='major', labelsize=22)

#     axs[-1].set_xlabel("Time (s)", fontsize=20)
#     axs[-1].tick_params(axis='x', labelsize=20)
#     plt.tight_layout(rect=[0, 0, 1, 0.96])

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png", bbox_inches='tight', dpi=600)
#     plt.close(fig)
#     buf.seek(0)
#     return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")
# app.run(debug=True)

# import dash
# from dash import dcc, html, Input, Output
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# import base64
# import os
# import itertools # Although not directly used for scenarios, useful for combinations

# # --- File and Metric Setup ---
# # Base CCA names that you are testing. Used to construct filenames.
# cca_names = ["CUBIC", "BBRv1", "BBRv2", "BBRv3","BBRv3_Features"]

# # metric_labels = {
# #     "throughput_mbps": "Throughput (Mbps)",
# #     "rtt_ms": "RTT (ms)",
# #     "jitter_ms": "Jitter (ms)",
# #     "cwnd_bytes": "Congestion Window (Bytes)",
# #     "retransmits": "Retransmissions"
# #     # "pacing_rate": "Pacing Rate (Mbps)"
# #     # "delivery_rate": "Delivery Rate (Mbps)"
# #     # "min_rtt": "Minimum RTT (ms)"

# #     # Add other metrics here if they exist in your CSVs and you want to plot them
# # }

# metric_labels = {
#     "throughput_mbps": "Throughput (Mbps)",
#     "rtt_ms": "RTT (ms)",
#     "jitter_ms": "Jitter (ms)",
#     "cwnd_bytes": "Congestion Window (Bytes)",
#     "retransmits": "Retransmissions",
#     "pacing_rate": "Pacing Rate",
#     "delivery_rate": "Delivery Rate",
#     "pacing_gain": "Pacing Gain",
#     "inflight_data": "Data Inflight"
# }


# custom_colors = {
#     "CUBIC": "darkred",
#     "BBRv1": "purple",
#     "BBRv2": "darkgreen",
#     "BBRv3": "blue",
#     "BBRv3_Features": "pink"
# }

# # --- Dash App ---
# app = dash.Dash(__name__)
# app.title = "TCP Metrics Visualizer"

# # Load topology image
# # Ensure this path is correct on the system where you run the Dash app
# topo_image_path = "/home/sit/Desktop/demo_visulize/home_security.jpeg"
# topo_base64 = None
# if os.path.exists(topo_image_path):
#     with open(topo_image_path, "rb") as img_file:
#         topo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# app.layout = html.Div(style={
#     "fontFamily": "'Segoe UI', sans-serif",
#     "background": "linear-gradient(135deg, #e0f7fa, #f1f8ff)",
#     "minHeight": "100vh",
#     "padding": "20px"
# }, children=[

#     html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px", "minHeight": "calc(100vh - 40px)"}, children=[
        
#         # --- Left Panel: Network Topology ---
#         html.Div([
#             html.H3("Network Topology", style={"color": "#1a237e", "marginBottom": "10px", "textAlign": "center"}),
#             html.Img(
#                 src=f"data:image/png;base64,{topo_base64}",
#                 style={"width": "100%", "height": "calc(100% -0px)", "objectFit": "contain", "borderRadius": "12px", "border": "2px solid #ccc"}
#             ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f", "textAlign": "center"})
#         ], style={
#             "flex": "1", # Takes 1 unit of available space
#             "padding": "20px",
#             "backgroundColor": "#ffffff",
#             "borderRadius": "12px",
#             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)",
#             "display": "flex",
#             "flexDirection": "column",
#             "height": "100%", # Make it take full height of its parent flex container
#             "justifyContent": "flex-start",
#             "alignItems": "center"
#         }),

#         # --- Right Panel: Dashboard Controls and Plot ---
#         html.Div([
#             html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

#             html.Div([
#                 html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="aqm-select",
#                     options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "CAKE"]],
#                     value="PFIFO", # Default selected AQM
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="direction-select",
#                     options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
#                     value="Upload", # Default selected direction
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="scenario-select",
#                     # Options and initial value will be set by the callback
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="metric-select",
#                     options=[{"label": label, "value": key} for key, label in metric_labels.items()],
#                     value=["throughput_mbps", "rtt_ms"], # Default selected metrics
#                     multi=True,
#                     placeholder="Choose one or more metrics",
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Img(id="metric-plot", style={
#                     "width": "100%",
#                     "border": "2px solid #ccc",
#                     "borderRadius": "12px",
#                     "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
#                 })
#             ])
#         ], style={
#             "flex": "2", # Takes 2 units of available space (so it's twice as wide as the left panel)
#             "padding": "20px",
#             "backgroundColor": "#ffffff",
#             "borderRadius": "12px",
#             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
#         })
#     ])
# ])

# # --- Helper function to load data based on AQM and Direction ---
# def load_data_for_aqm_direction(aqm_type, direction_type):
#     """
#     Loads and preprocesses dataframes for a given AQM type and direction.
#     Assumes file names like 'CCA_AQM_DIRECTION.csv' (e.g., 'Cubic_PFIFO_Upload.csv')
#     """
#     current_available_flows = {}
#     for name in cca_names: # Iterate through defined CCA names (Cubic, BBRv1, etc.)
#         filename = f"{name}_{aqm_type}_{direction_type}.csv"
#         if os.path.exists(filename):
#             try:
#                 df = pd.read_csv(filename)
#                 # Ensure 'time_sec' column exists before assigning to 'Time'
#                 if "time_sec" in df.columns:
#                     df["Time"] = df["time_sec"]
#                 else:
#                     print(f"Warning: 'time_sec' column not found in {filename}. Plotting may be affected.")
#                     df["Time"] = df.index # Fallback to DataFrame index
                
#                 df["label"] = name # Assign the CCA name as a label for plotting
#                 current_available_flows[name] = df
#             except Exception as e:
#                 print(f"Error loading {filename}: {e}")
#                 continue
#     return current_available_flows

# # --- Callback to update scenario dropdown options based on AQM and Direction ---
# @app.callback(
#     Output("scenario-select", "options"),
#     Output("scenario-select", "value"), # Also reset selected value when options change
#     Input("aqm-select", "value"),
#     Input("direction-select", "value")
# )
# def set_scenario_options(aqm_selected, direction_selected):
#     current_flows = load_data_for_aqm_direction(aqm_selected, direction_selected)
    
#     current_flow_scenarios = {}
    
#     # Generate all combinations of two flows (Cubic, BBRv1, etc.), including self-vs-self
#     # Ensure both CCAs in a pair are actually available for the selected AQM/Direction
#     for f1_name in cca_names:
#         for f2_name in cca_names:
#             if f1_name in current_flows and f2_name in current_flows:
#                 # To handle unique scenarios (e.g., "Cubic vs BBRv1" is same as "BBRv1 vs Cubic" for options list)
#                 # You can decide if you want both or just one. Here, I'm keeping both for explicit selection if desired,
#                 # but sorting the names ensures consistent scenario naming like "BBRv1 vs Cubic" not "Cubic vs BBRv1" if you want.
#                 # For clarity, let's just make sure both exist and name consistently:
#                 # scenario_key = " vs ".join(sorted([f1_name, f2_name])) # Uncomment if you only want one entry per pair
#                 scenario_key = f"{f1_name} vs {f2_name}" # This matches your request for explicit combinations
#                 current_flow_scenarios[scenario_key] = (current_flows[f1_name].copy(), current_flows[f2_name].copy())

#     options = [{"label": k, "value": k} for k in sorted(current_flow_scenarios.keys())]
    
#     # Set default value to the first available scenario, or None if no scenarios are found
#     default_value = options[0]["value"] if options else None
    
#     return options, default_value

# # --- Plot Callback ---
# @app.callback(
#     Output("metric-plot", "src"),
#     Input("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value"),
#     Input("metric-select", "value")
# )
# def update_plot(scenario, aqm, direction, selected_metrics):
#     # Retrieve the relevant dataframes based on current AQM and Direction selections
#     current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

#     # Handle cases where no scenario or metrics are selected, or data is missing
#     if not scenario or not selected_metrics:
#         return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

#     # Parse the selected scenario string to get the two CCA names (e.g., "Cubic", "BBRv3")
#     f1_name, f2_name = scenario.split(" vs ")

#     # Verify that data for both selected flows is actually available for the current AQM/Direction
#     if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
#         print(f"Error: Data for scenario '{scenario}' not found for AQM '{aqm}' and Direction '{direction}'.")
#         # Return a blank image with a text indicating missing data
#         fig, ax = plt.subplots(figsize=(8, 4))
#         ax.text(0.5, 0.5, f"Data missing for '{scenario}' with AQM '{aqm}' and Direction '{direction}'.\n"
#                             "Please ensure CSV files like '{CCA}_{AQM}_{Direction}.csv' exist.", 
#                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#                 fontsize=14, color='red')
#         ax.axis('off') # Hide axes
#         buf = io.BytesIO()
#         plt.savefig(buf, format="png", bbox_inches='tight', dpi=100)
#         plt.close(fig)
#         buf.seek(0)
#         return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

#     # Get the actual DataFrame copies for plotting
#     df1 = current_flows_for_plot[f1_name].copy()
#     df2 = current_flows_for_plot[f2_name].copy()

#     # Apply smoothing to selected metrics
#     for df in [df1, df2]:
#         for metric in selected_metrics: # Only smooth selected metrics to save computation
#             if metric in df.columns:
#                 df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()
#             else:
#                 # If a selected metric column is missing, set smoothed column to None
#                 df[f"{metric}_smoothed"] = None 
#                 print(f"Warning: Metric '{metric}' not found in CSV for {df['label'].iloc[0]}.")


#     num_metrics = len(selected_metrics)
#     # Adjust figure size dynamically based on number of metrics for better readability
#     fig, axs = plt.subplots(num_metrics, 1, figsize=(12, 4 * num_metrics), sharex=True)
#     # Add full scenario description to the plot title
#     fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=16)

#     # Ensure axs is always an iterable list, even if only one subplot
#     if num_metrics == 1:
#         axs = [axs]

#     for i, metric in enumerate(selected_metrics):
#         # Plot only if smoothed data is available and not all NaN (e.g., if column was missing)
#         if f"{metric}_smoothed" in df1.columns and df1[f"{metric}_smoothed"] is not None and not df1[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df1["Time"], df1[f"{metric}_smoothed"],
#                         label=df1["label"].iloc[0], 
#                         color=custom_colors.get(df1["label"].iloc[0], "black"), 
#                         linestyle="-", linewidth=2)
        
#         if f"{metric}_smoothed" in df2.columns and df2[f"{metric}_smoothed"] is not None and not df2[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df2["Time"], df2[f"{metric}_smoothed"],
#                         label=df2["label"].iloc[0], 
#                         color=custom_colors.get(df2["label"].iloc[0], "black"), 
#                         linestyle="-", linewidth=2)
        
#         axs[i].set_ylabel(metric_labels[metric])
#         axs[i].grid(True, linestyle='--', alpha=0.7) # Add grid for easier reading
#         axs[i].legend(loc='upper right') # Consistent legend placement
#         # axs[i].tick_params(axis='x', rotation=45) # Rotate x-axis labels if needed for long timeseries

#     axs[-1].set_xlabel("Time (s)")
#     # Adjust layout to prevent titles/labels from overlapping
#     plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust rect to make space for suptitle

#     # Save plot to a BytesIO buffer and convert to base64 for Dash display
#     buf = io.BytesIO()
#     plt.savefig(buf, format="png", bbox_inches='tight', dpi=100) # Use higher DPI for better image quality
#     plt.close(fig) # Close the figure to free memory
#     buf.seek(0)
#     return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

# # --- Run the App ---
# if __name__ == "__main__":
#     # A simple check to alert the user if no files are found at all for the initial load.
#     # The real dynamic loading happens in the callbacks.
#     initial_flows_check = load_data_for_aqm_direction("PFIFO", "Upload") 
#     if not initial_flows_check:
#         print("\n" + "="*80)
#         print("WARNING: No initial data files found for 'PFIFO' 'Upload'.")
#         print("Please ensure your CSV files are named like 'CCA_AQM_Direction.csv' ")
#         print("(e.g., 'Cubic_PFIFO_Upload.csv') and are in the same directory.")
#         print("The dashboard will still start, but may show no scenarios initially.")
#         print("="*80 + "\n")
    
#     app.run (debug=True) # Run in debug mode for easier development








# import dash
# from dash import dcc, html, Input, Output
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# import base64
# import os
# import itertools

# # --- File and Metric Setup ---
# # Base CCA names that you are testing. Used to construct filenames.
# cca_names = ["Cubic", "BBRv1", "BBRv2", "BBRv3"] # Keep these consistent with your file naming

# metric_labels = {
#     "throughput_mbps": "Throughput (Mbps)",
#     "rtt_ms": "RTT (ms)",
#     "jitter_ms": "Jitter (ms)",
#     "cwnd_bytes": "Congestion Window (Bytes)",
#     "retransmits": "Retransmissions"
#     # Add other metrics here if they exist in your CSVs and you want to plot them
# }

# # Custom colors for each CCA for consistent plotting
# custom_colors = {
#     "Cubic": "#E53935", # Material Design Red
#     "BBRv1": "#8E24AA", # Material Design Purple
#     "BBRv2": "#4CAF50", # Material Design Green
#     "BBRv3": "#1976D2"  # Material Design Blue (deeper than default)
# }

# # --- Dash App ---
# app = dash.Dash(__name__)
# app.title = "TCP Metrics Visualizer"

# # Load topology image
# # Ensure this path is correct on the system where you run the Dash app
# # IMPORTANT: For Dash deployments, it's often better to place images in the 'assets' folder
# # and reference them as '/assets/image_name.png'
# topo_image_path = "/home/sit/Desktop/demo_visulize/home_security.jpeg"
# topo_base64 = None
# if os.path.exists(topo_image_path):
#     with open(topo_image_path, "rb") as img_file:
#         topo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# app.layout = html.Div(style={
#     "fontFamily": "'Roboto', sans-serif", # Changed font to Roboto (commonly available)
#     "background": "linear-gradient(135deg, #e0f7fa, #f1f8ff)", # Subtle blue-ish gradient
#     "minHeight": "100vh",
#     "padding": "25px", # Increased padding
#     "display": "flex",
#     "flexDirection": "column",
#     "gap": "25px"
# }, children=[
#     html.H1("TCP Flow Metrics Dashboard", style={
#         "textAlign": "center",
#         "color": "#0D47A1", # Darker blue for main title
#         "marginBottom": "20px",
#         "fontSize": "2.5em", # Larger font size
#         "fontWeight": "bold",
#         "textShadow": "1px 1px 2px rgba(0,0,0,0.1)" # Subtle text shadow
#     }),

#     html.Div(style={"display": "flex", "flexDirection": "row", "gap": "25px", "flexWrap": "wrap"}, children=[ # Added flexWrap for responsiveness
        
#         # --- Left Panel: Network Topology ---
#         html.Div([
#             html.H3("Network Topology", style={"color": "#1A237E", "marginBottom": "15px", "textAlign": "center", "fontSize": "1.8em"}),
#             html.Img(
#                 src=f"data:image/png;base64,{topo_base64}",
#                 style={
#                     "width": "100%",
#                     "height": "auto", # 'auto' to maintain aspect ratio
#                     "maxHeight": "400px", # Max height for image
#                     "objectFit": "contain",
#                     "borderRadius": "12px",
#                     "border": "2px solid #BBDEFB", # Light blue border
#                     "boxShadow": "0px 4px 15px rgba(0, 0, 0, 0.15)" # Stronger shadow
#                 }
#             ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#D32F2F", "textAlign": "center", "padding": "20px"})
#         ], style={
#             "flex": "1",
#             "minWidth": "300px", # Ensure it doesn't get too small on narrow screens
#             "padding": "25px", # Increased padding
#             "backgroundColor": "#FFFFFF",
#             "borderRadius": "15px", # More rounded corners
#             "boxShadow": "0px 5px 20px rgba(0, 0, 0, 0.15)", # Stronger shadow for cards
#             "display": "flex",
#             "flexDirection": "column",
#             "alignItems": "center"
#         }),

#         # --- Right Panel: Dashboard Controls and Plot ---
#         html.Div([
#             html.H3("Analysis Controls", style={"textAlign": "center", "color": "#1A237E", "marginBottom": "25px", "fontSize": "1.8em"}), # New title for controls
            
#             # --- Controls Section ---
#             html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "20px", "marginBottom": "30px"}, children=[
#                 html.Div([
#                     html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#424242", "marginBottom": "8px", "display": "block"}),
#                     dcc.Dropdown(
#                         id="aqm-select",
#                         options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "Cake"]],
#                         value="PFIFO",
#                         clearable=False,
#                         style={"color": "#000", "minWidth": "150px"} # Ensure dropdowns don't collapse too much
#                     )
#                 ]),
#                 html.Div([
#                     html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#424242", "marginBottom": "8px", "display": "block"}),
#                     dcc.Dropdown(
#                         id="direction-select",
#                         options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
#                         value="Upload",
#                         clearable=False,
#                         style={"color": "#000", "minWidth": "150px"}
#                     )
#                 ]),
#                 html.Div([
#                     html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#424242", "marginBottom": "8px", "display": "block"}),
#                     dcc.Dropdown(
#                         id="scenario-select",
#                         clearable=False,
#                         style={"color": "#000", "minWidth": "150px"}
#                     )
#                 ]),
#                 html.Div([
#                     html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#424242", "marginBottom": "8px", "display": "block"}),
#                     dcc.Dropdown(
#                         id="metric-select",
#                         options=[{"label": label, "value": key} for key, label in metric_labels.items()],
#                         value=["throughput_mbps", "rtt_ms"],
#                         multi=True,
#                         placeholder="Choose one or more metrics",
#                         style={"color": "#000", "minWidth": "150px"}
#                     )
#                 ])
#             ]),

#             # --- Plot Area ---
#             dcc.Loading( # Added loading spinner for better UX
#                 id="loading-plot",
#                 type="cube", # You can choose 'default', 'graph', 'cube', etc.
#                 children=[
#                     html.Img(id="metric-plot", style={
#                         "width": "100%",
#                         "border": "2px solid #CFD8DC", # Lighter border for the plot
#                         "borderRadius": "12px",
#                         "boxShadow": "0 4px 12px rgba(0,0,0,0.1)", # Subtle shadow
#                         "backgroundColor": "#FFFFFF", # Ensure plot background is white
#                         "minHeight": "300px", # Minimum height for the plot area
#                         "objectFit": "contain"
#                     })
#                 ]
#             )
#         ], style={
#             "flex": "2",
#             "minWidth": "450px", # Ensure it doesn't get too small
#             "padding": "25px", # Increased padding
#             "backgroundColor": "#FFFFFF",
#             "borderRadius": "15px",
#             "boxShadow": "0px 5px 20px rgba(0, 0, 0, 0.15)",
#             "display": "flex",
#             "flexDirection": "column",
#             "height": "auto" # Allow height to adjust to content
#         })
#     ])
# ])

# # --- Helper function to load data based on AQM and Direction ---
# def load_data_for_aqm_direction(aqm_type, direction_type):
#     """
#     Loads and preprocesses dataframes for a given AQM type and direction.
#     Assumes file names like 'CCA_AQM_DIRECTION.csv' (e.g., 'Cubic_PFIFO_Upload.csv')
#     """
#     current_available_flows = {}
#     for name in cca_names: # Iterate through defined CCA names (Cubic, BBRv1, etc.)
#         filename = f"{name}_{aqm_type}_{direction_type}.csv"
#         # Look for files in the current directory (where the Dash app is run)
#         # If your files are in a specific subfolder (e.g., 'data/'), prepend that:
#         # full_path = os.path.join("data", filename)
#         if os.path.exists(filename):
#             try:
#                 df = pd.read_csv(filename)
#                 if "time_sec" in df.columns:
#                     df["Time"] = df["time_sec"]
#                 else:
#                     print(f"Warning: 'time_sec' column not found in {filename}. Plotting may be affected.")
#                     df["Time"] = df.index # Fallback to DataFrame index if 'time_sec' is missing
                
#                 df["label"] = name # Assign the CCA name as a label for plotting
#                 current_available_flows[name] = df
#             except Exception as e:
#                 print(f"Error loading {filename}: {e}")
#                 continue
#     return current_available_flows

# # --- Callback to update scenario dropdown options based on AQM and Direction ---
# @app.callback(
#     Output("scenario-select", "options"),
#     Output("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value")
# )
# def set_scenario_options(aqm_selected, direction_selected):
#     current_flows = load_data_for_aqm_direction(aqm_selected, direction_selected)
    
#     available_cca_for_scenario = list(current_flows.keys()) # CCAs that have data for selected AQM/Direction
    
#     scenario_options = []
#     # Generate combinations of 2 CCAs from the available ones
#     # Use sorted() to ensure "Cubic vs BBRv1" and "BBRv1 vs Cubic" don't both appear if you only want one.
#     # If you want all permutations (Cubic vs BBRv1 AND BBRv1 vs Cubic), use itertools.product
#     # For unique pairs and self-vs-self:
#     for f1_name in sorted(available_cca_for_scenario):
#         for f2_name in sorted(available_cca_for_scenario): # Iterate all available for second flow
#              scenario_label = f"{f1_name} vs {f2_name}"
#              scenario_options.append({"label": scenario_label, "value": scenario_label})

#     # Sort options alphabetically for better UX
#     options = sorted(scenario_options, key=lambda x: x['label'])

#     default_value = options[0]["value"] if options else None
    
#     return options, default_value

# # --- Plot Callback ---
# @app.callback(
#     Output("metric-plot", "src"),
#     Input("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value"),
#     Input("metric-select", "value")
# )
# def update_plot(scenario, aqm, direction, selected_metrics):
#     # Handle initial state or missing selections
#     if not scenario or not selected_metrics:
#         # Return a blank transparent image or a placeholder
#         return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

#     # Load data for the current AQM and Direction
#     current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

#     # Parse the selected scenario string to get the two CCA names (e.g., "Cubic", "BBRv3")
#     f1_name, f2_name = scenario.split(" vs ")

#     # Verify that data for both selected flows is actually available for the current AQM/Direction
#     if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
#         print(f"Error: Data for scenario '{scenario}' not found for AQM '{aqm}' and Direction '{direction}'.")
#         # Return a blank image with a text indicating missing data
#         fig, ax = plt.subplots(figsize=(10, 5)) # Adjusted size for message
#         ax.text(0.5, 0.5, f"Data missing for '{scenario}' with AQM '{aqm}' and Direction '{direction}'.\n"
#                             "Please ensure CSV files like '{CCA}_{AQM}_{Direction}.csv' exist.", 
#                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#                 fontsize=14, color='#D32F2F', wrap=True) # Red color for error message
#         ax.axis('off') # Hide axes
#         buf = io.BytesIO()
#         plt.savefig(buf, format="png", bbox_inches='tight', dpi=150) # Higher DPI for error message too
#         plt.close(fig)
#         buf.seek(0)
#         return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

#     # Get the actual DataFrame copies for plotting
#     df1 = current_flows_for_plot[f1_name].copy()
#     df2 = current_flows_for_plot[f2_name].copy()

#     # Create subplots dynamically based on the number of selected metrics
#     num_metrics = len(selected_metrics)
#     fig, axs = plt.subplots(num_metrics, 1, figsize=(12, 4.5 * num_metrics), sharex=True) # Adjust figure height dynamically
    
#     # Add full scenario description to the plot title
#     # Using specific font sizes for professionalism
#     fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=18, color="#0D47A1", fontweight='bold')

#     # Ensure axs is always an iterable list, even if only one subplot
#     if num_metrics == 1:
#         axs = [axs]

#     for i, metric in enumerate(selected_metrics):
#         # Apply smoothing to the current metric
#         df1_smoothed_data = None
#         df2_smoothed_data = None
        
#         if metric in df1.columns:
#             df1_smoothed_data = df1[metric].rolling(window=10, min_periods=1).mean()
#         else:
#             print(f"Warning: Metric '{metric}' not found in CSV for {df1['label'].iloc[0]}. Skipping plot for this metric/flow.")

#         if metric in df2.columns:
#             df2_smoothed_data = df2[metric].rolling(window=10, min_periods=1).mean()
#         else:
#             print(f"Warning: Metric '{metric}' not found in CSV for {df2['label'].iloc[0]}. Skipping plot for this metric/flow.")

#         # Plot only if smoothed data is available and not all NaN (e.g., if column was missing)
#         if df1_smoothed_data is not None and not df1_smoothed_data.isnull().all():
#             axs[i].plot(df1["Time"], df1_smoothed_data,
#                         label=df1["label"].iloc[0], 
#                         color=custom_colors.get(df1["label"].iloc[0], "#212121"), # Fallback to dark grey
#                         linestyle="-", linewidth=2.5) # Slightly thicker lines
        
#         if df2_smoothed_data is not None and not df2_smoothed_data.isnull().all():
#             axs[i].plot(df2["Time"], df2_smoothed_data,
#                         label=df2["label"].iloc[0], 
#                         color=custom_colors.get(df2["label"].iloc[0], "#757575"), # Fallback to medium grey
#                         linestyle="-", linewidth=2.5)
        
#         axs[i].set_ylabel(metric_labels[metric], fontsize=14, color="#333") # Axis label font size and color
#         axs[i].grid(True, linestyle='--', alpha=0.6, color="#E0E0E0") # Lighter grid lines
#         axs[i].legend(loc='upper right', fontsize=12, frameon=True, shadow=True, fancybox=True) # Enhanced legend

#         # Specific Y-axis limit for Throughput
#         if metric == "throughput_mbps":
#             axs[i].set_ylim(0, 10.5) # Slightly above 10 Mbps to show the ceiling clearly
#             axs[i].axhline(y=10, color='grey', linestyle=':', linewidth=1.5, label='10 Mbps Bottleneck')
#             axs[i].legend(loc='upper right', fontsize=12, frameon=True, shadow=True, fancybox=True) # Re-add legend to include bottleneck line

#         axs[i].tick_params(axis='both', which='major', labelsize=12) # Tick label font size

#     axs[-1].set_xlabel("Time (s)", fontsize=14, color="#333") # X-axis label font size and color
    
#     # Adjust layout to prevent titles/labels from overlapping
#     plt.tight_layout(rect=[0, 0, 1, 0.94]) # Adjust rect to make space for suptitle and padding

#     # Save plot to a BytesIO buffer and convert to base64 for Dash display
#     buf = io.BytesIO()
#     plt.savefig(buf, format="png", bbox_inches='tight', dpi=200) # Increased DPI to 200 for better image quality
#     plt.close(fig) # Close the figure to free memory
#     buf.seek(0)
#     return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

# # --- Run the App ---
# if __name__ == "__main__":
#     # A simple check to alert the user if no files are found at all for the initial load.
#     initial_flows_check = load_data_for_aqm_direction("PFIFO", "Upload") 
#     if not initial_flows_check:
#         print("\n" + "="*80)
#         print("WARNING: No initial data files found for 'PFIFO' 'Upload'.")
#         print("Please ensure your CSV files are named like 'CCA_AQM_Direction.csv' ")
#         print("(e.g., 'Cubic_PFIFO_Upload.csv') and are in the same directory as this script,")
#         print("or adjust the 'filename' construction in load_data_for_aqm_direction.")
#         print("The dashboard will still start, but may show no scenarios initially.")
#         print("="*80 + "\n")
    
#     # THE ONLY CHANGE NEEDED IS HERE:
#     app.run(debug=True) # Changed from app.run_server to app.run

