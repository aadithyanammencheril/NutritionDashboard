import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configure the page
st.set_page_config(
    page_title="Vegetarian Foods Nutrition Dashboard",
    page_icon="",
    layout="wide"
)

# Load and cache data
@st.cache_data
def load_data():
    """Load the vegetable nutrition data"""
    try:
        df = pd.read_csv('v1_veg.csv')
        df.columns = df.columns.str.strip()
        df = df.dropna()
        return df
    except FileNotFoundError:
        st.error("Please upload your csv file to use this app.")
        return None

def create_radar_chart(selected_foods, df):
    """Create a clean radar chart for selected vegetables"""
    if not selected_foods:
        return go.Figure()  # Return empty figure instead of None
    
    fig = go.Figure()
    
    # Nutrition categories and labels
    nutrients = ['prot_g', 'tot_fat_g', 'tot_fib_g', 'carb_g']
    labels = ['Protein (g)', 'Fat (g)', 'Fiber (g)', 'Carbs (g)']
    
    # Bold, distinct color palette
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
    
    # Smart scaling - use reasonable max based on selected foods
    selected_data = df[df['Food Name'].isin(selected_foods)]
    if not selected_data.empty:
        max_values = [selected_data[nutrient].max() for nutrient in nutrients]
        chart_max = max(max_values) * 1.3  # Add 30% padding
        chart_max = max(chart_max, 10)  # Ensure minimum scale of 10
    else:
        chart_max = 50
    
    for i, food in enumerate(selected_foods):
        food_data = df[df['Food Name'] == food]
        if not food_data.empty:
            food_row = food_data.iloc[0]
            values = [food_row[nutrient] for nutrient in nutrients]
            
            # Better food name handling for legend
            display_name = food if len(food) <= 20 else food[:17] + "..."
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=display_name,
                line=dict(color=colors[i % len(colors)], width=3),
                fillcolor=colors[i % len(colors)],
                opacity=0.4
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, chart_max],
                tickfont=dict(size=12, color='#2C3E50'),
                gridcolor='#BDC3C7',
                gridwidth=2,
                linecolor='#34495E',
                linewidth=2
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color='#2C3E50', family='Arial'),
                linecolor='#34495E',
                linewidth=2,
                gridcolor='#BDC3C7'
            ),
            bgcolor='#F8F9FA'
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color='#2C3E50'),
            bordercolor='#BDC3C7',
            borderwidth=1,
            bgcolor='white'
        ),
        height=500,
        margin=dict(t=50, b=50, l=50, r=200),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Arial', color='#2C3E50')
    )
    
    return fig  # This was missing!
    
def create_scatter_overview(df):
    """Create scatter plot showing all vegetables"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['prot_g'],
        y=df['tot_fib_g'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['carb_g'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Carbs (g)")
        ),
        text=df['Food Name'],
        hovertemplate='<b>%{text}</b><br>' +
                     'Protein: %{x:.1f}g<br>' +
                     'Fiber: %{y:.1f}g<br>' +
                     'Carbs: %{marker.color:.1f}g<extra></extra>'
    ))
    
    fig.update_layout(
        title="All Vegetables: Protein vs Fiber (Color = Carbs)",
        xaxis_title="Protein (g)",
        yaxis_title="Fiber (g)",
        height=400,
        showlegend=False
    )
    
    return fig

def create_top_performers_chart(df):
    """Create interactive bar chart showing top performers with nutrient selector"""
    return None  # Placeholder - will be replaced with new implementation

def create_enhanced_top_performers(df, selected_nutrient='Protein'):
    """Create enhanced interactive top performers chart with rich hover tooltips"""
    # Nutrient mapping
    nutrient_map = {
        'Protein': 'prot_g',
        'Fat': 'tot_fat_g', 
        'Fiber': 'tot_fib_g',
        'Carbs': 'carb_g'
    }
    
    # Color mapping for nutrients
    color_map = {
        'Protein': '#E74C3C',
        'Fat': '#3498DB',
        'Fiber': '#2ECC71', 
        'Carbs': '#F39C12'
    }
    
    selected_col = nutrient_map[selected_nutrient]
    chart_color = color_map[selected_nutrient]
    
    # Get top 15 performers for selected nutrient
    top_performers = df.nlargest(15, selected_col).copy()
    
    # Truncate long names
    top_performers['Display_Name'] = top_performers['Food Name'].apply(
        lambda x: x[:25] + "..." if len(x) > 25 else x
    )
    
    # Create the main bar chart
    fig = go.Figure()
    
    # Calculate percentiles for context in tooltips
    percentiles = {}
    for nutrient, col in nutrient_map.items():
        percentiles[nutrient] = df[col].quantile([0.25, 0.5, 0.75, 0.9, 0.95]).to_dict()
    
    def get_nutrient_level(value, nutrient):
        p = percentiles[nutrient]
        if value >= p[0.95]: return "Top 5%"
        elif value >= p[0.9]: return "Top 10%"
        elif value >= p[0.75]: return "High"
        elif value >= p[0.5]: return "Above Average"
        elif value >= p[0.25]: return "Average"
        else: return "Below Average"
    
    # Create custom hover text with all nutrients
    hover_texts = []
    for _, row in top_performers.iterrows():
        hover_text = f"""
<b>{row['Food Name']}</b><br>
<br>
<b>Complete Nutritional Profile:</b><br>
🥩 Protein: {row['prot_g']:.1f}g ({get_nutrient_level(row['prot_g'], 'Protein')})<br>
🥑 Fat: {row['tot_fat_g']:.1f}g ({get_nutrient_level(row['tot_fat_g'], 'Fat')})<br>
🌾 Fiber: {row['tot_fib_g']:.1f}g ({get_nutrient_level(row['tot_fib_g'], 'Fiber')})<br>
🍠 Carbs: {row['carb_g']:.1f}g ({get_nutrient_level(row['carb_g'], 'Carbs')})<br>
<extra></extra>
"""
        hover_texts.append(hover_text)
    
    # Add the bars
    fig.add_trace(go.Bar(
        y=top_performers['Display_Name'],
        x=top_performers[selected_col],
        orientation='h',
        marker=dict(
            color=chart_color,
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        hovertemplate=hover_texts,
        name=selected_nutrient
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"🏆 Top 15 {selected_nutrient} Sources",
            font=dict(size=20, color='#2C3E50'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text=f"{selected_nutrient} (g per 100g)",
                font=dict(size=14, color='#2C3E50')
            ),
            tickfont=dict(size=12, color='#2C3E50'),
            gridcolor='#ECF0F1',
            gridwidth=1
        ),
        yaxis=dict(
            title="",
            categoryorder='total ascending',
            tickfont=dict(size=11, color='#2C3E50')
        ),
        height=600,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=200, r=50, t=80, b=50),
        hoverlabel=dict(
            bgcolor='white',
            bordercolor=chart_color,
            font=dict(size=12, color='#2C3E50')
        )
    )
    
    return fig

def main():
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Header with introduction
    st.title("Vegetarian Foods Nutrition Dashboard")
    st.markdown("*Interactive tool for comparing nutritional profiles of vegetarian foods*")
    
    # Introduction and context
    with st.expander("ℹ️ About This Dashboard", expanded=False):
        st.markdown("""
        ### What This Tool Does
        This interactive dashboard helps you explore and compare the nutritional content of vegetarian foods. 
        You can visualize nutritional profiles using various charts and discover top performers in each nutrient category.
        
        ### Data Source
        All nutritional data is sourced from the **Indian Food Composition Tables (IFCT) 2017**, 
        published by the National Institute of Nutrition, Hyderabad. This is the most comprehensive 
        and authoritative database of Indian food nutrition available.
        
        ### What's Included
        - **314 vegetarian food items** including vegetables, fruits, grains, legumes, dairy products, nuts, and more
        - **4 key nutrients**: Protein, Fat, Fiber, and Carbohydrates (All values are expressed per 100g edible portion)
        - **Interactive comparisons** and detailed nutritional profiles
        
        ### Important Limitations
        - **Vegetarian foods only** - No meat, fish, or poultry
        - **Basic nutrients only** - Vitamins, minerals, and other micronutrients not included
        - **Limited dataset** - This tool covers a subset of the full IFCT database
        
        ### Want Complete Nutrition Data?
        For comprehensive nutritional information including vitamins, minerals, amino acids, and non-vegetarian foods, 
        refer to the complete **[IFCT 2017 PDF Database](https://www.nin.res.in/ebooks/IFCT2017.pdf)**.
        """)
    
    st.markdown("---")
    
    # Simple default selection - just pick first few items to avoid complex logic
    default_vegetables = df['Food Name'].head(3).tolist()
    
    # Vegetable selection
    st.subheader("Select Vegetables to Compare")
    
    selected_vegetables = st.multiselect(
        "Choose up to 5 vegetables:",
        options=sorted(df['Food Name'].unique()),
        default=default_vegetables,
        max_selections=5,
        help="Start with the pre-selected vegetables or choose your own"
    )
    
    # Show radar chart
    if selected_vegetables:
        # Create two columns for radar chart and overview
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Nutritional Profile Comparison")
            try:
                radar_fig = create_radar_chart(selected_vegetables, df)
                st.plotly_chart(radar_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating radar chart: {e}")
        
        with col2:
            st.subheader("Dataset Overview")
            try:
                overview_fig = create_scatter_overview(df)
                st.plotly_chart(overview_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating scatter plot: {e}")
        
        # Show values table below chart
        st.subheader("Nutritional Values (per 100g)")
        
        # Create clean comparison table
        comparison_df = df[df['Food Name'].isin(selected_vegetables)][
            ['Food Name', 'prot_g', 'tot_fat_g', 'tot_fib_g', 'carb_g']
        ].copy()
        
        # Rename columns for display
        comparison_df.columns = ['Vegetable', 'Protein (g)', 'Fat (g)', 'Fiber (g)', 'Carbs (g)']
        
        # Round values for cleaner display
        for col in ['Protein (g)', 'Fat (g)', 'Fiber (g)', 'Carbs (g)']:
            comparison_df[col] = comparison_df[col].round(1)
        
        # Display table
        st.dataframe(
            comparison_df, 
            use_container_width=True,
            hide_index=True
        )
        
        # Add enhanced top performers chart
        st.subheader("Top Nutritional Performers")
        
        with st.expander("💡 How to Use Top Performers", expanded=False):
            st.markdown("""
            - **Choose a nutrient** from the dropdown to see the highest performers
            - **Hover over any bar** to see the complete nutritional profile of that food
            - **Percentile rankings** show how each food compares to the entire database
            - **Use this to discover** foods that excel in specific nutrients
            """)
        
        # Nutrient selector
        col_selector, col_spacer = st.columns([2, 3])
        with col_selector:
            selected_nutrient = st.selectbox(
                "Select nutrient to explore:",
                options=['Protein', 'Fat', 'Fiber', 'Carbs'],
                index=0,
                help="Choose a nutrient to see the top performers"
            )
        
        try:
            enhanced_fig = create_enhanced_top_performers(df, selected_nutrient)
            st.plotly_chart(enhanced_fig, use_container_width=True)
            st.markdown("*💡 Hover over any bar to see the complete nutritional profile of that vegetable*")
        except Exception as e:
            st.error(f"Error creating enhanced chart: {e}")
        
    else:
        st.info("👆 Please select at least one vegetable to see the radar chart")
        
        # Show comprehensive overview when no vegetables selected
        st.subheader("Dataset Overview - All 314 Vegetables")
        
        # Show overview charts
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                overview_fig = create_scatter_overview(df)
                st.plotly_chart(overview_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating scatter plot: {e}")
            
        with col2:
            # Show some quick stats about the dataset
            st.markdown("### Quick Stats")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Total Vegetables", len(df))
                st.metric("Highest Protein", f"{df['prot_g'].max():.1f}g")
            with col_b:
                st.metric("Highest Fiber", f"{df['tot_fib_g'].max():.1f}g")
                st.metric("Lowest Carbs", f"{df['carb_g'].min():.1f}g")
        
        # Show enhanced top performers chart
        try:
            enhanced_fig = create_enhanced_top_performers(df, 'Protein')  # Default to protein
            st.plotly_chart(enhanced_fig, use_container_width=True)
            st.markdown("*💡 Hover over any bar to see complete nutritional profiles*")
        except Exception as e:
            st.error(f"Error creating enhanced chart: {e}")

if __name__ == "__main__":
    main()