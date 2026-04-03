import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import os

# ---------------------------
# CONFIG`
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

# ---------------------------
# THEME
# ---------------------------
theme = st.toggle("Dark Mode")

bg_color = "#0e1117" if theme else "white"
text_color = "white" if theme else "black"

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
    color: {text_color};
}}
.title {{
    background: linear-gradient(90deg, #ff9a9e, #a18cd1, #84fab0);
    padding: 18px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: white;
    border-radius: 12px;
    margin-bottom: 20px;
}}
.section {{
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    padding: 10px;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-top: 25px;
}}
.card {{
    padding: 25px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-weight: bold;
}}
.card1 {{ background: linear-gradient(135deg, #ff9a9e, #fad0c4); }}
.card2 {{ background: linear-gradient(135deg, #a18cd1, #fbc2eb); }}
.card3 {{ background: linear-gradient(135deg, #f6d365, #fda085); }}
.card4 {{ background: linear-gradient(135deg, #84fab0, #8fd3f4); }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# CHART STYLE
# ---------------------------
def style_chart(fig):
    axis_color = "white" if theme else "black"
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font_color=text_color,
        xaxis=dict(tickfont=dict(color=axis_color)),
        yaxis=dict(tickfont=dict(color=axis_color))
    )
    return fig

# ---------------------------
# TITLE
# ---------------------------
st.markdown('<div class="title">SSS DATA ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)

# ---------------------------
# LOAD DATA
# ---------------------------

def load_data():
    zip_file = [f for f in os.listdir() if f.endswith(".zip")][0]

    with zipfile.ZipFile(zip_file) as z:
        file_name = [f for f in z.namelist() if f.endswith(".csv")][0]
        with z.open(file_name) as f:
            df = pd.read_csv(f, encoding="cp1252")

    return df

df = load_data()

# ---------------------------
# CLEAN DATA
# ---------------------------
df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip()
df["Service"] = df["Service"].astype(str).str.strip()
df["From_Port"] = df["From_Port"].astype(str).str.strip().str.upper()
df["To_Port"] = df["To_Port"].astype(str).str.strip().str.upper()

df["Inserted_At"] = pd.to_datetime(
    df["Inserted_At"],
    format="%d-%m-%Y %H:%M:%S",
    errors="coerce"
)
df["Inserted_Date"] = pd.to_datetime(
    df["Inserted_At"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)
st.write("Unique Dates:", df["Inserted_Date"].unique())
st.write("Count:", df["Inserted_Date"].nunique())
# ---------------------------
# FILTER UI
# ---------------------------
st.markdown("### Filters")    

col1, col2, col3, col4 = st.columns(4)

operator_list = sorted(df["Operator_Code"].dropna().unique())
service_list = sorted(df["Service"].dropna().unique())
from_port_list = sorted(df["From_Port"].dropna().unique())
to_port_list = sorted(df["To_Port"].dropna().unique())

operator = col1.multiselect("Operator", operator_list)
service = col2.multiselect("Service", service_list)
from_port = col3.multiselect("From Port", from_port_list)
to_port = col4.multiselect("To Port", to_port_list)

# ---------------------------
# DATE PICKER (FINAL FIX)
# ---------------------------
valid_dates = df["Inserted_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min()
    max_date = valid_dates.max()

    date_range = st.date_input(
        "📅 Select Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="date_range_fixed"
    )

    # 🔥 HANDLE ALL TYPES (LIST / TUPLE / SINGLE)
    if isinstance(date_range, (list, tuple)):
        if len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]
        else:
            start_date = end_date = date_range[0]
    else:
        start_date = end_date = date_range

    # 🔥 FORCE SCALAR DATETIME
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

else:
    start_date = end_date = None
    # ---------------------------
# DEFAULT FILTERS
# ---------------------------
if not operator: operator = operator_list
if not service: service = service_list
if not from_port: from_port = from_port_list
if not to_port: to_port = to_port_list

# ---------------------------
# APPLY FILTERS
# ---------------------------
filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port))
]


# ---------------------------
# DATE FILTER (UPDATED)
# ---------------------------
if start_date and end_date:
    filtered_df = filtered_df[
        (filtered_df["Inserted_Date"].dt.date >= start_date) &
        (filtered_df["Inserted_Date"].dt.date <= end_date)
    ]
# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# SUMMARY TABLE WITH FINAL TOTAL
# ---------------------------
st.markdown('<div class="section">Date vs Operator Summary</div>', unsafe_allow_html=True)

# Summary per date & operator
summary_df = (
    filtered_df
    .dropna(subset=["Inserted_Date", "Operator_Code"])
    .groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Operator_Count")
)

# Sort
summary_df = summary_df.sort_values(by=["Inserted_Date", "Operator_Code"])

# ---------------------------
# GRAND TOTAL (ONLY ONE ROW)
# ---------------------------
grand_total = pd.DataFrame({
    "Inserted_Date": ["TOTAL"],
    "Operator_Code": [""],
    "Operator_Count": [summary_df["Operator_Count"].sum()]
})

# ---------------------------
# FORMAT DATE
# ---------------------------
summary_df["Inserted_Date"] = pd.to_datetime(summary_df["Inserted_Date"]).dt.strftime("%d-%m-%Y")

# Combine
final_df = pd.concat([summary_df, grand_total], ignore_index=True)

# ---------------------------
# RESET INDEX (FIX ISSUE)
# ---------------------------
final_df = final_df.reset_index(drop=True)

# Display
st.dataframe(final_df, use_container_width=True)# ---------------------------
# OPERATOR TREND
# ---------------------------
st.markdown('<div class="section">Date Wise Operator Trend</div>', unsafe_allow_html=True)

trend = (
    filtered_df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

fig = px.bar(
    trend,
    y="Inserted_Date",
    x="Count",
    color="Operator_Code",
    orientation="h",
    text="Operator_Code"   # ✅ IMPORTANT LINE
)

fig.update_traces(
    textposition="outside",
    textfont=dict(size=10)
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# OPERATOR COMPARISON
# ---------------------------
st.markdown('<div class="section">Operator Comparison</div>', unsafe_allow_html=True)

compare = filtered_df["Operator_Code"].value_counts().reset_index()
compare.columns = ["Operator", "Count"]

fig_compare = px.bar(compare, x="Operator", y="Count", color="Operator")
fig_compare = style_chart(fig_compare)
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------------
# TOP ROUTES
# ---------------------------
st.markdown('<div class="section">Top Routes</div>', unsafe_allow_html=True)

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(route_df, x="Count", y="Route", orientation="h")
fig_route = style_chart(fig_route)
st.plotly_chart(fig_route, use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">Service Distribution</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(service_df.head(10), x="Count", y="Service", orientation="h")
fig_service = style_chart(fig_service)
st.plotly_chart(fig_service, use_container_width=True)
