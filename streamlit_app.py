import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st

# Load the CSV file
csv_path = "data/my_data.csv"
data = pd.read_csv(csv_path)

# Filter the data to focus on HIV/AIDS interventions
hiv_data = data[data['cause'] == 'HIV/AIDS']

# Load a world shapefile or GeoJSON file
# Example: 'naturalearth_lowres' provided by GeoPandas
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Ensure the country names in both datasets match
hiv_data['location_name'] = hiv_data['location_name'].str.lower()
world['name'] = world['name'].str.lower()

# Merge the ICER data with the geographical data
merged = world.merge(hiv_data, how='left', left_on='name', right_on='location_name')

# Create an interactive map using Plotly
fig1 = px.choropleth(
    merged,
    geojson=merged.geometry,
    locations=merged.index,
    color='predicted_icer_usd',
    hover_name='location_name',
    hover_data=['predicted_icer_usd'],
    color_continuous_scale='Viridis',
    title='ICER for HIV/AIDS Across Countries'
)

# Update the layout for better visualization
fig1.update_geos(
    fitbounds="locations",
    visible=False
)

fig1.update_layout(
    margin={"r":0,"t":30,"l":0,"b":0},
    coloraxis_colorbar=dict(
        title="ICER (USD)"
    )
)

# Descriptive Analysis: ICER distribution by region
region_icer = hiv_data.groupby('region_name')['predicted_icer_usd'].describe()

# Plotting ICER distribution by region
fig2 = px.box(hiv_data, x='region_name', y='predicted_icer_usd', title='ICER Distribution for HIV/AIDS Interventions by Region')

# Calculate the average ICER by region
region_icer_avg = hiv_data.groupby('region_name')['predicted_icer_usd'].mean().reset_index()

# Sort the data in descending order of average ICER
region_icer_avg = region_icer_avg.sort_values(by='predicted_icer_usd', ascending=False)

# Plotting average ICER by region
fig3 = px.bar(
    region_icer_avg,
    x='region_name',
    y='predicted_icer_usd',
    title='Average ICER for HIV/AIDS Interventions by Region',
    labels={'predicted_icer_usd': 'Average ICER (USD)', 'region_name': 'Region'},
    template='plotly_white'
)

# Update the layout for better visualization
fig3.update_layout(
    xaxis_title="Region",
    yaxis_title="Average ICER (USD)",
    margin=dict(l=40, r=40, t=40, b=40),
    title={
        'text': 'Average ICER for HIV/AIDS Interventions by Region',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

# Add hover template for better interactivity
fig3.update_traces(
    hovertemplate='<b>Region</b>: %{x}<br><b>Average ICER (USD)</b>: %{y:.2f}<extra></extra>',
    marker_color='blue'
)

# Filter data for North Africa and Middle East region
north_africa_middle_east_data = hiv_data[hiv_data['region_name'] == 'north africa and middle east']

# Calculate the average ICER by country
country_icer_avg = north_africa_middle_east_data.groupby('location_name')['predicted_icer_usd'].mean().reset_index()

# Sort the data in descending order of average ICER
country_icer_avg = country_icer_avg.sort_values(by='predicted_icer_usd', ascending=False)

# Plotting average ICER by country
fig4 = px.bar(
    country_icer_avg,
    x='location_name',
    y='predicted_icer_usd',
    title='Average ICER for HIV/AIDS Interventions by Country in North Africa and Middle East',
    labels={'predicted_icer_usd': 'Average ICER (USD)', 'location_name': 'Country'},
    template='plotly_white'
)

# Update the layout for better visualization
fig4.update_layout(
    xaxis_title="Country",
    yaxis_title="Average ICER (USD)",
    margin=dict(l=40, r=40, t=40, b=40),
    title={
        'text': 'Average ICER for HIV/AIDS Interventions by Country in North Africa and Middle East',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

# Add hover template for better interactivity
fig4.update_traces(
    hovertemplate='<b>Country</b>: %{x}<br><b>Average ICER (USD)</b>: %{y:.2f}<extra></extra>',
    marker_color='blue'
)

# Aggregate data to calculate mean ICER for each intervention type within each country
intervention_means = north_africa_middle_east_data.groupby(['location_name', 'intervention'])['predicted_icer_usd'].mean().reset_index()

# Create a grouped bar plot
fig6 = px.bar(intervention_means, x='location_name', y='predicted_icer_usd', color='intervention', barmode='group',
             title='Average ICER for HIV/AIDS Interventions by Country and Intervention Type in North Africa and Middle East',
             labels={'predicted_icer_usd': 'Average ICER (USD)', 'location_name': 'Country', 'intervention': 'Intervention Type'})

# Further filter the data to include only Egypt and Sudan
egypt_sudan_data = north_africa_middle_east_data[north_africa_middle_east_data['location_name'].str.lower().isin(['egypt', 'sudan'])]

# Separate the data for Egypt and Sudan
egypt_data = egypt_sudan_data[egypt_sudan_data['location_name'].str.lower() == 'egypt']
sudan_data = egypt_sudan_data[egypt_sudan_data['location_name'].str.lower() == 'sudan']

# Group data by intervention type and age group for Egypt
egypt_age_group_data = egypt_data.groupby(['intervention', 'population_age'])['predicted_icer_usd'].mean().reset_index()

# Group data by intervention type and age group for Sudan
sudan_age_group_data = sudan_data.groupby(['intervention', 'population_age'])['predicted_icer_usd'].mean().reset_index()

# Plotting the average ICER by age group per intervention type for Egypt
fig_egypt = px.bar(
    egypt_age_group_data,
    x='population_age',
    y='predicted_icer_usd',
    color='intervention',
    title='Average ICER for HIV/AIDS Interventions by Age Group and Intervention Type in Egypt',
    labels={'predicted_icer_usd': 'Average ICER (USD)', 'population_age': 'Age Group'},
    template='plotly_white',
    barmode='group'
)

# Function to plot ICER by Age Group and Intervention Type for a given country
def plot_icer_by_age_group_and_intervention(country_data, country_name, intervention_type):
    filtered_data = country_data[country_data['intervention'] == intervention_type]
    fig = px.bar(
        filtered_data,
        x='population_age',
        y='predicted_icer_usd',
        color='intervention',
        title=f'Average ICER for HIV/AIDS Interventions by Age Group and Intervention Type in {country_name} ({intervention_type})',
        labels={'predicted_icer_usd': 'Average ICER (USD)', 'population_age': 'Age Group'},
        template='plotly_white',
        barmode='group'
    )
    return fig


# Plotting the average ICER by age group per intervention type for Sudan
fig_sudan = px.bar(
    sudan_age_group_data,
    x='population_age',
    y='predicted_icer_usd',
    color='intervention',
    title='Average ICER for HIV/AIDS Interventions by Age Group and Intervention Type in Sudan',
    labels={'predicted_icer_usd': 'Average ICER (USD)', 'population_age': 'Age Group'},
    template='plotly_white',
    barmode='group'
)

# Check for missing values in the relevant columns
missing_data = egypt_sudan_data[['prevalence_per_100k', 'predicted_icer_usd']].isnull().sum()

# Check for zero values
zero_values = (egypt_sudan_data[['prevalence_per_100k', 'predicted_icer_usd']] == 0).sum()

# Filter out rows with zero values
filtered_data = egypt_sudan_data[(egypt_sudan_data['prevalence_per_100k'] > 0) & (egypt_sudan_data['predicted_icer_usd'] > 0)]

# Plot Prevalence vs. ICER
fig_prevalence_icer_filtered = px.scatter(
    filtered_data,
    x='prevalence_per_100k',
    y='predicted_icer_usd',
    color='intervention',
    facet_col='location_name',
    title='Prevalence per 100k vs. ICER by Country and Intervention Type',
    labels={
        'prevalence_per_100k': 'Prevalence per 100k',
        'predicted_icer_usd': 'ICER (USD)',
        'intervention': 'Intervention Type',
        'location_name': 'Country'
    },
    template='plotly_white'
)

# Update marker size
fig_prevalence_icer_filtered.update_traces(marker=dict(size=12))

# Streamlit layout
st.title('HIV/AIDS Intervention Analysis')

# MSBA Logo
html_string = '''<!DOCTYPE html>
<html>
<body>
 <a href="https://www.aub.edu.lb/osb/MSBA/Pages/default.aspx">
  <img src="https://www.aub.edu.lb/osb/research/Darwazah/PublishingImages/OSB%20Stamp%20color-MSBA.png" width=300" height="80" />
 </a>
</body>
</html>'''
st.sidebar.markdown(html_string, unsafe_allow_html=True)

def space(n,element): # n: number of lines
    for i in range(n):
        element.write("")
space(4,st.sidebar)

# Sidebar with names listed
st.sidebar.subheader("Done by:")
st.sidebar.markdown("Mohammad Hussein Ayoub")
st.sidebar.markdown("Taima Kelani")
st.sidebar.markdown("Leen Al Sayyid")

# Sidebar with hyperlinked subheader
st.sidebar.markdown("### [Professor Samar Hajj](https://www.aub.edu.lb/pages/profile.aspx?memberID=sh137)")

# MSBA Logo
html_string1 = '''<!DOCTYPE html>
<html>
<body>
 <a href="https://www.aub.edu.lb/osb/MSBA/Pages/default.aspx">
  <img src="https://spservices.aub.edu.lb/PublicWebService.svc/FMIS_GetProfilePicture?memberId=sh137" width=200" height="150" />
 </a>
</body>
</html>'''
st.sidebar.markdown(html_string1, unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5,tab7 = st.tabs(['Geographical Mapping', 'Average ICER by Region', 'Average ICER by Country', 'Intervention Type', 'Country Age Group', 'fig_prevalence vs ICER'])

with tab1:
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.plotly_chart(fig6, use_container_width=True)

with tab5:
    # Interactive country and intervention type selection
    country = st.selectbox("Select Country", options=["Egypt", "Sudan"])
    intervention_type = st.selectbox("Select Intervention Type", options=intervention_types)
    
    if country == "Egypt":
        st.plotly_chart(plot_icer_by_age_group_and_intervention(egypt_age_group_data, "Egypt", intervention_type), use_container_width=True)
    else:
        st.plotly_chart(plot_icer_by_age_group_and_intervention(sudan_age_group_data, "Sudan", intervention_type), use_container_width=True)



with tab7:
    st.plotly_chart(fig_prevalence_icer_filtered, use_container_width=True)




