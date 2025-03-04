import streamlit as st
import pandas as pd
import base64
from PIL import Image
from components.Select import MySelect
from components.SampleInfo import SampleDefault
from components.HomePage import Summary
from components.TimeSeries import TimeDisplay
from components.CrossSection import GlobalDisplay
from components.Comparison import CompareDisplay

st.set_page_config(layout="wide")
def sidebar_bg(side_bg):
    side_bg_ext = 'png'

    with open(side_bg, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            top: 10px;
            left: 10px;
            background: url(data:image/{side_bg_ext};base64,{encoded_image}) no-repeat left top;
            background-size: 15%;
            padding-left: 0px; /* Adjust this value based on the size of your image */
            padding-top: 20px; /* Adjust this value to control the vertical position of the text */
            position: relative;
        }}
        [data-testid="stSidebar"] > div:first-child::after {{
            content: 'Impact Research Platform';
            position: absolute;
            left: 0px;
            top: 5px;
            padding-left: 60px; /* Adjust this value based on the size of your image */
            font-size: 16px; /* Adjust this value to control the font size */
            font-weight: 600;
            color: #000; /* Adjust this value to control the font color */
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

#Test function
def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )
    
def main_banner(image_path, width=None):
    # 加载图像文件
    image = Image.open(image_path)
    image = image.resize((width, 150), Image.LANCZOS)
    
    # 在页面最上方显示图像
    st.image(image, use_container_width =True)

def colorbg():
    st.markdown(
        """
        <style>
        .stApp { background-color: #DCDCDC

; }
        </style>
        """,
        unsafe_allow_html=True
    )
def animation():
    # load JavaScript
    st.markdown(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const observer = new MutationObserver(() => {
                const components = document.querySelectorAll('.stApp .element-container');
                components.forEach(component => {
                    if (!component.classList.contains('component-animation')) {
                        component.classList.add('component-animation');
                    }
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        });
        </script>
        """,
        unsafe_allow_html=True,
    )

    # load css file
    st.markdown(
        """
        <link href="assets/styles.css" rel="stylesheet" type="text/css">
        """,
        unsafe_allow_html=True,
    )

#main_bg('assets/color.png')
sidebar_bg('assets/hku-logo.png')
colorbg()
main_banner('assets/top.jpg', width=800)
#animation()
#没效果先不用了

@st.cache_data
def load_data():
    return pd.read_csv("data/ALL.csv")

data_default = load_data()
sample = SampleDefault(data_default)
sample.default_value()
sample.sample_display_default()

app_mode = st.sidebar.selectbox('Select Page',["Home", "Time-Series Analysis", "Cross-Section Data Analysis", 
                                               "Comparison & Seperate Analysis","Document Upload"], 
                                index=0, key="page_radio")

if app_mode == "Home":
    st.header("Welcome Home!")
    st.text("This page shows a summary of the entire data. You can get custom summary results by changing the options in the sidebar. Here's how to use it:")
    # Add "i" icon for instruction/help
    help_button = st.button("ℹ️ Click Me for Instruction")  
    if help_button:
        with st.expander("Page Instructions"):
            st.markdown(
                f"""
                **How to use the platform:**
                1. **Select a Index**: Slide to select relative weight of each index components to define the index. Default is based on variance of components, which can be obtained by double-clicking the "Reset" button.
                2. **Select a {st.session_state.class_name}**: Choose the {st.session_state.class_name} you want to focus on.
                3. **Select an Attribute**: Pick the attribute you want to analyze.
                4. **Adjust the Time**: Slide to select the time you're interested in.
                5. **Adjust Time Range**: Select the time range for the analysis.
                6. **View Results**: Based on your selections, the visualizations will update, showing trends and comparisons of {st.session_state.index_name} with other factors.

                **Feel free to explore and understand global {st.session_state.index_name} patterns and their impact over time!**
                """
            )

    #Load and display the stored value  
    st.markdown("Current dataset is shown below, you can download it as file ~.csv:")
    st.dataframe(st.session_state.dataset)
    st.text(f"""
            Let us explore the dynamic relationship between {st.session_state.index_name} and other factors across different {st.session_state.class_name} and {st.session_state.time_name} — unlocking insights into their trends and implications from a broad perspective.
            """)  
    # Add interactive link for the latest air pollution data
    if st.session_state.data_state == "Sample":
        st.markdown(
            """
            <p style="font-size:18px;">
                <a href="https://www.who.int/health-topics/air-pollution" target="_blank" style="color:#1E90FF; font-weight:bold;">
                    Click here to explore the latest global air pollution data from WHO!
                </a>
            </p>
            """, unsafe_allow_html=True
        )

    #Select operation
    select = MySelect()
    #Select index weights
    select.select_weight()
    #Select custom components
    select.components_select(one_class=True,attribute=True,time=True,time_range=True)

    #Display operation
    summary = Summary(st.session_state.dataset,
                      st.session_state.selected_country,
                      st.session_state.year,
                      st.session_state.selected_attribute,
                      st.session_state.weights,
                      st.session_state.time_range)
    summary.display()
    # display(st.session_state.dataset,st.session_state.selected_country,
    #         st.session_state.selected_attribute,st.session_state.year,
    #         st.session_state.weights)


if app_mode == "Time-Series Analysis":
    st.header("📈 Analysis by Time Trend")
    st.write(f"This page allows you to analyze time trends of {st.session_state.index_name} and other metrics ({st.session_state.variables[0]}, {st.session_state.variables[1]}, etc.) across multiple {st.session_state.class_name} over time. Here's how to use it:")
    # Page instruction button
    instruction_button = st.button("📖 Page Instructions", key="instruction_button")  
    if instruction_button:
        with st.expander("Page Instructions"):
            st.markdown(
                f"""
                **How to Use:**
                1. **Select {st.session_state.class_name}**: Use the sidebar to choose the {st.session_state.class_name} you want to analyze. You can double click the "Choose ALL", "Cancle ALL","Default" buttons for Quick Operation.
                2. **Select Attribute**: Choose the attribute that you want to compare against {st.session_state.index_name}.
                3. **Adjust Time Range**: Select the time range for the analysis.
                4. **View Visualizations**: 
                    - **Map**: Visualizes the distribution of the selected attribute across Countries (if Class input is Country).
                    - **Scatter Plot**: Visualizes the relationship between {st.session_state.index_name} and the selected attribute.
                    - **Line Chart**: Displays the trends of {st.session_state.index_name} and the selected attribute over time for the chosen {st.session_state.class_name}.

                **Key Features:**
                - The scatter plot allows you to see how {st.session_state.index_name} correlates with other factors through time.
                - The line chart provides time trend analysis, showing how {st.session_state.index_name} and selected attribute has evolved over the years.

                Enjoy exploring the data!
                """
            )
    
    #Select operation
    select = MySelect()
    #Select custom components
    select.components_select(classes=True,attribute=True,include_i=False,time_range=True)

    #Display operation
    time_display = TimeDisplay(st.session_state.dataset,
                      st.session_state.selected_countries,
                      st.session_state.time_range,
                      st.session_state.selected_attribute,
                      )
    time_display.display_country_map_t()

    col1, col2 = st.columns([3, 2], gap='small')
    with col1:
        st.subheader(f"Scatter Plot")
        time_display.render_scatterplot()
    
    with col2:
        st.subheader("Line Chart")
        time_display.render_plotchart()


if app_mode == "Cross-Section Data Analysis":
    st.header("🌍 Analysis by Countries")
    st.text(f"This page allows you to analyze {st.session_state.index_name} and other metrics ({st.session_state.variables[0]}, {st.session_state.variables[1]}, etc.) for a given {st.session_state.time_name} across different {st.session_state.class_name}. Here's how to use it:")   
    # Page instruction button
    instruction_button = st.button("📖 Page Instructions", key="instruction_button_cross_section")  # Instruction Button for Cross-Section
    if instruction_button:
        with st.expander("Page Instructions"):
            st.markdown(
                f"""
                **How to Use:**
                1. **Select Time**: Choose the time for which you want to analyze the data.
                2. **Select Attribute**: Choose the attribute that you want to compare against {st.session_state.class_name}.
                3. **View Visualizations**: 
                    - **Map**: Visualizes the distribution of the selected attribute across Countries (if Class input is Country).
                    - **Bar Chart**: Compares the selected attribute across {st.session_state.class_name} for the chosen time.
                    - **Scatter Plot**: Shows the correlation between {st.session_state.index_name} and the selected attribute.

                **Key Features:**
                - This page helps you compare different {st.session_state.class_name} based on the selected time and attribute.
                - It also allows you to have a global insight on how {st.session_state.index_name} correlates with other factors.

                Enjoy exploring the data!
                """
            )

    #Select operation
    select = MySelect()
    #Select custom components
    select.components_select(attribute=True,include_i=True,time=True)

    #Display 
    global_display = GlobalDisplay(st.session_state.dataset,
                      st.session_state.year,
                      st.session_state.selected_attribute, )
    
    global_display.display_country_map()
    global_display.render_barchart()
    global_display.display_scatter_country()

if app_mode == "Comparison & Seperate Analysis":
    st.header("⚔️ In-Depth Analysis") 
    st.text(f"This page allows you to compare two {st.session_state.class_name} or do {st.session_state.class_name}-specific analysis base on {st.session_state.index_name} and other metrics ({st.session_state.variables[0]}, {st.session_state.variables[1]}, etc.) for a chosen {st.session_state.time_name}. Here's how to use it:")
    # Page instruction button
    instruction_button = st.button("📖 Page Instructions", key="instruction_button_comparison")  
    if instruction_button:
        with st.expander("Page Instructions"):
            st.markdown(
                """
                **How to Use:**
                1. **Select Countries**: Choose two countries you want to compare.
                2. **Select Year**: Choose the year for which you want to analyze the data.
                3. **Select Attribute**: Choose the attribute (e.g., GDP, Inflation) that you want to compare across the two countries.
                4. **View Visualizations**: 
                    - **Radar Map**: Visualizes and compares the level of selected attributes.
                    - **Data Detail**: 
                    - **Map**: Visualizes the distribution of the selected attribute for both Countries (if Class input is Country).
                    - **Scatter Plot**: Compares Air Pollution between the two countries based on the selected attribute.

                **Key Features:**
                - This page provides an in-depth comparison of two countries and helps you understand the differences in air pollution and other key metrics.
                - You can see how different countries perform relative to each other across various attributes.

                Enjoy comparing the data!
                """
            )

    #Select operation
    select = MySelect()
    #Select custom components
    select.components_select(attribute=True,compare=True,attributes=True)

    #Display
    compare_display = CompareDisplay(st.session_state.dataset,
                      st.session_state.country1,
                      st.session_state.country2,
                      st.session_state.year,
                      st.session_state.selected_attribute,
                      st.session_state.selected_attributes,
                      )
    compare_display.comparison_map()
    compare_display.display_country_map_compare()
    compare_display.render_scatterplot_compare()


if app_mode == "Document Upload":
    st.header("📄 Document Upload")
    
    # Page instruction button
    instruction_button = st.button("📖 Page Instructions", key="instruction_button_document_upload")  # Instruction Button for Document Upload
    if instruction_button:
        with st.expander("Page Instructions"):
            st.markdown(
                """
                This page allows you to upload your dataset and analyze its key features. Here's find out how to use it:

                **How to Use:**
                1. **Upload Your Dataset**: Click the 'Upload File' button to upload your CSV file containing the data.
                2. **Preview the Data**: After uploading, the first few rows of your dataset will be displayed for preview.
                3. **Analyze Basic Statistics**: The page automatically calculates key metrics like mean, median, and variance for the numeric attributes in your dataset.
                4. **Explore the Distribution**: Visualize the distribution of individual attributes using histograms.
                5. **Dual-Axis Chart**: This chart shows the relationship between the mean and variance of each attribute to help identify patterns or anomalies.

                **Key Features:**
                - You can explore the dataset, analyze key statistics, and visualize the data.
                - At the bottom of the page, you can download the statistical summary and visualizations for further analysis.

                Enjoy uploading and analyzing your dataset!
                """
            )
    select = MySelect()
    select.state_data()
    select.select_names()
    select.select_index()
    


