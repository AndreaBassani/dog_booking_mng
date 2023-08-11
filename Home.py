import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px
from pathlib import Path

st.title('My Doggy Revenue')

# Load existing data or create a new DataFrame
DATA_PATH = Path('data/input_data.csv')
if DATA_PATH.is_file():
    historic_df = pd.read_csv('data/input_data.csv', parse_dates=['date','Start Date', 'End Date'])
else: 
    historic_df = pd.DataFrame(columns=['date','Dog Name', 'Start Date', 'End Date', 'Net App Income', 'Cash Income','Total Income'])


with st.form('add_dog_form'):
    dog_name = st.text_input("Enter dog's name")
    next_week = dt.date.today() + dt.timedelta(days=7)
    jan_1 = dt.date(dt.date.today().year, 1, 1)
    dec_31 = dt.date(dt.date.today().year + 1, 12, 31)
    date_booked = st.date_input('Select date range:', (dt.date.today(), next_week), jan_1, dec_31)
    net_app_income_input = st.number_input('Net App Income:', value=0.0, step=0.01)
    cash_income_input = st.number_input('Cash Income:', value=0.0, step=0.01)
    submitted = st.form_submit_button('Submit')

if submitted:

    # Append the new data to the existing DataFrame
    new_data = {
        'date': dt.date.today(),
        'Dog Name': [dog_name],
        'Start Date': [date_booked[0]],
        'End Date': [date_booked[1]],
        'Net App Income': [net_app_income_input],
        'Cash Income':[cash_income_input],
        'Total Income':[cash_income_input+net_app_income_input]
    }
    df = pd.DataFrame(new_data)
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['End Date'] = pd.to_datetime(df['End Date']) + pd.DateOffset(hours=23,minutes=59)
    historic_df = pd.concat([historic_df, df], ignore_index=True)
    # Save the updated DataFrame to CSV
    historic_df.to_csv('data/input_data.csv', index=False)
    st.session_state.data = historic_df



if historic_df.shape[0]>0:
    
    historic_df.sort_values(by=['Start Date'], inplace=True)

    fig = px.timeline(historic_df.sort_values(by=['Start Date']), x_start='Start Date', x_end='End Date', y='Dog Name', color='Dog Name', text='Total Income')
    fig.add_vline(x=dt.date.today(), line_width=1, line_color="red", line_dash="dot")
    fig.update_layout(
    font=dict(
        family="Arial, sans-serif",
        size=15,  # Set the font size here
    ),
    yaxis_title=None
)
    st.plotly_chart(fig, use_container_width=True)

if "data" not in st.session_state:
    st.session_state.data = historic_df


def callback():
    edited_rows = st.session_state["data_editor"]["edited_rows"]
    rows_to_delete = []

    for idx, value in edited_rows.items():
        if value["Delete Row"] is True:
            rows_to_delete.append(idx)

    st.session_state["data"] = (
        st.session_state["data"].drop(rows_to_delete, axis=0).reset_index(drop=True)
    )


columns = st.session_state["data"].columns
column_config = {column: st.column_config.Column(disabled=True) for column in columns}

modified_df = st.session_state["data"].copy()
modified_df["Delete Row"] = False
# Make Delete be the first column
modified_df = modified_df[["Delete Row"] + modified_df.columns[:-1].tolist()]

historic_df = st.data_editor(
    modified_df,
    key="data_editor",
    on_change=callback,
    hide_index=True,
    column_config=column_config,
)
historic_df.drop(["Delete Row"], axis=1, inplace=True)
historic_df.to_csv('data/input_data.csv', index=False)