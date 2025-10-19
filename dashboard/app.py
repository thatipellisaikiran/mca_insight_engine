import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

def main():
    st.set_page_config(
        page_title="MCA Insights Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📊 MCA Insights Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose Dashboard View",
        ["📈 Overview", "🏢 Company Analysis", "👥 Director Insights", "💰 Financial Patterns", "📅 Trends Analysis"]
    )
    
    # Sample data generation (replace with your actual data)
    @st.cache_data
    def load_sample_data():
        # Generate sample company data
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='M')
        industries = ['Technology', 'Manufacturing', 'Services', 'Healthcare', 'Finance', 'Retail']
        states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Uttar Pradesh']
        
        data = []
        for i in range(1000):
            data.append({
                'company_id': f'COMP{i:04d}',
                'company_name': f'Company {i}',
                'incorporation_date': np.random.choice(dates),
                'industry': np.random.choice(industries),
                'state': np.random.choice(states),
                'authorized_capital': np.random.lognormal(12, 1.5),
                'paid_up_capital': np.random.lognormal(11, 1.2),
                'director_count': np.random.randint(1, 8),
                'status': np.random.choice(['Active', 'Active', 'Active', 'Dormant'], p=[0.7, 0.2, 0.05, 0.05])
            })
        
        df = pd.DataFrame(data)
        df['incorporation_year'] = df['incorporation_date'].dt.year
        return df
    
    df = load_sample_data()
    
    # Main content based on selection
    if app_mode == "📈 Overview":
        show_overview(df)
    elif app_mode == "🏢 Company Analysis":
        show_company_analysis(df)
    elif app_mode == "👥 Director Insights":
        show_director_insights(df)
    elif app_mode == "💰 Financial Patterns":
        show_financial_patterns(df)
    elif app_mode == "📅 Trends Analysis":
        show_trends_analysis(df)

def show_overview(df):
    st.header("📈 Executive Overview")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_companies = len(df)
        st.metric("Total Companies", f"{total_companies:,}")
    
    with col2:
        active_companies = len(df[df['status'] == 'Active'])
        st.metric("Active Companies", f"{active_companies:,}")
    
    with col3:
        avg_capital = df['authorized_capital'].mean()
        st.metric("Avg Authorized Capital", f"₹{avg_capital:,.0f}")
    
    with col4:
        current_year = datetime.now().year
        recent_companies = len(df[df['incorporation_year'] == current_year])
        st.metric(f"New in {current_year}", f"{recent_companies}")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Companies by Industry")
        industry_counts = df['industry'].value_counts()
        fig = px.pie(
            values=industry_counts.values,
            names=industry_counts.index,
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Companies by State")
        state_counts = df['state'].value_counts().head(10)
        fig = px.bar(
            x=state_counts.values,
            y=state_counts.index,
            orientation='h',
            title="Top 10 States"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registration Trends")
        yearly_counts = df.groupby('incorporation_year').size()
        fig = px.line(
            x=yearly_counts.index,
            y=yearly_counts.values,
            title="Company Registrations by Year"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Capital Distribution")
        fig = px.histogram(
            df,
            x='authorized_capital',
            nbins=20,
            title="Authorized Capital Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_company_analysis(df):
    st.header("🏢 Company Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_industry = st.selectbox(
            "Select Industry",
            ['All'] + list(df['industry'].unique())
        )
    
    with col2:
        selected_state = st.selectbox(
            "Select State",
            ['All'] + list(df['state'].unique())
        )
    
    # Filter data
    filtered_df = df.copy()
    if selected_industry != 'All':
        filtered_df = filtered_df[filtered_df['industry'] == selected_industry]
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    
    # Display filtered results
    st.subheader("Company Details")
    st.dataframe(
        filtered_df[['company_name', 'industry', 'state', 'authorized_capital', 'status']].head(20),
        use_container_width=True
    )
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_cap = filtered_df['authorized_capital'].mean()
        st.metric("Average Capital", f"₹{avg_cap:,.0f}")
    
    with col2:
        max_cap = filtered_df['authorized_capital'].max()
        st.metric("Maximum Capital", f"₹{max_cap:,.0f}")
    
    with col3:
        company_count = len(filtered_df)
        st.metric("Companies Found", f"{company_count}")

def show_director_insights(df):
    st.header("👥 Director Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Directors per Company")
        fig = px.histogram(
            df,
            x='director_count',
            nbins=10,
            title="Distribution of Director Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Director Patterns by Industry")
        industry_directors = df.groupby('industry')['director_count'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=industry_directors.values,
            y=industry_directors.index,
            orientation='h',
            title="Average Directors per Company by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_financial_patterns(df):
    st.header("💰 Financial Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Capital vs Industry")
        fig = px.box(
            df,
            x='industry',
            y='authorized_capital',
            title="Authorized Capital Distribution by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Paid-up vs Authorized Capital")
        fig = px.scatter(
            df,
            x='authorized_capital',
            y='paid_up_capital',
            color='industry',
            title="Capital Utilization Analysis"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_trends_analysis(df):
    st.header("📅 Trends Analysis")
    
    # Yearly trends by industry
    yearly_industry = df.groupby(['incorporation_year', 'industry']).size().reset_index(name='count')
    
    fig = px.line(
        yearly_industry,
        x='incorporation_year',
        y='count',
        color='industry',
        title="Company Registration Trends by Industry"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # State-wise trends
    col1, col2 = st.columns(2)
    
    with col1:
        top_states = df['state'].value_counts().head(5).index
        state_trends = df[df['state'].isin(top_states)]
        state_yearly = state_trends.groupby(['incorporation_year', 'state']).size().reset_index(name='count')
        
        fig = px.line(
            state_yearly,
            x='incorporation_year',
            y='count',
            color='state',
            title="Top 5 States - Registration Trends"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Capital trends
        capital_trends = df.groupby('incorporation_year')['authorized_capital'].mean().reset_index()
        fig = px.line(
            capital_trends,
            x='incorporation_year',
            y='authorized_capital',
            title="Average Authorized Capital Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()