import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import numpy as np
import plotly.graph_objs as go
import math
warnings.filterwarnings('ignore')



def calculate_impermanent_loss(initial_price_1, current_price_1, current_price_2):

    # Calculate relative price changes
    k = current_price_1 / initial_price_1

    # Calculate impermanent loss formula
    IL = 2.0 * np.sqrt(k) / (1.0 + k) - 1.0

    return IL
    
    
# Function to calculate leveraged yield farming returns
def leveraged_yield_farming(capital,total_needed,borrow_a,borrow_b,rewards,new_price_a,price_a,price_b,borrowed_cost_a,borrowed_cost_b,leverage_ratio):


    # Calculate impermanent losses
    IL = calculate_impermanent_loss(new_price_a, price_a, price_b)

    # Calculate debt
    debt_a = new_price_a * borrow_a
    debt_b = price_b * borrow_b
    
    interest_a = borrowed_cost_a / 100.0 * new_price_a
    interest_b = borrowed_cost_b / 100.0 * price_b
    borrow_interest = interest_a + interest_b
    
    # New value
    new_value = (total_needed / 2.0 * new_price_a / price_a + total_needed / 2.0) * (IL + 1.0)
    
    price_effect = ((new_value - debt_a - debt_b) - capital) / capital * 100.0 
    
    HODL_TokenA = new_price_a / price_a * 100.0 - 100.0
    V2_Farm = (0.5 * new_price_a / price_a + 0.5) * (IL + 1.0) * 100.0 - 100.0 + rewards / leverage_ratio / capital * 100.0
    
    
    # Calculate profit or loss
    profit_loss = price_effect - borrow_interest/capital*100 + rewards/capital*100

    
    return profit_loss,price_effect,rewards,borrow_interest,HODL_TokenA,V2_Farm




# Streamlit interface
def main():


    st.set_page_config(page_title="LYF Calculator",page_icon=":chart_with_upwards_trend:",layout="wide")

    st.title(" :chart_with_upwards_trend: Leveraged Yield Farming Calculator")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)


    # Set up layout with two columns
    col1, col2 = st.columns([1, 2])

    # Left column: Input widgets
    with col1:
        
        # Users Capital
        token_a = st.number_input('Initial Investment for Token A', min_value=0.0, step=1000.0, value=10000.0, format='%f')
        token_b = st.number_input('Initial Investment for Token B', min_value=0.0, step=1000.0, value=10000.0, format='%f')

        price_a = st.number_input('Initial price for Token A', min_value=0.0, step=0.1, value=1.0, format='%f')
        price_b = st.number_input('Initial price for Token B (USDC)', min_value=0.0, step=0.1, value=1.0, format='%f')
                
        capital = token_a + token_b
        
        
        # Leveraged Position
        leverage_ratio = st.slider('Leverage Ratio', min_value=1.0, max_value=5.0, value=2.0, step=0.1, format='%f')
        
        total_needed = leverage_ratio * capital
        
        
        # Borrow
        total_to_borrow = total_needed - capital
        borrowed_percentage_a = st.slider('Percentage of Token A to borrow (%)', min_value=0.0, max_value=100.0, value=20.0, step=1.0, format='%f')
        
        USD_token_a_borrow = borrowed_percentage_a / 100.0 * total_to_borrow
        USD_token_b_borrow = total_to_borrow - USD_token_a_borrow
        
        borrowed_cost_a = st.number_input('Borrowing Cost of Token A to borrow (%)', min_value=0.0, step=10.0, value=10.0, format='%f')
        borrowed_cost_b = st.number_input('Borrowing Cost of Token B to borrow (%)', min_value=0.0, step=10.0, value=20.0, format='%f')
        borrow_a = USD_token_a_borrow / price_a
        borrow_b = USD_token_b_borrow / price_b
         
        
        
        # Calculate Yield Rewards
        annual_yield = st.number_input('Original Annual Yield (%)', min_value=0.0, step=5.0, value=15.0, format='%f')
        rewards = annual_yield / 100.0 * total_needed
        
        

        xmin = st.number_input('Minimum Token A price (ratio)', min_value=-1.0, value=-0.5, format='%f')
        xmax = st.number_input('Maximum Token A price (ratio)', min_value=-1.0, value=5.0, format='%f')        
        

    # Right column: Plotly graph
    with col2:
        st.subheader('Profit/Loss Curve with Respect to Token Price Change')

        # Calculate Profit/Losses
        token_a_prices = (1.0 + np.linspace(xmin, xmax, 100)) * price_a
        
        profits_losses = []
        price_effect = []
        rewards_list = []
        borrow_cost = []
        HODL = []
        V2 = []
                
        for new_price_a in token_a_prices:
        
            pf,pe,re,bo,hodl_amnt,v2_amt = leveraged_yield_farming(capital,total_needed,borrow_a,borrow_b,rewards,new_price_a,price_a,price_b,borrowed_cost_a,borrowed_cost_b,leverage_ratio)
            profits_losses.append(pf)
            rewards_list.append(re/capital*100)
            borrow_cost.append(bo/capital*100)
            price_effect.append(pe)
            HODL.append(hodl_amnt)
            V2.append(v2_amt)

        
        x_values = token_a_prices/price_a*100.0-100.0

        # Plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_values, y=profits_losses , mode='lines', name='Strategy'))        
        fig.add_trace(go.Scatter(x=x_values, y=HODL , mode='lines', name='HODL Token A'))       
        fig.add_trace(go.Scatter(x=x_values, y=V2 , mode='lines', name='V2 Farm'))
        fig.update_layout(title='Profit/Loss Curve',
                          xaxis_title='Token Price Change (%)',
                          yaxis_title='Profit/Loss (%)',
                          template='plotly_dark',
                          xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),  # Add grid lines for x-axis
                          yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))  # Add grid lines for y-axis)
 
                      
        #fig.update_layout(xaxis=dict(range=[-100.0,max(x_values)]))                               
        #fig.update_layout(yaxis=dict(range=[ymin,ymax]))
                       
                        
                          
        st.plotly_chart(fig)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=token_a_prices/price_a*100.0-100.0, y=price_effect , mode='lines', name='Price Effect'))
        
        fig.update_layout(title='Price Effect (%)',
                          xaxis_title='Token Price Change (%)',
                          yaxis_title='Price Effect (%)',
                          template='plotly_dark',
                          xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),  # Add grid lines for x-axis
                          yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'))  # Add grid lines for y-axis

  
        #fig.update_layout(yaxis=dict(range=[ymin,ymax]))  
        #fig.update_layout(xaxis=dict(range=[-100.0,max(x_values)]))         
   

        st.plotly_chart(fig)

        st.write("Token A to borrow = ",borrow_a, " --> $", USD_token_a_borrow, " at original price")
        st.write("Token B to borrow = ",borrow_b, " --> $", USD_token_b_borrow, " at original price")
        st.write("Estimated Yield Rewards (%) = ",rewards_list[0],"%")



if __name__ == '__main__':
    main()

