import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
from components.FittingModel import select_fit, fitting, plot_fit

class CompareDisplay:
    def __init__(self,data,country1,country2,year,metric,metrics):
        self.data=data
        self.country1=country1
        self.country2=country2
        self.year=year
        self.metric = metric
        self.metrics = metrics

    # divide into different levels 
    def assign_levels(self, data, metrics):
        levels = {}

        for metric in metrics:
            # check and fill NA
            if data[metric].isnull().any():
                data[metric].fillna(data[metric].median(), inplace=True)

            unique_values = data[metric].unique()
            if len(unique_values) == 1:
                # create ranges if all values are the same
                bins = [unique_values[0] - 1, unique_values[0], unique_values[0] + 1]
            else:
                # calculate the ranges
                bins = np.unique(np.percentile(data[metric].astype(float), np.linspace(0, 100, 11)))
                if len(bins) < 2:
                    bins = [data[metric].min() - 1, data[metric].max() + 1]  # create the ranges
                else:
                    bins[-1] += 1  # make sure greatest value lies in the back

            # use bin and deal with NA
            levels[metric] = pd.cut(data[metric], bins=bins, labels=range(1, len(bins)), include_lowest=True)
            # debug
            if 1 not in levels[metric].cat.categories:
                levels[metric] = levels[metric].cat.add_categories([1])
            # fill na with int
            levels[metric] = levels[metric].fillna(1).astype(int)
        return pd.DataFrame(levels)

    def create_radar_chart(self,metrics, data, country_name,fill_color):
        fig = go.Figure()

        # add data to chart
        fig.add_trace(go.Scatterpolar(
            r=data.values,
            theta=metrics,
            fill='toself',
            fillcolor=fill_color,
            line_color=fill_color,
            name=country_name
        ))
        # 自定义角度轴上的标签
        custom_labels = st.session_state.variables
        # settings
        fig.update_layout(
            polar=dict(
            radialaxis=dict(visible=True, range=[1, 10], color='#696969'),  # 等级范围为 1 到 10
            angularaxis=dict(
                ticktext=custom_labels,  # 自定义标签
                tickvals=metrics  # 这些标签对应的原始值
            )
        ),
            showlegend=False,
            width=300,
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    def comparison_map(self):
        data=self.data
        year=self.year
        country1=self.country1
        country2=self.country2
        metrics = self.metrics

        # select data according to user
        if year != False:
            data = data[(data[st.session_state.time_name] == year)]
        filtered_data = data[data[st.session_state.class_name].isin([country1, country2])]

        if st.session_state.index_name in filtered_data.columns:
            # levels and metrics
            graded_data = self.assign_levels(data, metrics)
            graded_data[st.session_state.class_name] = data[st.session_state.class_name]
            graded_data[st.session_state.time_name] = data[st.session_state.time_name]
            # if no enough data
            if filtered_data.shape[0] < 2:
                # get data
                if data[st.session_state.index_name].empty:
                    st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
                else:
                    # get data
                    if year != False:
                        graded_data=graded_data[graded_data[st.session_state.time_name] == year]
                    country1_data = graded_data[graded_data[st.session_state.class_name] == country1][metrics]
                    if country1_data.empty:
                        st.subheader(f"{year} Analysis of {st.session_state.class_name}")
                        st.error("Not enough data for Display")
                        st.subheader("Detailed Data")
                        st.error("Not enough data for Display")

                    else:
                        country1_data =  country1_data.iloc[0]
                        # draw radars
                        fig1 = self.create_radar_chart(metrics, country1_data, country1,'rgba(70, 130, 180, 0.5)')

                        # show radars
                        st.subheader(f"{year} Analysis of {st.session_state.class_name}")
                        st.plotly_chart(fig1, use_container_width=True)

                        # show data comparison
                        st.subheader("Detailed Data")
                        comparison_table = pd.DataFrame({
                            "metrics": metrics,
                            f"{country1} (level)": country1_data.values,
                            f"{country1} (original)": filtered_data[filtered_data[st.session_state.class_name] == country1][metrics].iloc[0].values,
                        })
                        st.dataframe(comparison_table, height=300,width=1000)
            else:
                # get data
                if data[st.session_state.index_name].empty:
                    st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
                else:
                    if year != False:
                        graded_data=graded_data[graded_data[st.session_state.time_name] == year]
                    country1_data = graded_data[graded_data[st.session_state.class_name] == country1][metrics]
                    country2_data = graded_data[graded_data[st.session_state.class_name] == country2][metrics]

                    if country1_data.empty or country2_data.empty:
                        st.subheader(f"{year} Analysis of {st.session_state.class_name}")
                        st.error("Not enough data for Display")
                        st.subheader("Detailed Data")
                        st.error("Not enough data for Display")
                    else:
                        country1_data =  country1_data.iloc[0]
                        country2_data =  country2_data.iloc[0]
                        # draw radars
                        fig1 = self.create_radar_chart(metrics, country1_data, country1,'rgba(70, 130, 180, 0.5)')
                        fig2 = self.create_radar_chart(metrics, country2_data, country2,'rgba(255, 140, 0, 0.5)')

                        # show radars
                        st.subheader(f"{year} Comparison of {st.session_state.class_name}")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.plotly_chart(fig1, use_container_width=True)
                        with col2:
                            st.plotly_chart(fig2, use_container_width=True)

                        # show data comparison
                        st.subheader("Detailed Data Comparison")
                        comparison_table = pd.DataFrame({
                            "metrics": metrics,
                            f"{country1} (level)": country1_data.values,
                            f"{country2} (level)": country2_data.values,
                            "difference (level)": country1_data.values - country2_data.values,
                            f"{country1} (original)": filtered_data[filtered_data[st.session_state.class_name] == country1][metrics].iloc[0].values,
                            f"{country2} (original)": filtered_data[filtered_data[st.session_state.class_name] == country2][metrics].iloc[0].values,
                            "difference (original)": filtered_data[filtered_data[st.session_state.class_name] == country1][metrics].iloc[0].values - filtered_data[filtered_data[st.session_state.class_name] == country2][metrics].iloc[0].values,
                        })
                        st.dataframe(comparison_table, height=300,width=1000)
 


    def display_country_map_compare(self):
        data=self.data
        year=self.year
        country1=self.country1
        country2=self.country2
        map_attribute = self.metric

        country_data=data
        if map_attribute in country_data.columns:
            max_attribute = max(country_data[map_attribute])
            min_attribute = min(country_data[map_attribute])
            country_data=data[(data[st.session_state.class_name].isin([country1, country2])) & 
                            (data[st.session_state.time_name]==year)]
            st.subheader(f"Heatmap for {map_attribute}")
            # Plot the selected attribute trend on a map
            fig = px.choropleth(
                country_data,
                locations=st.session_state.class_name,
                locationmode="country names",
                color=map_attribute,
                hover_name=st.session_state.class_name,
                #animation_frame="Year",
                projection="miller",
                color_continuous_scale="PuBuGn",
                range_color=[min_attribute, max_attribute]
            )
            fig.update_layout(
                geo=dict(
                    showframe=False, 
                    lakecolor='#fff4b9'
                ),
                annotations=[dict(
                    x=0.5,
                    y=0.02,
                    xref='paper',
                    yref='paper',
                    text='The darker the color, the larger the value.',
                    showarrow=False
                )],
                font_family="Averta",
                hoverlabel_font_family="Averta",
                width=600,
                height=380,# Make the plot bigger
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_showscale=False,
                plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Unable to display data, missing the attributes. Make sure to custom the index on homepage.")

    def render_scatterplot_compare(self):
        data=self.data
        selected_country1=self.country1
        selected_country2=self.country2
        metric = self.metric

        if metric in data.columns:
            filtered_data1 = data[data[st.session_state.class_name]==selected_country1]
            filtered_data2 = data[data[st.session_state.class_name]==selected_country2]

            filtered_data1=filtered_data1[list(set([st.session_state.time_name,st.session_state.class_name,st.session_state.index_name,metric]))].dropna()
            filtered_data2=filtered_data2[list(set([st.session_state.time_name,st.session_state.class_name,st.session_state.index_name,metric]))].dropna()
            # draw
            select_fit(page="Cross-Sectopm")
            if selected_country1==selected_country2:
                st.write(filtered_data1.shape(0))
                if filtered_data1[st.session_state.index_name].empty:
                    st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
                else:
                    if filtered_data1.shape[0]>2:
                        params1, fitted_x,fitted_y,mse = fitting(filtered_data=filtered_data1, metric=metric,
                                                            method=st.session_state.method,
                                                            preprocess = st.session_state.preprocess)
                        fig1 = plot_fit(filtered_data1,fitted_x,fitted_y,metric,
                                        marker_color="#4682B4",line_color="#4682B4")
                        col1, col2,col3 =  st.columns([1,5,1])
                        with col2:  # 只在中间列显示图表
                            st.plotly_chart(fig1)
                            st.markdown(
                                f"""
                        <p><span style='font-size:25px;font-style: italic;color:#696969;''>The fitting result is:</span> </p>
                        """,
                        unsafe_allow_html=True)
                            st.markdown(
                                f"<span style='font-size:20px;font-style: italic; color:#4682B4;'>{params1}</span>",
                                unsafe_allow_html=True)
                    else:
                        st.error("Not enough data for fitting.")
            else:
                if filtered_data1[st.session_state.index_name].empty:
                    st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
                else:
                    if filtered_data1.shape[0]>2 and filtered_data2.shape[0]>2:
                        params1, fitted_x,fitted_y,mse = fitting(filtered_data=filtered_data1, metric=metric,
                                                                method=st.session_state.method,
                                                                preprocess = st.session_state.preprocess)
                        fig1 = plot_fit(filtered_data1,fitted_x,fitted_y,metric,
                                        marker_color="#4682B4",line_color="#4682B4")
                        params2, fitted_x,fitted_y,mse = fitting(filtered_data=filtered_data2, metric=metric,
                                                                method=st.session_state.method,
                                                                preprocess = st.session_state.preprocess)
                        fig2 = plot_fit(filtered_data2,fitted_x,fitted_y,metric,
                                        marker_color="#FF8C00",line_color="#FF8C00")
                        col1, col2 =  st.columns(2)
                        with col1:  # 只在中间列显示图表
                            st.plotly_chart(fig1)
                            st.markdown(
                                f"""
                        <p><span style='font-size:25px;font-style: italic;color:#696969;''>The fitting result is:</span> </p>
                        """,
                        unsafe_allow_html=True)
                            st.markdown(
                                f"<span style='font-size:20px;font-style: italic; color:#4682B4;'>{params1}</span>",
                                unsafe_allow_html=True)

                        with col2:
                            st.plotly_chart(fig2)
                            st.markdown(
                                f"""
                        <p><span style='font-size:25px;font-style: italic;color:#696969;''>The fitting result is:</span> </p>
                        """,
                        unsafe_allow_html=True)
                            st.markdown(
                                f"<span style='font-size:20px;font-style: italic; color:#FF8C00;'>{params2}</span>",
                                unsafe_allow_html=True)
                    else:
                        st.error("Not enough data for fitting.")
        else:
            st.error(f"Unable to display data, missing the attributes. Make sure to custom the index on homepage.")
