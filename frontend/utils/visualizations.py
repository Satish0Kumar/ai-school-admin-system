"""
Visualization utilities for Streamlit app
"""
import plotly.graph_objects as go
import plotly.express as px


def create_confidence_chart(probabilities):
    """Create a bar chart showing confidence distribution"""
    
    risk_levels = ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']
    values = [
        probabilities['Low Risk'],
        probabilities['Medium Risk'],
        probabilities['High Risk'],
        probabilities['Critical Risk']
    ]
    colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
    
    fig = go.Figure(data=[
        go.Bar(
            x=risk_levels,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}%' for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Probability: %{y:.2f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Risk Level Probability Distribution",
        xaxis_title="Risk Level",
        yaxis_title="Probability (%)",
        yaxis_range=[0, 100],
        height=400,
        showlegend=False,
        hovermode='x'
    )
    
    return fig


def create_gauge_chart(confidence, risk_level):
    """Create a gauge chart for confidence score"""
    
    # Determine color based on risk level
    color_map = {
        'Low Risk': 'green',
        'Medium Risk': 'orange',
        'High Risk': 'red',
        'Critical Risk': 'darkred'
    }
    color = color_map.get(risk_level, 'gray')
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Prediction Confidence", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 75], 'color': '#fff3e0'},
                {'range': [75, 100], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': confidence
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_feature_importance_chart():
    """Create a sample feature importance chart (placeholder)"""
    
    features = [
        'Current GPA',
        'Attendance %',
        'Failed Subjects',
        'Assignment Rate',
        'Disciplinary Incidents',
        'Previous GPA'
    ]
    importance = [25, 20, 15, 13, 12, 10]
    
    fig = go.Figure(data=[
        go.Bar(
            y=features,
            x=importance,
            orientation='h',
            marker_color='steelblue',
            text=[f'{v}%' for v in importance],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Key Risk Factors",
        xaxis_title="Importance (%)",
        yaxis_title="Feature",
        height=350,
        showlegend=False
    )
    
    return fig
