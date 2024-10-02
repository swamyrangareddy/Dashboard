import streamlit as st
import plotly.express as px
import pandas as pd
import os
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import time
from streamlit_extras.metric_cards import style_metric_cards

import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title(":chart_with_upwards_trend: Payment Dashboard")


# load Style css
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;  /* Light gray background */
    }
    [data-testid=metric-container] {
        box-shadow: 0 0 4px #686664;
        padding: 10px;
    }

    .plot-container>div {
        box-shadow: 0 0 2px #070505;
        padding: 5px;
        border-color: #000000;
    }

    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.2rem;
        color: rgb(0, 0, 0);
        border-color: #000000;
        color-scheme: #000000;
    }

    .sidebar-content {
        color: white;
    }

    [data-testid=stSidebar] {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def style_metric_cards(background_color="#333333", border_left_color="#444444", border_color="#555555", box_shadow="#000000"):
    st.markdown(
        f"""
        <style>
        div[data-testid="metric-container"] {{
            background-color: {background_color};
            border-left: 5px solid {border_left_color};
            border: 1px solid {border_color};
            box-shadow: 0 0 4px {box_shadow};
            padding: 10px;
            border-radius: 5px;
            color: #FFFFFF;  /* Text color for dark theme */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
df = pd.read_csv("Untitled_report.csv")


st.sidebar.header("Please Filter Here: ")

# Convert created_date to datetime
df["created"] = pd.to_datetime(df["created"])

start_date = st.sidebar.date_input("Start date", df["created"].min())
end_date = st.sidebar.date_input("End date", df["created"].max())

# Ensure start_date and end_date are in datetime format
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

subscription = st.sidebar.multiselect(
    "Select the subscription: ",
    options=df["subscription"].unique(),
    default=df["subscription"].unique()
)



df_selection=df.query(
    "subscription == @subscription and created >= @start_date and created <= @end_date")

def Home():
    with st.expander("VIEW DATA"):
        showData=st.multiselect('Filter: ',df_selection.columns,default=['created','customer_id','email','phone','name', 'address_line1', 'address_line2', 'address_city', 'address_state', 'address_country', 'address_postal_code','subscription','automatic_tax_enabled','invoice_number','description','quantity','currency','line_item_amount','total_invoice_amount','discount','fee','tax','net_amount'])
        st.dataframe(df_selection[showData],use_container_width=True)

    #Total Transaction 
    total_transaction = df_selection["total_invoice_amount"].count()
    # Total net Amount 
    total_net_amount = df_selection["net_amount"].sum()
    # Total fee amount 
    total_fee_amount = df_selection["fee"].sum()
    # Total subscriptions sold (monthly, yearly) 
    total_sub = df_selection.dropna(subset=["subscription"])
    total_subscriptions_sold = total_sub["subscription"].count()

    total_tax =df_selection["tax"].sum()

    # unique customers
    unique_costomers = df["customer_id"].nunique()

    # Debugging: Display calculated values
    # st.write(f"Total Transactions: {total_transaction}")
    # st.write(f"Total Net Amount: {total_net_amount}")
    # st.write(f"Total Fee Amount: {total_fee_amount}")
    # st.write(f"Total Subscriptions Sold: {total_subscriptions_sold}")

    total1, total2, total3 = st.columns(3, gap='small')
    with total1:
        st.info('Total Transaction', icon="💰")
        st.metric(label="Total Transactions", value=f"$ {total_transaction:,.0f}")

    with total2:
        st.info('Total Net Amount', icon="💰")
        st.metric(label="Total Net Amount", value=f"$ {total_net_amount:,.0f}")

    with total3:
        st.info('Total Fee Amount', icon="💰")
        st.metric(label="Total Fee Amount", value=f"$ {total_fee_amount:,.0f}")
    
    total1, total2, total3 = st.columns(3, gap='small')

    with total1:
        st.info('Total Tax Amount', icon="💰")
        st.metric(label="Total Tax", value=f"$ {total_tax:,.0f}")

    with total2:
        st.info('Total Subscriptions Sold')
        st.metric(label="Total Subscriptions Sold", value=f"{total_subscriptions_sold:,.0f}")
    
    with total3:
        st.info('Total customers')
        st.metric(label="Total customers", value=f"{unique_costomers:,.0f}")


    style_metric_cards(background_color="#333333", border_left_color="#444444", border_color="#555555", box_shadow="#000000")
    #style_metric_cards(background_color="#FFFFFF",border_left_color="#686664",border_color="#000000",box_shadow="#F71938")
    with st.expander("DISTRIBUTIONS BY FREQUENCY"):
        fig,ax = plt.subplots(figsize=(16,8))
        df_selection.hist(ax=ax, color='#898784', zorder=2, rwidth=0.9, legend=['Investment'])
        st.pyplot(fig)



def graphs():
    # Assuming 'df' is your DataFrame
    top5_subscriptions = df_selection.groupby("subscription")["net_amount"].sum().nlargest(5)
    # Convert the Series to a DataFrame for better display
    top5_subscriptions_df = top5_subscriptions.reset_index()

    # Create the pie chart
    fig1 = px.pie(top5_subscriptions_df, values=top5_subscriptions.values, names=top5_subscriptions.index, title="Top 5 Subscriptions by Net Amount")

    # Count the occurrences of each subscription type
    subscription_counts = df_selection["subscription"].value_counts()

    # Group by subscription and line item, then sum the charges
    grouped_df = df_selection.groupby(["subscription", "line_item_amount"])["line_item_amount"].count().reset_index(name="count")

    # Calculate total fees for each subscription
    total_fees = grouped_df.groupby("subscription")["line_item_amount"].sum()

    # Display the results
    fig2 = px.pie(grouped_df, values='count', names='subscription', title='Subscription and Line Item Amount Distribution')

    fig3 = px.line(
        total_fees,
        x=total_fees.index,
        y=total_fees.values,
        title='Total Fees by Subscription',
        labels={'x': 'Subscription Type', 'y': 'Total Fees'},
        markers=True
    )

    fig3.update_layout(
        xaxis_title='Subscription Type',
        yaxis_title='Total Fees',
        template='plotly_white'
    )


    # Ensure 'created' column is in datetime format
    df_selection['created'] = pd.to_datetime(df_selection['created'])

    # Group the data by month and sum the total invoice amounts
    df_selection['month'] = df_selection['created'].dt.to_period('M')
    df_monthly = df_selection.groupby('month')['total_invoice_amount'].sum().reset_index()

    # Convert the 'month' column back to datetime for plotting
    df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

    # Group the data by month and sum the total invoice amounts
    df_selection['month'] = df_selection['created'].dt.to_period('M')
    df_monthly = df_selection.groupby('month')['total_invoice_amount'].sum().reset_index()

    col1,col2 = st.columns(2)
    with col1:
        st.write("### Top 5 Subscriptions")
        st.plotly_chart(fig1)
    
    with col2:
        st.write("### Subscription counts")
        st.bar_chart(subscription_counts)

    st.markdown("---") 
    
    col1,col2 = st.columns(2)
    with col1:
        st.write("### Subscription and Line Item")
        st.plotly_chart(fig2)
    with col2:
        st.write("### Subscription Fees")
        st.plotly_chart(fig3)


def Progressbar():
    st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",unsafe_allow_html=True,)
    target=3000000000
    current=df_selection["total_invoice_amount"].sum()
    percent=round((current/target*100))
    mybar=st.progress(0)

    if percent>100:
        st.subheader("Target done !")
    else:
        st.write("you have ",percent, "% " ,"of ", (format(target, 'd')), "TZS")
        for percent_complete in range(percent):
            time.sleep(0.1)
            mybar.progress(percent_complete+1,text=" Target Percentage")

#menu bar
def sideBar():
    with st.sidebar:
        selected=option_menu(
            menu_title="Main Menu",
            options=["Home","Graphs"],
            icons=["house","eye"],
            menu_icon="cast",
            default_index=0
        )
    if selected=="Home":
        st.subheader(f"Page: {selected}")
        Home()
        graphs()
    if selected=="Graphs":
        st.subheader(f"Page: {selected}")
        #Progressbar()
        graphs()
    
sideBar()