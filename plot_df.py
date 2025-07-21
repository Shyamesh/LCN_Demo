


# # import dash
# # from dash import dcc, html, Input, Output
# # import pandas as pd
# # import matplotlib.pyplot as plt
# # import io
# # import base64
# # import os
# # import itertools

# # # --- File and Metric Setup ---
# # flow_files = {
# #     "Cubic": "cubic_flow.csv",
# #     "BBRv1": "bbrv1_flow.csv",
# #     "BBRv2": "bbrv2_flow.csv",
# #     "BBRv3": "bbrv3_flow.csv"
# # }

# # metric_labels = {
# #     "throughput_mbps": "Throughput (Mbps)",
# #     "rtt_ms": "RTT (ms)",
# #     "jitter_ms": "Jitter (ms)",
# #     "cwnd_bytes": "Congestion Window (Bytes)",
# #     "retransmits": "Retransmissions"
# # }

# # custom_colors = {
# #     "Cubic": "darkred",
# #     "BBRv1": "purple",
# #     "BBRv2": "darkgreen",
# #     "BBRv3": "blue"
# # }

# # # --- Load available files ---
# # available_flows = {}
# # for name, filename in flow_files.items():
# #     if os.path.exists(filename):
# #         df = pd.read_csv(filename)
# #         df["Time"] = df["time_sec"]
# #         df["label"] = name
# #         available_flows[name] = df

# # # --- Generate all scenarios including self-vs-self ---
# # flow_scenarios = {}
# # for f1 in available_flows.keys():
# #     for f2 in available_flows.keys():
# #         scenario_name = f"{f1} vs {f2}"
# #         flow_scenarios[scenario_name] = (available_flows[f1].copy(), available_flows[f2].copy())

# # # --- Dash App ---
# # app = dash.Dash(__name__)
# # app.title = "TCP Metrics Visualizer"

# # # Load topology image
# # topo_image_path = "/home/sit/Desktop/demo_visulize/home_security.jpeg"
# # topo_base64 = None
# # if os.path.exists(topo_image_path):
# #     with open(topo_image_path, "rb") as img_file:
# #         topo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# # app.layout = html.Div(style={
# #     "fontFamily": "'Segoe UI', sans-serif",
# #     "background": "linear-gradient(135deg, #e0f7fa, #f1f8ff)",
# #     "minHeight": "100vh",
# #     "padding": "20px"
# # }, children=[

# #     html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px"}, children=[
        
# #         # --- Left Panel ---
# #         html.Div([
# #             html.H3("Network Topology", style={"color": "#1a237e"}),
# #             html.Img(
# #                 src=f"data:image/png;base64,{topo_base64}",
# #                 style={"width": "100%", "height": "auto", "borderRadius": "12px", "border": "2px solid #ccc"}
# #             ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f"})
# #         ], style={
# #             "flex": "1",
# #             "padding": "20px",
# #             "backgroundColor": "#ffffff",
# #             "borderRadius": "12px",
# #             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
# #         }),

# #         # --- Right Panel ---
# #         html.Div([
# #             html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

# #             html.Div([
# #                 html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
# #                 dcc.Dropdown(
# #                     id="aqm-select",
# #                     options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "Cake"]],
# #                     value="PFIFO",
# #                     clearable=False,
# #                     style={"color": "#000"}
# #                 )
# #             ], style={"marginBottom": "20px"}),

# #             html.Div([
# #                 html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
# #                 dcc.Dropdown(
# #                     id="scenario-select",
# #                     options=[{"label": k, "value": k} for k in sorted(flow_scenarios.keys())],
# #                     value=sorted(flow_scenarios.keys())[0],
# #                     clearable=False,
# #                     style={"color": "#000"}
# #                 )
# #             ], style={"marginBottom": "20px"}),

# #             html.Div([
# #                 html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#333"}),
# #                 dcc.Dropdown(
# #                     id="metric-select",
# #                     options=[{"label": label, "value": key} for key, label in metric_labels.items()],
# #                     value=["throughput_mbps", "rtt_ms"],
# #                     multi=True,
# #                     placeholder="Choose one or more metrics",
# #                     style={"color": "#000"}
# #                 )
# #             ], style={"marginBottom": "20px"}),

# #             html.Div([
# #                 html.Img(id="metric-plot", style={
# #                     "width": "100%",
# #                     "border": "2px solid #ccc",
# #                     "borderRadius": "12px",
# #                     "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
# #                 })
# #             ])
# #         ], style={
# #             "flex": "2",
# #             "padding": "20px",
# #             "backgroundColor": "#ffffff",
# #             "borderRadius": "12px",
# #             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
# #         })
# #     ])
# # ])

# # # --- Plot Callback ---
# # @app.callback(
# #     Output("metric-plot", "src"),
# #     Input("scenario-select", "value"),
# #     Input("aqm-select", "value"),
# #     Input("metric-select", "value")
# # )
# # def update_plot(scenario, aqm, selected_metrics):
# #     df1, df2 = flow_scenarios[scenario]

# #     for df in [df1, df2]:
# #         for metric in metric_labels:
# #             df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()

# #     num_metrics = len(selected_metrics)
# #     fig, axs = plt.subplots(num_metrics, 1, figsize=(10, 3.5 * num_metrics), sharex=True)
# #     fig.suptitle(f"{scenario} | AQM: {aqm}", fontsize=16)

# #     if num_metrics == 1:
# #         axs = [axs]

# #     for i, metric in enumerate(selected_metrics):
# #         axs[i].plot(df1["Time"], df1[f"{metric}_smoothed"],
# #                     label=df1["label"].iloc[0], color=custom_colors.get(df1["label"].iloc[0], "black"), linestyle="-", linewidth=2)
# #         axs[i].plot(df2["Time"], df2[f"{metric}_smoothed"],
# #                     label=df2["label"].iloc[0], color=custom_colors.get(df2["label"].iloc[0], "black"), linestyle="-", linewidth=2)
# #         axs[i].set_ylabel(metric_labels[metric])
# #         axs[i].grid(True)
# #         axs[i].legend()

# #     axs[-1].set_xlabel("Time (s)")
# #     plt.tight_layout(rect=[0, 0, 1, 0.97])

# #     buf = io.BytesIO()
# #     plt.savefig(buf, format="png")
# #     plt.close(fig)
# #     buf.seek(0)
# #     return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

# # # --- Run the App ---
# # if __name__ == "__main__":
# #     if not flow_scenarios:
# #         print("❌ No valid flow files found. Add CSV files like 'cubic_flow.csv', 'bbrv1_flow.csv' etc.")
# #     else:
# #         app.run(debug=True)



# import dash
# from dash import dcc, html, Input, Output
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# import base64
# import os
# import itertools

# # --- File and Metric Setup ---
# # Base CCA names for mapping to file names (used in the previous, more robust solution)
# # For this specific request, we'll revert to the original simplified loading
# # but keep the list for scenario generation.
# cca_names = ["Cubic", "BBRv1", "BBRv2", "BBRv3"] # Keep for scenario generation logic

# metric_labels = {
#     "throughput_mbps": "Throughput (Mbps)",
#     "rtt_ms": "RTT (ms)",
#     "jitter_ms": "Jitter (ms)",
#     "cwnd_bytes": "Congestion Window (Bytes)",
#     "retransmits": "Retransmissions"
# }

# custom_colors = {
#     "Cubic": "darkred",
#     "BBRv1": "purple",
#     "BBRv2": "darkgreen",
#     "BBRv3": "blue"
# }

# # --- Load available files ---
# # IMPORTANT: This original loading logic does NOT filter by AQM or Direction from filenames.
# # If you want to integrate AQM/Direction filtering as discussed previously,
# # you MUST use the more advanced loading logic provided in the previous response.
# # For *this* specific request (only topology figure sizing), we use your provided code.
# available_flows = {}
# flow_files_map = { # Renamed to avoid confusion with cca_names list
#     "Cubic": "cubic_flow.csv",
#     "BBRv1": "bbrv1_flow.csv",
#     "BBRv2": "bbrv2_flow.csv",
#     "BBRv3": "bbrv3_flow.csv"
# }
# for name, filename in flow_files_map.items():
#     if os.path.exists(filename):
#         try:
#             df = pd.read_csv(filename)
#             df["Time"] = df["time_sec"]
#             df["label"] = name
#             available_flows[name] = df
#         except Exception as e:
#             print(f"Error loading {filename}: {e}")
#             continue


# # --- Generate all scenarios including self-vs-self ---
# flow_scenarios = {}
# # Only generate scenarios if there are available flows
# if available_flows:
#     for f1 in available_flows.keys():
#         for f2 in available_flows.keys():
#             scenario_name = f"{f1} vs {f2}"
#             flow_scenarios[scenario_name] = (available_flows[f1].copy(), available_flows[f2].copy())
# else:
#     print("No flow data files found to generate scenarios.")


# # --- Dash App ---
# app = dash.Dash(__name__)
# app.title = "TCP Metrics Visualizer"

# # Load topology image
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

#     html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px", "minHeight": "calc(100vh - 40px)"}, children=[ # Added minHeight here
        
#         # --- Left Panel ---
#         html.Div([
#             html.H3("Network Topology", style={"color": "#1a237e", "marginBottom": "10px"}), # Added margin-bottom
#             html.Img(
#                 src=f"data:image/png;base64,{topo_base64}",
#                 style={"width": "100%", "height": "calc(100% - 40px)", "objectFit": "contain", "borderRadius": "12px", "border": "2px solid #ccc"} # Adjusted height and added objectFit
#             ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f"})
#         ], style={
#             "flex": "1",
#             "padding": "20px",
#             "backgroundColor": "#ffffff",
#             "borderRadius": "12px",
#             "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)",
#             "display": "flex", # Added flex display
#             "flexDirection": "column", # Arrange children in a column
#             "height": "100%", # Make it take full height of parent
#             "justifyContent": "flex-start", # Align content to the top
#             "alignItems": "center" # Center horizontally if content is smaller
#         }),

#         # --- Right Panel ---
#         html.Div([
#             html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

#             html.Div([
#                 html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="aqm-select",
#                     options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "Cake"]],
#                     value="PFIFO",
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),
            
#             # --- New Direction Dropdown (re-added from previous solution for completeness) ---
#             html.Div([
#                 html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="direction-select",
#                     options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
#                     value="Upload", # Default value
#                     clearable=False,
#                     style={"color": "#000"}
#                 )
#             ], style={"marginBottom": "20px"}),

#             html.Div([
#                 html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
#                 dcc.Dropdown(
#                     id="scenario-select",
#                     # Options will be populated by callback, as in the previous, more robust solution
#                     # For this specific request, the initial options will be from the hardcoded `flow_scenarios`
#                     options=[{"label": k, "value": k} for k in sorted(flow_scenarios.keys())] if flow_scenarios else [],
#                     value=sorted(flow_scenarios.keys())[0] if flow_scenarios else None,
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

# # --- Plot Callback ---
# @app.callback(
#     Output("metric-plot", "src"),
#     Input("scenario-select", "value"),
#     Input("aqm-select", "value"),
#     Input("direction-select", "value"), # Add direction as an input
#     Input("metric-select", "value")
# )
# def update_plot(scenario, aqm, direction, selected_metrics): # Update function signature
#     # Re-integrate the dynamic loading logic for robustness
#     # This assumes your CSVs are named like "Cubic_PFIFO_Upload.csv" etc.
    
#     # Helper to load data based on AQM and Direction
#     def load_data_for_aqm_direction(aqm_type, direction_type):
#         current_available_flows = {}
#         for name in cca_names:
#             filename = f"{name}_{aqm_type}_{direction_type}.csv"
#             if os.path.exists(filename):
#                 try:
#                     df = pd.read_csv(filename)
#                     df["Time"] = df["time_sec"]
#                     df["label"] = name
#                     current_available_flows[name] = df
#                 except Exception as e:
#                     print(f"Error loading {filename}: {e}")
#                     continue
#         return current_available_flows

#     # Load flows based on current AQM and Direction selections
#     current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

#     if not scenario or not selected_metrics:
#         # Return a blank image if no scenario or metrics are selected
#         return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

#     # Parse scenario name to get individual flow names
#     f1_name, f2_name = scenario.split(" vs ")

#     # Check if both flows are available for the current AQM/Direction
#     if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
#         print(f"Data for scenario '{scenario}' not found for AQM '{aqm}' and Direction '{direction}'.")
#         return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

#     df1 = current_flows_for_plot[f1_name].copy()
#     df2 = current_flows_for_plot[f2_name].copy()

#     for df in [df1, df2]:
#         for metric in metric_labels:
#             if metric in df.columns: # Ensure metric column exists
#                 df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()
#             else:
#                 df[f"{metric}_smoothed"] = None # Handle missing metric by setting to None

#     num_metrics = len(selected_metrics)
#     fig, axs = plt.subplots(num_metrics, 1, figsize=(12, 4 * num_metrics), sharex=True)
#     fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=16) # Add direction to title

#     if num_metrics == 1:
#         axs = [axs]

#     for i, metric in enumerate(selected_metrics):
#         # Only plot if smoothed data is available
#         if f"{metric}_smoothed" in df1.columns and df1[f"{metric}_smoothed"] is not None and not df1[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df1["Time"], df1[f"{metric}_smoothed"],
#                         label=df1["label"].iloc[0], color=custom_colors.get(df1["label"].iloc[0], "black"), linestyle="-", linewidth=2)
        
#         if f"{metric}_smoothed" in df2.columns and df2[f"{metric}_smoothed"] is not None and not df2[f"{metric}_smoothed"].isnull().all():
#             axs[i].plot(df2["Time"], df2[f"{metric}_smoothed"],
#                         label=df2["label"].iloc[0], color=custom_colors.get(df2["label"].iloc[0], "black"), linestyle="-", linewidth=2)
        
#         axs[i].set_ylabel(metric_labels[metric])
#         axs[i].grid(True, linestyle='--', alpha=0.7)
#         axs[i].legend(loc='upper right')
#         axs[i].tick_params(axis='x', rotation=45)

#     axs[-1].set_xlabel("Time (s)")
#     plt.tight_layout(rect=[0, 0, 1, 0.96])

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png", bbox_inches='tight', dpi=100)
#     plt.close(fig)
#     buf.seek(0)
#     return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

# # --- Run the App ---
# if __name__ == "__main__":
#     # Remove the initial hardcoded flow_files loading if using the dynamic loading
#     # The initial check is now less critical as data is loaded on demand.
#     # We still need to ensure the scenario dropdown is populated correctly on initial load.
    
#     # Initial population of scenario dropdown for the first render
#     # This requires the set_scenario_options callback to run.
#     # The app.run_server will handle the initial callback execution.
#     print("Starting Dash app. Ensure your CSV files are named like 'CCA_AQM_Direction.csv' (e.g., 'Cubic_PFIFO_Upload.csv') in the same directory.")
#     app.run_server(debug=True)




import dash
from dash import dcc, html, Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import itertools # Although not directly used for scenarios, useful for combinations

# --- File and Metric Setup ---
# Base CCA names that you are testing. Used to construct filenames.
cca_names = ["Cubic", "BBRv1", "BBRv2", "BBRv3"]

metric_labels = {
    "throughput_mbps": "Throughput (Mbps)",
    "rtt_ms": "RTT (ms)",
    "jitter_ms": "Jitter (ms)",
    "cwnd_bytes": "Congestion Window (Bytes)",
    "retransmits": "Retransmissions"
    # Add other metrics here if they exist in your CSVs and you want to plot them
}

custom_colors = {
    "Cubic": "darkred",
    "BBRv1": "purple",
    "BBRv2": "darkgreen",
    "BBRv3": "blue"
}

# --- Dash App ---
app = dash.Dash(__name__)
app.title = "TCP Metrics Visualizer"

# Load topology image
# Ensure this path is correct on the system where you run the Dash app
topo_image_path = "/home/sit/Desktop/demo_visulize/home_security.jpeg"
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
        
        # --- Left Panel: Network Topology ---
        html.Div([
            html.H3("Network Topology", style={"color": "#1a237e", "marginBottom": "10px", "textAlign": "center"}),
            html.Img(
                src=f"data:image/png;base64,{topo_base64}",
                style={"width": "100%", "height": "calc(100% -0px)", "objectFit": "contain", "borderRadius": "12px", "border": "2px solid #ccc"}
            ) if topo_base64 else html.Div("Topology image not found.", style={"color": "#d32f2f", "textAlign": "center"})
        ], style={
            "flex": "1", # Takes 1 unit of available space
            "padding": "20px",
            "backgroundColor": "#ffffff",
            "borderRadius": "12px",
            "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)",
            "display": "flex",
            "flexDirection": "column",
            "height": "100%", # Make it take full height of its parent flex container
            "justifyContent": "flex-start",
            "alignItems": "center"
        }),

        # --- Right Panel: Dashboard Controls and Plot ---
        html.Div([
            html.H2("TCP Flow Metrics Dashboard", style={"textAlign": "center", "color": "#0d47a1"}),

            html.Div([
                html.Label("Select AQM:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="aqm-select",
                    options=[{"label": x, "value": x} for x in ["PFIFO", "CoDel", "FQ-CoDel", "Cake"]],
                    value="PFIFO", # Default selected AQM
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Direction:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="direction-select",
                    options=[{"label": x, "value": x} for x in ["Upload", "Download"]],
                    value="Upload", # Default selected direction
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Flow Scenario:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="scenario-select",
                    # Options and initial value will be set by the callback
                    clearable=False,
                    style={"color": "#000"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Metrics:", style={"fontWeight": "bold", "color": "#333"}),
                dcc.Dropdown(
                    id="metric-select",
                    options=[{"label": label, "value": key} for key, label in metric_labels.items()],
                    value=["throughput_mbps", "rtt_ms"], # Default selected metrics
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
            "flex": "2", # Takes 2 units of available space (so it's twice as wide as the left panel)
            "padding": "20px",
            "backgroundColor": "#ffffff",
            "borderRadius": "12px",
            "boxShadow": "0px 2px 10px rgba(0, 0, 0, 0.1)"
        })
    ])
])

# --- Helper function to load data based on AQM and Direction ---
def load_data_for_aqm_direction(aqm_type, direction_type):
    """
    Loads and preprocesses dataframes for a given AQM type and direction.
    Assumes file names like 'CCA_AQM_DIRECTION.csv' (e.g., 'Cubic_PFIFO_Upload.csv')
    """
    current_available_flows = {}
    for name in cca_names: # Iterate through defined CCA names (Cubic, BBRv1, etc.)
        filename = f"{name}_{aqm_type}_{direction_type}.csv"
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                # Ensure 'time_sec' column exists before assigning to 'Time'
                if "time_sec" in df.columns:
                    df["Time"] = df["time_sec"]
                else:
                    print(f"Warning: 'time_sec' column not found in {filename}. Plotting may be affected.")
                    df["Time"] = df.index # Fallback to DataFrame index
                
                df["label"] = name # Assign the CCA name as a label for plotting
                current_available_flows[name] = df
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
    return current_available_flows

# --- Callback to update scenario dropdown options based on AQM and Direction ---
@app.callback(
    Output("scenario-select", "options"),
    Output("scenario-select", "value"), # Also reset selected value when options change
    Input("aqm-select", "value"),
    Input("direction-select", "value")
)
def set_scenario_options(aqm_selected, direction_selected):
    current_flows = load_data_for_aqm_direction(aqm_selected, direction_selected)
    
    current_flow_scenarios = {}
    
    # Generate all combinations of two flows (Cubic, BBRv1, etc.), including self-vs-self
    # Ensure both CCAs in a pair are actually available for the selected AQM/Direction
    for f1_name in cca_names:
        for f2_name in cca_names:
            if f1_name in current_flows and f2_name in current_flows:
                # To handle unique scenarios (e.g., "Cubic vs BBRv1" is same as "BBRv1 vs Cubic" for options list)
                # You can decide if you want both or just one. Here, I'm keeping both for explicit selection if desired,
                # but sorting the names ensures consistent scenario naming like "BBRv1 vs Cubic" not "Cubic vs BBRv1" if you want.
                # For clarity, let's just make sure both exist and name consistently:
                # scenario_key = " vs ".join(sorted([f1_name, f2_name])) # Uncomment if you only want one entry per pair
                scenario_key = f"{f1_name} vs {f2_name}" # This matches your request for explicit combinations
                current_flow_scenarios[scenario_key] = (current_flows[f1_name].copy(), current_flows[f2_name].copy())

    options = [{"label": k, "value": k} for k in sorted(current_flow_scenarios.keys())]
    
    # Set default value to the first available scenario, or None if no scenarios are found
    default_value = options[0]["value"] if options else None
    
    return options, default_value

# --- Plot Callback ---
@app.callback(
    Output("metric-plot", "src"),
    Input("scenario-select", "value"),
    Input("aqm-select", "value"),
    Input("direction-select", "value"),
    Input("metric-select", "value")
)
def update_plot(scenario, aqm, direction, selected_metrics):
    # Retrieve the relevant dataframes based on current AQM and Direction selections
    current_flows_for_plot = load_data_for_aqm_direction(aqm, direction)

    # Handle cases where no scenario or metrics are selected, or data is missing
    if not scenario or not selected_metrics:
        return "data:image/png;base64," + base64.b64encode(io.BytesIO().read()).decode("utf-8")

    # Parse the selected scenario string to get the two CCA names (e.g., "Cubic", "BBRv3")
    f1_name, f2_name = scenario.split(" vs ")

    # Verify that data for both selected flows is actually available for the current AQM/Direction
    if f1_name not in current_flows_for_plot or f2_name not in current_flows_for_plot:
        print(f"Error: Data for scenario '{scenario}' not found for AQM '{aqm}' and Direction '{direction}'.")
        # Return a blank image with a text indicating missing data
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, f"Data missing for '{scenario}' with AQM '{aqm}' and Direction '{direction}'.\n"
                            "Please ensure CSV files like '{CCA}_{AQM}_{Direction}.csv' exist.", 
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
                fontsize=14, color='red')
        ax.axis('off') # Hide axes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

    # Get the actual DataFrame copies for plotting
    df1 = current_flows_for_plot[f1_name].copy()
    df2 = current_flows_for_plot[f2_name].copy()

    # Apply smoothing to selected metrics
    for df in [df1, df2]:
        for metric in selected_metrics: # Only smooth selected metrics to save computation
            if metric in df.columns:
                df[f"{metric}_smoothed"] = df[metric].rolling(window=10, min_periods=1).mean()
            else:
                # If a selected metric column is missing, set smoothed column to None
                df[f"{metric}_smoothed"] = None 
                print(f"Warning: Metric '{metric}' not found in CSV for {df['label'].iloc[0]}.")


    num_metrics = len(selected_metrics)
    # Adjust figure size dynamically based on number of metrics for better readability
    fig, axs = plt.subplots(num_metrics, 1, figsize=(12, 4 * num_metrics), sharex=True)
    # Add full scenario description to the plot title
    fig.suptitle(f"{scenario} | AQM: {aqm} | Direction: {direction}", fontsize=16)

    # Ensure axs is always an iterable list, even if only one subplot
    if num_metrics == 1:
        axs = [axs]

    for i, metric in enumerate(selected_metrics):
        # Plot only if smoothed data is available and not all NaN (e.g., if column was missing)
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
        
        axs[i].set_ylabel(metric_labels[metric])
        axs[i].grid(True, linestyle='--', alpha=0.7) # Add grid for easier reading
        axs[i].legend(loc='upper right') # Consistent legend placement
        # axs[i].tick_params(axis='x', rotation=45) # Rotate x-axis labels if needed for long timeseries

    axs[-1].set_xlabel("Time (s)")
    # Adjust layout to prevent titles/labels from overlapping
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust rect to make space for suptitle

    # Save plot to a BytesIO buffer and convert to base64 for Dash display
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=100) # Use higher DPI for better image quality
    plt.close(fig) # Close the figure to free memory
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

# --- Run the App ---
if __name__ == "__main__":
    # A simple check to alert the user if no files are found at all for the initial load.
    # The real dynamic loading happens in the callbacks.
    initial_flows_check = load_data_for_aqm_direction("PFIFO", "Upload") 
    if not initial_flows_check:
        print("\n" + "="*80)
        print("WARNING: No initial data files found for 'PFIFO' 'Upload'.")
        print("Please ensure your CSV files are named like 'CCA_AQM_Direction.csv' ")
        print("(e.g., 'Cubic_PFIFO_Upload.csv') and are in the same directory.")
        print("The dashboard will still start, but may show no scenarios initially.")
        print("="*80 + "\n")
    
    app.run (debug=True) # Run in debug mode for easier development