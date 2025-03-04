import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from components.FittingModel import preprocessing

class Summary:
    def __init__(self,data,one_class,time,attribute,weight,time_range):
        self.data=data
        self.one_class=one_class
        self.time=time
        self.attribute=attribute
        self.weight=weight
        self.time_range=time_range

    def  Globe_model(self,data,selected_attribute,selected_year):   
        # Ensure 'Country' column has valid country names or ISO codes for mapping
        if True:
            filtered_df = data[data[st.session_state.time_name]==selected_year]
            max_attribute = max(data[selected_attribute])
            min_attribute = min(data[selected_attribute])
            
            # Plotting the 3D interactive map
            fig = px.choropleth(
            filtered_df,
            locations=st.session_state.class_name,
            locationmode="country names",
            color=selected_attribute,
            hover_name=st.session_state.class_name,
            projection="orthographic",
            color_continuous_scale="PuBuGn",
            range_color=[min_attribute, max_attribute]
            )

            # Customize the colorbar title and add more layout features
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{selected_attribute}"
                ),
                # Add more layout customizations
                title_font=dict(size=24, family='Arial', color='darkblue'),
                geo=dict(
                    showland=True,
                    landcolor='#DCDCDC',
                    showocean=True,
                    oceancolor='#F0FFFF',
                    showlakes=True,
                    lakecolor='#4682B4',
                    showrivers=True,
                    rivercolor='#4682B4'
                ),
                width=400,
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )

            # Add annotations for better visualization
            fig.add_annotation(
                text="The darker the color, the larger the value.",
                xref="paper", yref="paper",
                x=0.5, y=0.1, showarrow=False,
                font=dict(size=12, family='Arial'),
            )
            
            # Display the map in Streamlit
            st.plotly_chart(fig)

    def render_barchart(self,data, year, metric):
        filtered_data = data[data[st.session_state.time_name] == year]
        top_25 = filtered_data.nlargest(10, metric)
        bottom_25 = filtered_data.nsmallest(10, metric)
        option = st.sidebar.radio(
                "Please Select One Direction:",
                options=["Descending","Ascending"]
            )
        if option=="Descending":
            st.subheader(f"Top 10 {st.session_state.class_name}")
            chart = alt.Chart(top_25).mark_bar(color = "#4682B4").encode(
                    x=alt.X(metric, title=metric),
                    y=alt.Y(st.session_state.class_name, sort="-x", title=st.session_state.class_name),
                    tooltip=[st.session_state.class_name, metric]
                ).properties(width=400, height=330, background='transparent').interactive()
            st.altair_chart(chart)
        else:
            st.subheader(f"Bottom 10 {st.session_state.class_name}")
            chart = alt.Chart(bottom_25).mark_bar(color = "#4682B4").encode(
                x=alt.X(metric, title=metric),
                y=alt.Y(st.session_state.class_name, sort="x", title=st.session_state.class_name),
                tooltip=[st.session_state.class_name, metric]
            ).properties(width=400, height=330, background='transparent').interactive()
            st.altair_chart(chart)

    def missing_display(self,data,metric):
        a = data
        # 计算均值透视表，并处理缺失值
        pivot_table = a.pivot_table(index=st.session_state.class_name,
                                    columns=st.session_state.time_name,
                                    values=metric,
                                    aggfunc='mean')
        
        # 由于 Plotly 不直接支持 NaN 值作为热图的一部分，我们需要将它们替换为一个特殊的值
        # 这里我们选择使用 None，因为 Plotly 在处理热图时会忽略 None 值
        fill_value = max(data[metric])*100000000  # 或者你可以计算列/行的均值来填充：fill_value = pivot_table.mean().mean()
        pivot_table_filled = pivot_table.fillna(fill_value) 
        
        # 将透视表转换为 Plotly 可以接受的格式
        z = pivot_table_filled.to_numpy() if not pivot_table_filled.isnull().values.any() else pivot_table_filled.apply(lambda x: x.to_numpy() if pd.notnull(x).all() else [None]*len(x)).to_numpy()
        x = pivot_table_filled.columns
        y = pivot_table_filled.index
        
        # 创建热图
        heatmap = go.Heatmap(z=z,
                            x=x,
                            y=y,
                            colorscale="PuBuGn",  # 颜色映射
                            showscale=False,        # 显示颜色条
                            colorbar_title=metric, # 颜色条标题
                            text=np.where(np.isnan(z), 'Missing', ''), # 在缺失数据的位置显示文本
                            hoverinfo='text+x+y+z') # 鼠标悬停时显示的信息
        
        # 设置图表标题和轴标签
        layout = go.Layout(
                        xaxis_title=st.session_state.time_name,
                        yaxis_title=st.session_state.class_name,
                        xaxis_tickangle=45,
                                width=400,
                                height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False) # 旋转 x 轴标签
        
        # 创建图表对象
        fig = go.Figure(data=[heatmap], layout=layout)
        
        # 在 Streamlit 中显示图表
        st.plotly_chart(fig)

    def display_air_index(self,data, selected_country, weights,time_range):
        formatted_weights = [f"{w:.2f}" for w in weights]
        
        # 污染物名称及其标准
        pollutants_info = {
            'Nitrogen_oxide_Nox': {
                "Standard": "0-100 µg/m³ (Good), 101-200 µg/m³ (Moderate), >200 µg/m³ (Hazardous)",
                "Health Impacts": "Can cause respiratory problems and worsen asthma."
            },
            'Sulphur_dioxide_SO2': {
                "Standard": "0-50 µg/m³ (Good), 51-150 µg/m³ (Moderate), >150 µg/m³ (Hazardous)",
                "Health Impacts": "Can cause throat irritation, coughing, and aggravate lung diseases."
            },
            'Carbon_monoxide_CO': {
                "Standard": "0-4.4 µg/m³ (Good), 4.5-9.4 µg/m³ (Moderate), >10 µg/m³ (Hazardous)",
                "Health Impacts": "High levels can cause headaches, dizziness, and poisoning."
            },
            'Organic_carbon_OC': {
                "Standard": "Varies (based on region and conditions)",
                "Health Impacts": "Long-term exposure can lead to respiratory and cardiovascular diseases."
            },
            'NMVOCs': {
                "Standard": "Varies (based on region and conditions)",
                "Health Impacts": "Contributes to ozone formation, leading to respiratory issues."
            },
            'Black_carbon_BC': {
                "Standard": "Varies (based on region and conditions)",
                "Health Impacts": "Affects lung health, aggravates asthma and heart conditions."
            },
            'Ammonia_NH3': {
                "Standard": "0-20 µg/m³ (Good), >20 µg/m³ (Hazardous)",
                "Health Impacts": "Can irritate eyes, skin, and respiratory systems."
            }
        }
        
        # 空气污染数据列名
        cols = st.session_state.index_components
        year_cols = [st.session_state.time_name] + cols
        
        # Filter data for the selected country or global
        if selected_country != "Global":
            country_data = data[year_cols]
        elif selected_country == "Global":
            country_data = data[year_cols].groupby(st.session_state.time_name).mean().reset_index()
        
        # 计算加权空气污染指数
        country_data = country_data.dropna()
        if time_range != False:
            country_data = country_data[country_data[st.session_state.time_name].between(time_range[0], time_range[1])]
        Year = country_data[st.session_state.time_name]
        n = len(cols)
        
        # Apply weights to the pollution data
        for i in range(n):
            if "preprocess_index" in st.session_state:
                country_data[cols[i]] = preprocessing(country_data,st.session_state.preprocess_index[i],cols[i])
            country_data[cols[i]] = country_data[cols[i]] * weights[i] * 100
        vals_array = country_data[cols].values.T
        
        # Initialize the plot
        fig = go.Figure()
        
        # Add traces for each pollutant
        for i, vals in enumerate(vals_array):
            pollutant = cols[i]
            
            # 通过 formatted_weights 添加权重，并在图表中展示
            if (st.session_state.data_state=="Sample") & (pollutant in st.session_state.index_components_default):
                hovertext = f"<b>{pollutant}</b><br><b>Year:</b> %{{x}}<br><b>Value:</b> %{{y}}<br><b>Standard:</b> {pollutants_info[pollutant]['Standard']}<br><b>Health Impacts:</b> {pollutants_info[pollutant]['Health Impacts']}"
            else:
                hovertext = f"<b>{pollutant}</b><br><b>Year:</b> %{{x}}<br><b>Value:</b> %{{y}}<br><b>Component:</b>{pollutant}"

            fig.add_trace(
                go.Bar(x=Year, y=vals, name=f"{pollutant} ({formatted_weights[i]})", 
                    hovertemplate=hovertext)
            )
        
        # Update the layout of the figure
        fig.update_layout(
            barmode="stack",
            font_family="Averta",
            hoverlabel_font_family="Averta",
            xaxis_title_text=st.session_state.time_name,
            xaxis_title_font_size=18,
            xaxis_tickfont_size=16,
            hoverlabel_font_size=8,
            height=380,
            width=800,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                yanchor="bottom",
                y=1,  # 将图例放置在图表的底部
                xanchor="center",
                x=0.5
            )
        )
        
        # Display the plot
        st.plotly_chart(fig)


    def display_summary(self, data):
        cols = st.session_state.index_components
        filtered_data=data
        #filtered_data=data.drop(cols, axis=1)
        numeric_cols = filtered_data.select_dtypes(include='number')

        if not numeric_cols.empty:
            summary_stats = numeric_cols.describe().T
            summary_stats.insert(3,'variance',numeric_cols.var())
            st.write(summary_stats)
            # 为每一列绘制小提琴图
            st.subheader("Data Visualization")
            visual_data=filtered_data.drop([st.session_state.class_name,st.session_state.time_name], axis=1)
            colors = ["#6495ED","#4B0082","#3CB371","#808000","#FFD700","#800000"]
            violinplots = []
            for i,column in enumerate(visual_data.columns):
                if column != 'Year':  # 假设'Year'列不是您想要绘制小提琴图的列
                    fig = px.violin(visual_data, x=column, box=True, points=False,
                                    color_discrete_sequence=[colors[i % len(colors)]])  # 使用不同的颜色序列 #
                    fig.update_layout(yaxis=dict(rangemode="tozero"),width=400,height=300,margin=dict(l=0, r=0, t=0, b=0),
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)')  # 设置y轴范围为0到最大值
                    violinplots.append(fig)
            
            cols = st.columns(3)
            n=len(visual_data.columns)

            with cols[0]:
                c1=[]
                for i in range(n):
                    if i%3==1:
                        c1.append(i)
                for i in c1:
                    st.plotly_chart(violinplots[i], key=f"violinplot_{i}")
            with cols[1]:
                c2=[]
                for i in range(n):
                    if i%3==2:
                        c2.append(i)
                for i in c2:
                    st.plotly_chart(violinplots[i], key=f"violinplot_{i}")
            with cols[2]:
                c3=[]
                for i in range(n):
                    if i%3==0:
                        c3.append(i)
                for i in c3:
                    st.plotly_chart(violinplots[i], key=f"violinplot_{i}")


    def display_key_indicator(self, data):
        filtered_data=data.drop(st.session_state.index_components, axis=1)
        numeric_cols = filtered_data.select_dtypes(include='number')

        if not numeric_cols.empty:
            # Visualization of statistics
            st.subheader("Key Indicator Distribution")
            stats_option = st.selectbox(
                "Please Select the Statistical Indicator:",
                options=["Mean", "Median", "Variance"],
            )

            # Prepare the data for visualization
            if stats_option == "Mean":
                chart_data = numeric_cols.mean().reset_index()
            elif stats_option == "Median":
                chart_data = numeric_cols.median().reset_index()
            elif stats_option == "Variance":
                chart_data = numeric_cols.var().reset_index()

            chart_data.columns = ["Attribute", "Value"]

            #Call the dual-axis chart function
                    # Separate GDP (or other large-scale attributes) from the rest
            large_scale_attr = "GDP"
            small_scale_data = chart_data[chart_data["Attribute"] != large_scale_attr]
            large_scale_data = chart_data[chart_data["Attribute"] == large_scale_attr]

            # Create the dual-axis figure
            fig = go.Figure()

            # Add bar chart for smaller scale attributes
            fig.add_trace(
                go.Bar(
                    x=small_scale_data["Attribute"],
                    y=small_scale_data["Value"],
                    name="Other Attributes",
                    marker_color="#4682B4",
                    yaxis="y1",  # Primary Y-axis
                )
            )

            # Add line chart for large-scale attribute (GDP)
            if not large_scale_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=large_scale_data["Attribute"],
                        y=large_scale_data["Value"],
                        mode="lines+markers",
                        name=large_scale_attr,
                        marker_color="#D2691E",
                        yaxis="y2",  # Secondary Y-axis
                    )
                )

            # Update layout for dual axes
            fig.update_layout(
                title="Dual-Axis Visualization",
                xaxis_title="Attributes",
                yaxis=dict(
                    title="Value (Small Scale Attributes)",
                    titlefont=dict(color="#4682B4"),
                    tickfont=dict(color="#4682B4"),
                ),
                yaxis2=dict(
                    title="Value (Large Scale Attribute: GDP)",
                    titlefont=dict(color="#D2691E"),
                    tickfont=dict(color="#D2691E"),
                    overlaying="y",
                    side="right",
                ),
                legend=dict(x=0.1, y=1.1),
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        paper_bgcolor='rgba(0,0,0,0)'
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig)

        else:
            st.warning("No Useful Attributes")
    
        

        
    def display(self):
        data=self.data
        map_option=self.attribute
        selected_year=self.time
        selected_country=self.one_class
        normalized_weights=self.weight
        time_range=self.time_range

        if selected_country != "Global":
            filtered_data = data[data[st.session_state.class_name] == selected_country]
        else:
            filtered_data = data

        col1, col2 = st.columns([1, 1],gap='small')
        # Country HeatMap Display
        with col1:
            option = st.sidebar.radio(
                f"Please Select a Way to Display {map_option} overtime:",
                options=["Heatmap","Bar Chart","Missing Value"]
            )
            if option == "Heatmap":
                st.subheader(f"3D {map_option} HeatMap")
                self.Globe_model(filtered_data,  map_option, selected_year)
            elif option == "Bar Chart":
                st.subheader(f"{map_option} Bar Chart")
                self.render_barchart(filtered_data, selected_year, map_option)
            elif option == "Missing Value":
                st.subheader(f"{map_option} Missing Value")
                self.missing_display(filtered_data,map_option)
        # Air Pollution Index Display
        with col2:
            st.subheader(f"{st.session_state.index_name}")
            self.display_air_index(data=filtered_data,selected_country=selected_country,weights=normalized_weights,time_range=time_range)
        # Summary Statistics for Numeric Columns Display
        st.subheader(f"Data Statistic Summaries")
        self.display_summary(filtered_data)
        self.display_key_indicator(filtered_data)


