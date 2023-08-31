import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots 
from wordcloud import WordCloud
import matplotlib.pyplot as plt



# === UTILITIES ===

@st.cache
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

# Function to generate and display word cloud
def generate_wordcloud(data_counts):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(data_counts)
    
    # Create a figure and axis object explicitly
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    
    st.pyplot(fig)  # Pass the specific figure object to st.pyplot

# === SIDEBAR CONFIGURATION ===
st.sidebar.header("Dashboard Configuration")
st.sidebar.markdown("Use the options below to customize the visualizations.")
# Add more sidebar configurations if needed

# === COMPONENT 1 ===

## 1.a General distribution of articles
st.header("PLTS & PLTB Coverage in Indonesia")
st.markdown("In this dashboard, I am striving to comprehend how news media sites cover the development of Solar Power Plants (PLTS) and Wind Power Plants (PLTB) in Indonesia. Utilizing data mining and text analysis methods, I deployed a bot to gather news articles from three distinct news outlets, selected based on the number of users accessing the media according to similarweb's statistics. The retrieved news articles from their search pages align with the pre-identified keywords. These articles are then cleaned and analyzed to examine their distribution over time, the segments that report the issue the most, key actors, and the central ideas surrounding the issue")

st.subheader("The Overall Corpus")
st.markdown("""
In this section, you are presented with a summary of articles obtained from all keywords and categorized into PLTS-related and PLTB-related articles. These keywords have been identified by David and me. From the graph below, we can observe that using broader keywords generates a higher number of articles. You can use the legend next to the graph to filter the data and hover over specific points on the graph to access precise information.
""")

media_data = load_data("Media_PLTSB - Sheet1.csv")

# Sidebar for Component 1.a
st.sidebar.subheader("Media Distribution")
viz_type_media = st.sidebar.radio(
    "Select Visualization Type for **Keywords**",
    ("Line Graph", "Bar Chart", "Raw Data")
)

# Display based on selection
if viz_type_media == "Bar Chart":
    # Calculate the total counts for each media
    total_counts = {
        'Detik': media_data['Detik'].sum(),
        'CNBC': media_data['CNBC'].sum(),
        'Tribun': media_data['Tribun'].sum()
    }

    # Create a bar chart
    total_articles = go.Figure(data=[go.Bar(
        x=list(total_counts.keys()),
        y=list(total_counts.values())
    )])

    # Add titles and labels
    total_articles.update_layout(title_text='Total Articles Produced Per Media', xaxis_title='Media', yaxis_title='Article')

    # Display the plot using plotly_chart
    st.plotly_chart(total_articles)
    st.markdown("**Notes:** This bar chart shows the total number of articles produced by each media outlet. Comparing these numbers can provide insights into the volume of coverage given by each media source.")

elif viz_type_media == "Raw Data":
    # Display Raw Data
    st.write(media_data)
    st.markdown("**Notes:** The raw data provides a comprehensive view of media coverage data across different media outlets. Exploring this data can help in identifying specific trends and patterns in media coverage.")

else:  # Default to Line Graph
    # Create a subplot for line graph
    keyword_media = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    keyword_media.add_trace(go.Scatter(x=media_data['Keyword'], y=media_data['Detik'], mode='lines+markers', name='Detik'), secondary_y=True)
    keyword_media.add_trace(go.Scatter(x=media_data['Keyword'], y=media_data['CNBC'], mode='lines+markers', name='CNBC'), secondary_y=True)
    keyword_media.add_trace(go.Scatter(x=media_data['Keyword'], y=media_data['Tribun'], mode='lines+markers', name='Tribun'), secondary_y=True)

    # Add titles and labels
    keyword_media.update_layout(title_text='Keyword Across Media', xaxis_title='Keyword', yaxis_title='Counts')

    # Display the plot using plotly_chart
    st.plotly_chart(keyword_media)
    st.markdown("**Notes:** The line graph visualizes the distribution of articles across different media outlets based on specific keywords. The trends in media coverage can provide insights into the popularity and emphasis of certain topics in the media.")

## 1.b Key actors identified from the whole corpus

# Key Actors Analysis
key_actors_data = load_data("corpus_cleaned.csv")  # Load the new source data

st.subheader("Key Actors Analysis")
st.markdown("In the following visualizations, you will observe various actors and institutions identified within the entire dataset. This dataset was collected using the aforementioned keywords from three news outlets: Detik.com, Cnbcindonesia.com, and Tribunnews.com. To discern key actors mentioned in these media sources, I employed Named Entity Recognition (NER) using a pre-defined model known as cahya/bert-base-indonesian-NER. While you may encounter some false positives in the word cloud, it is due to my time limitations, which prevented me from comparing different models or fine-tuning the model with the corpus. It is highly recommended that future research teams allocate more time to train and evaluate the model on a specific corpus")

# Sidebar for Word Cloud
st.sidebar.subheader("PLTS: Word Cloud - Overall Corpus")
entity_type = st.sidebar.selectbox("Choose Entity Type", ['Individuals', 'Organizations'])
top_n = st.sidebar.slider('Choose top N entities for word cloud', 10, 100, 50)

# Add a checkbox to the sidebar for showing raw data
show_raw_data = st.sidebar.checkbox("Show Raw Data", False)

# Filter relevant entities based on entity type
filtered_key_actors_data = key_actors_data[key_actors_data['NER_Label'] == 'B-PER'] if entity_type == 'Individuals' else key_actors_data[key_actors_data['NER_Label'] == 'B-ORG']

# Group by entities and sum the counts
key_actors_counts = filtered_key_actors_data.groupby('Entity')['Counts'].sum().reset_index()

# Filter entities with counts >= 2
key_actors_counts = key_actors_counts[key_actors_counts['Counts'] >= 2]

# Sort entities by counts in descending order
key_actors_counts = key_actors_counts.sort_values(by='Counts', ascending=False)

# Generate and display the word cloud
st.subheader(f"PLTS: Top {top_n} {entity_type}")
entity_counts = dict(zip(key_actors_counts['Entity'], key_actors_counts['Counts']))
generate_wordcloud({entity: entity_counts[entity] for entity in list(entity_counts)[:top_n]})

# # Display the key actors table when the button is checked
# st.subheader(f"Top {entity_type} in the Corpus")
# if show_raw_data:
#     st.dataframe(key_actors_counts)

st.markdown("**Note:** You might observe that I haven't combined similar names into a single entity, as even a slight difference in spelling might lead to distinct identifications. You can hover over the sidebar to choose the number of entities you wish to display, ranging from 10 to 100. You can also change the category of actors, either **Individual** or **Organization**")


# Placeholder for 1.b visualizations

# Load the new data source for PLTB word cloud
pltb_wordcloud_data = load_data("pltb_wordcloud.csv")

# Sidebar for PLTB Word Cloud
st.sidebar.subheader("PLTB: Word Cloud - Overall Corpus")
entity_type_pltb = st.sidebar.selectbox("Choose Entity Type (PLTB)", ['Individuals', 'Organizations'], key="pltb_entity_type")
top_n_pltb = st.sidebar.slider('Choose top N entities for word cloud (PLTB)', 10, 100, 50, key="pltb_top_n")

# Filter relevant entities based on entity type for PLTB
filtered_pltb_wordcloud_data = pltb_wordcloud_data[pltb_wordcloud_data['NER_Label'] == 'B-PER'] if entity_type_pltb == 'Individuals' else pltb_wordcloud_data[pltb_wordcloud_data['NER_Label'] == 'B-ORG']

# Group by entities and sum the counts for PLTB
pltb_counts = filtered_pltb_wordcloud_data.groupby('Entity')['Counts'].sum().reset_index()

# Filter entities with counts >= 2 for PLTB
pltb_counts = pltb_counts[pltb_counts['Counts'] >= 2]

# Sort entities by counts in descending order for PLTB
pltb_counts = pltb_counts.sort_values(by='Counts', ascending=False)

# Generate and display the word cloud for PLTB
st.subheader(f"PLTB: Word Cloud for Top {top_n_pltb} {entity_type_pltb}")
pltb_entity_counts = dict(zip(pltb_counts['Entity'], pltb_counts['Counts']))
generate_wordcloud({entity: pltb_entity_counts[entity] for entity in list(pltb_entity_counts)[:top_n_pltb]})

st.markdown("**Note:** You might observe that I haven't combined similar names into a single entity, as even a slight difference in spelling might lead to distinct identifications. You can hover over the sidebar to choose the number of entities you wish to display, ranging from 10 to 100. You can also change the category of actors, either **Individual** or **Organization**")


# === COMPONENT 2 ===




# Dashboard Title
st.title("PLTS Cirata: Media Coverage Analysis")

# Sidebar Title
st.sidebar.title("PLTS Analysis Sidebar")

# Context for the PLTS Coverage
st.subheader("PLTS Coverage")
st.markdown("In this segment, we will delve into how frequently major Indonesian newspapers cover the topic of PLTS, the segments under which they fall, the key actors frequently referred to, and the primary discussions related to PLTS Cirata. The sequence of media coverage will be as follows: Detik, CNBC, and Tribun. The name of the media source will be prominently displayed on top of the visualizations, along with its content. In some instances, the analysis is still ongoing (such as key ideas), as I require more time to produce a refined result and extrapolate the outcome to the entire dataset.")

@st.cache
def load_data(filepath):
    return pd.read_csv(filepath)

aggregated_counts = load_data("aggregated_counts.csv")
people_counts = aggregated_counts[aggregated_counts['NER_Label'] == 'B-PER'].set_index("Entity")["Counts"].to_dict()
org_counts = aggregated_counts[aggregated_counts['NER_Label'] == 'B-ORG'].set_index("Entity")["Counts"].to_dict()

# Function to generate and display word cloud
def generate_wordcloud(data_counts):
    wordcloud = WordCloud(width=800, height=400, background_color ='white').generate_from_frequencies(data_counts)
    
    # Create a figure and axis object explicitly
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    
    st.pyplot(fig)  # Pass the specific figure object to st.pyplot


# Sidebar Feature for Detik Analysis
st.sidebar.subheader("Detik Analysis - Date Range")
detik_start_year = st.sidebar.slider("Start Year - Detik", min_value=2000, max_value=2023, value=2000)
detik_end_year = st.sidebar.slider("End Year - Detik", min_value=2000, max_value=2023, value=2023)

# Detik Analysis
detik_plts_copy = load_data("detik_plts_cleaned.csv")
detik_plts_copy = detik_plts_copy[(detik_plts_copy['Year'] >= detik_start_year) & (detik_plts_copy['Year'] <= detik_end_year)]

st.subheader("Detik Analysis: Number of PLTS Articles")
st.markdown("Here, you can see the distribution of PLTS coverage (both related to PLTS Cirata and not—refer to the keywords provided at the top of the page) across the years.")
# Histogram for Detik Number of PLTS Articles
detik_plts_dis = px.histogram(detik_plts_copy, x='Year', nbins=int(detik_end_year - detik_start_year + 1))
detik_plts_dis.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of PLTS Articles")
st.plotly_chart(detik_plts_dis)
st.markdown("**Note**: Detik began discussing solar PV even before 2010, although the coverage was minimal. The attention to this issue increased in 2015 and continued to rise before a decrease in 2019. However, a significant surge was observed in 2020, and the trend has continued to grow until 2022. Data for 2023 is incomplete as I have collected articles only up to August 2023.")

st.subheader("Detik Analysis: Articles by Segment")

# Histogram for Detik by Segment
detik_plts_seg = px.histogram(detik_plts_copy, x='Year', color='Segment', nbins=int(detik_end_year - detik_start_year + 1))
detik_plts_seg.update_layout(bargap=0.1)
st.plotly_chart(detik_plts_seg)
st.markdown("**Note:** Segments might be associated with the departments or focuses of the media outlets. In this case, coverage related to PLTS on Detik.com is predominantly reported by the 'Finance' department, as detikFinance comprises a significant proportion of the overall coverage.")

# Sidebar for Word Cloud
st.sidebar.subheader("Word Cloud Options", key=20)
entity_type = st.sidebar.selectbox("Choose Entity Type", ['Individuals', 'Organizations'], key=100)
top_n = st.sidebar.slider('Choose top N entities for word cloud', 10, 100, 50, key='slider1')

# Word Cloud Visualization
if entity_type == 'Individuals':
    freq_data = people_counts
else:
    freq_data = org_counts

sorted_freq_data = dict(sorted(freq_data.items(), key=lambda item: item[1], reverse=True)[:top_n])
st.subheader(f"Word Cloud: Top {top_n} {entity_type}")
generate_wordcloud(sorted_freq_data)
st.markdown("Here, stakeholders exclusively identified from the Detik corpus on PLTS are presented. You can choose the number of individuals you wish to observe, ranging from 10 to 100. Hover over the sidebar for customization options")

# Sidebar Feature for CNBC Analysis
st.sidebar.subheader("CNBC Analysis - Date Range")
cnbc_start_year = st.sidebar.slider("Start Year - CNBC", min_value=2000, max_value=2023, value=2000)
cnbc_end_year = st.sidebar.slider("End Year - CNBC", min_value=2000, max_value=2023, value=2023)

# CNBC Analysis
cnbc_plts_merged = load_data("cnbc_plts_merged.csv")
cnbc_plts_merged = cnbc_plts_merged[(cnbc_plts_merged['Year'] >= cnbc_start_year) & (cnbc_plts_merged['Year'] <= cnbc_end_year)]

st.subheader("CNBC Analysis: Number of PLTS Articles")
# Histogram for CNBC Number of PLTS Articles
cnbc_plts_dis = px.histogram(cnbc_plts_merged, x='Year', nbins=int(cnbc_end_year - cnbc_start_year + 1))
cnbc_plts_dis.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of Articles")
st.plotly_chart(cnbc_plts_dis)

st.subheader("CNBC Analysis: Articles by Segment")

# Histogram for CNBC by Segment
cnbc_plts_seg = px.histogram(cnbc_plts_merged, x='Year', color='Segment', nbins=int(cnbc_end_year - cnbc_start_year + 1))
cnbc_plts_seg.update_layout(bargap=0.1)
st.plotly_chart(cnbc_plts_seg)
st.markdown("**Notes:** XYZ (I will fill out this section later.)")

# Sidebar Feature for Tribun Analysis
st.sidebar.subheader("Tribun Analysis - Date Range")
tribun_start_year = st.sidebar.slider("Start Year - Tribun", min_value=2000, max_value=2023, value=2000)
tribun_end_year = st.sidebar.slider("End Year - Tribun", min_value=2000, max_value=2023, value=2023)

# Tribun Analysis
tribun_plts_merged = load_data("tribun_plts_merged.csv")
tribun_plts_merged = tribun_plts_merged[(tribun_plts_merged['Year'] >= tribun_start_year) & (tribun_plts_merged['Year'] <= tribun_end_year)]

st.subheader("Tribun Analysis: Number of PLTS Articles")
# Histogram for Tribun
tribun_plts = px.histogram(tribun_plts_merged, x='Year', nbins=int(tribun_end_year - tribun_start_year + 1))
tribun_plts.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of Articles")
st.plotly_chart(tribun_plts)
st.markdown("**Notes:** XYZ (I will fill out this section later.)")

# 2.d - Placeholder for other Media Analysis
st.markdown("#### Placeholder for Future Media Outlet PLTS Analysis")
st.markdown("Please integrate the structure provided above for other media outlets once their respective data and analysis are available.")



# === COMPONENT 3 ===



# Dashboard Title
st.title("PLTB Project Analysis")

# Sidebar Title
st.sidebar.title("PLTB Analysis Sidebar")

# Context for the PLTB Coverage
st.subheader("PLTB Coverage")
st.markdown("In this section, we will delve deeper into the frequency with which major Indonesian newspapers cover the topic, what segments they fall under, and the main discussions they entail.")

@st.cache
def load_data(filepath):
    return pd.read_csv(filepath)

# Sidebar Feature for Detik Analysis
st.sidebar.subheader("Detik PLTB Analysis - Date Range")
detik_pltb_start_year = st.sidebar.slider("Start Year - Detik", min_value=2000, max_value=2023, value=2000, key="detik_pltb_start_year")
detik_pltb_end_year = st.sidebar.slider("End Year - Detik", min_value=2000, max_value=2023, value=2023, key="detik_pltb_end_year")

# Detik PLTB Analysis
detik_pltb_copy = load_data("detik_pltb_cleaned.csv")
detik_pltb_copy = detik_pltb_copy[(detik_pltb_copy['Year'] >= detik_pltb_start_year) & (detik_pltb_copy['Year'] <= detik_pltb_end_year)]

st.subheader("Detik PLTB Analysis: Number of Articles")
# Histogram for Detik Number of Articles
detik_pltb_dis = px.histogram(detik_pltb_copy, x='Year', nbins=int(detik_pltb_end_year - detik_pltb_start_year + 1))
detik_pltb_dis.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of Articles")
st.plotly_chart(detik_pltb_dis)

st.subheader("Detik PLTB Analysis: Articles by Segment")
# Histogram for Detik by Segment
detik_pltb_seg = px.histogram(detik_pltb_copy, x='Year', color='Segment', nbins=int(detik_pltb_end_year - detik_pltb_start_year + 1))
detik_pltb_seg.update_layout(bargap=0.1)
st.plotly_chart(detik_pltb_seg)

# Sidebar Feature for CNBC Analysis
st.sidebar.subheader("CNBC PLTB Analysis - Date Range")
cnbc_pltb_start_year = st.sidebar.slider("Start Year - CNBC", min_value=2000, max_value=2023, value=2000, key="cnbc_pltb_start_year")
cnbc_pltb_end_year = st.sidebar.slider("End Year - CNBC", min_value=2000, max_value=2023, value=2023, key="cnbc_pltb_end_year")

# CNBC PLTB Analysis
cnbc_pltb_merged = load_data("cnbc_pltb_merged.csv")
cnbc_pltb_merged = cnbc_pltb_merged[(cnbc_pltb_merged['Year'] >= cnbc_pltb_start_year) & (cnbc_pltb_merged['Year'] <= cnbc_pltb_end_year)]

st.subheader("CNBC PLTB Analysis: Number of Articles")

# Histogram for CNBC Number of Articles
cnbc_pltb_dis = px.histogram(cnbc_pltb_merged, x='Year', nbins=int(cnbc_pltb_end_year - cnbc_pltb_start_year + 1))
cnbc_pltb_dis.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of Articles")
st.plotly_chart(cnbc_pltb_dis)

st.subheader("CNBC PLTB Analysis: Articles by Segment")

# Histogram for CNBC by Segment
cnbc_pltb_seg = px.histogram(cnbc_pltb_merged, x='Year', color='Segment', nbins=int(cnbc_pltb_end_year - cnbc_pltb_start_year + 1))
cnbc_pltb_seg.update_layout(bargap=0.1)
st.plotly_chart(cnbc_pltb_seg)

# Sidebar Feature for Tribun Analysis
st.sidebar.subheader("Tribun PLTB Analysis - Date Range")
tribun_pltb_start_year = st.sidebar.slider("Start Year - Tribun", min_value=2000, max_value=2023, value=2000, key="tribun_pltb_start_year")
tribun_pltb_end_year = st.sidebar.slider("End Year - Tribun", min_value=2000, max_value=2023, value=2023, key="tribun_pltb_end_year")

# Tribun PLTB Analysis
tribun_pltb_merged = load_data("tribun_pltb_merged.csv")
tribun_pltb_merged = tribun_pltb_merged[(tribun_pltb_merged['Year'] >= tribun_pltb_start_year) & (tribun_pltb_merged['Year'] <= tribun_pltb_end_year)]

st.subheader("Tribun PLTB Analysis: Number of Articles")
# Histogram for Tribun
tribun_pltb = px.histogram(tribun_pltb_merged, x='Year', nbins=int(tribun_pltb_end_year - tribun_pltb_start_year + 1))
tribun_pltb.update_layout(bargap=0.1, xaxis_title="Year", yaxis_title="Number of Articles")
st.plotly_chart(tribun_pltb)





