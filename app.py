import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

st.title("📊 SSS DATA ANALYTICS DASHBOARD")

# ---------------------------
# LOAD LATEST FILE (NO CACHE)
# ---------------------------
files = [f for f in os.listdir() if f.endswith(".zip")]

if not files:
    st.error("❌ No ZIP file found")
    st.stop()

# 🔥 pick latest file
FILE_PATH = max(files, key=os.path.getmtime)

st.write("📁 Using file:", FILE_PATH)
st.write("📂 Available files:", os.listdir())

with zipfile.ZipFile(FILE_PATH) as z:
    csv_file = [f for f in z.namelist() if f.endswith(".csv")][0]
    df = pd.read_csv(z.open(csv_file), encoding="cp1252")

# ---------------------------
# CLEAN DATA
# ---------------------------
df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip().str.upper()
df["Service"] = df["Service"].astype(str).str.strip().str.upper()
df["From_Port"] = df["From_Port"].astype(str).str.strip().str.upper()
df["To_Port"] = df["To_Port"].astype(str).str.strip().str.upper()

# DATE FIX
df["Inserted_At"] = pd.to_datetime(
    df["Inserted_At"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

df["Inserted_Date"] = df["Inserted_At"]

# DEBUG
st.write("Total Rows:", len(df))
st.write("Unique Dates:", df["Inserted_Date"].dt.date.unique())

# ---------------------------
# FILTER UI
# ---------------------------
st.subheader("Filters")

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
# APPLY FILTERS (FIXED)
# ---------------------------
filtered_df = df.copy()

if operator:
    filtered_df = filtered_df[filtered_df["Operator_Code"].isin(operator)]

if service:
    filtered_df = filtered_df[filtered_df["Service"].isin(service)]

if from_port:
    filtered_df = filtered_df[filtered_df["From_Port"].isin(from_port)]

if to_port:
    filtered_df = filtered_df[filtered_df["To_Port"].isin(to_port)]

# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Operators", filtered_df["Operator_Code"].nunique())
c2.metric("Ports", filtered_df["From_Port"].nunique())
c3.metric("Terminals", filtered_df["From_Port_Terminal"].nunique())
c4.metric("Vessels", filtered_df["Vessel_Name"].nunique())

# ---------------------------
# SUMMARY TABLE
# ---------------------------
st.subheader("Date vs Operator Summary")

summary_df = (
    filtered_df
    .dropna(subset=["Inserted_Date", "Operator_Code"])
    .groupby([filtered_df["Inserted_Date"].dt.date, "Operator_Code"])
    .size()
    .reset_index(name="Operator_Count")
)

summary_df.columns = ["Inserted_Date", "Operator_Code", "Operator_Count"]

# GRAND TOTAL
grand_total = pd.DataFrame({
    "Inserted_Date": ["TOTAL"],
    "Operator_Code": [""],
    "Operator_Count": [summary_df["Operator_Count"].sum()]
})

summary_df["Inserted_Date"] = pd.to_datetime(summary_df["Inserted_Date"]).dt.strftime("%d-%m-%Y")

final_df = pd.concat([summary_df, grand_total], ignore_index=True)
final_df = final_df.reset_index(drop=True)

st.dataframe(final_df, use_container_width=True)

# ---------------------------
# OPERATOR TREND
# ---------------------------
st.subheader("Date Wise Operator Trend")

trend = (
    filtered_df.groupby([filtered_df["Inserted_Date"].dt.date, "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

trend.columns = ["Inserted_Date", "Operator_Code", "Count"]

fig = px.bar(
    trend,
    y="Inserted_Date",
    x="Count",
    color="Operator_Code",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# OPERATOR COMPARISON
# ---------------------------
st.subheader("Operator Comparison")

compare = filtered_df["Operator_Code"].value_counts().reset_index()
compare.columns = ["Operator", "Count"]

fig_compare = px.bar(compare, x="Operator", y="Count", color="Operator")
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------------
# TOP ROUTES
# ---------------------------
st.subheader("Top Routes")

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(route_df, x="Count", y="Route", orientation="h")
st.plotly_chart(fig_route, use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.subheader("Service Distribution")

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(service_df, x="Count", y="Service", orientation="h")
st.plotly_chart(fig_service, use_container_width=True)
