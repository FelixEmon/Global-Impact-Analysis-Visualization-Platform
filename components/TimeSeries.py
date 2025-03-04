import altair as alt
import streamlit as st
import plotly.express as px

class TimeDisplay:
    def __init__(self,data,classes,time_range,metric):
        self.data=data
        self.classes=classes
        self.time_range=time_range
        self.metric=metric

    def display_country_map_t(self):
        data = self.data
        selected_country = self.classes
        time_range = self.time_range
        map_attribute = self.metric

        max_attribute = max(data[map_attribute])
        min_attribute = min(data[map_attribute])
        # Filter data for the selected country or global
        if time_range != False:
            data = data[data[st.session_state.time_name].between(time_range[0], time_range[1])]
        country_data = data[data[st.session_state.class_name].isin(selected_country)]
        
        # Ensure the selected attribute exists
        if len(country_data)>0:
            if st.session_state.time_name in country_data.columns and map_attribute in country_data.columns:
                # Plot the selected attribute trend on a map
                fig = px.choropleth(
                    country_data,
                    locations=st.session_state.class_name,
                    locationmode="country names",
                    color=map_attribute,
                    hover_name=st.session_state.class_name,
                    animation_frame=st.session_state.time_name,
                    projection="miller",
                    color_continuous_scale="PuBuGn",
                    range_color=[min_attribute, max_attribute]
                )
                # Make the plot bigger
                fig.update_layout(
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
                    width=800,
                    height=500,# Make the plot bigger
                    margin=dict(l=0, r=0, t=0, b=0),
                    coloraxis_showscale=False,
                    geo=dict(
                        showframe=False, 
                        lakecolor='#fff4b9'
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                col1, col2,col3 = st.columns([1,10, 1],gap='small')
                with col2:
                    st.plotly_chart(fig)
                
            else:
                st.warning(f"Unable to display {selected_country} data, missing the attributes: '{st.session_state.time_name}' or '{map_attribute}'.")

    def render_scatterplot(self):
        data = self.data
        selected_countries = self.classes
        time_range = self.time_range
        metric = self.metric

        if st.session_state.index_name in data.columns:
            if time_range != False:
                data = data[data[st.session_state.time_name].between(time_range[0], time_range[1])]
            filtered_data = data[data[st.session_state.class_name].isin(selected_countries)]

            filtered_data=filtered_data[[st.session_state.class_name,st.session_state.time_name,
                                        st.session_state.index_name,metric]].dropna()
            # draw
            fig = px.scatter(filtered_data, x=st.session_state.index_name, y=metric, 
                            color=st.session_state.class_name, 
                            hover_data=[st.session_state.class_name]
                            )
            fig.update_traces(marker=dict(size=12,opacity=0.5))  # 将点的大小设置为12，可以根据需要调整这个值
            # 设置背景为透明
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',coloraxis_showscale=False)
            st.plotly_chart(fig)
        else:
            st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")

    def render_plotchart(self):
        data = self.data
        selected_countries = self.classes
        time_range = self.time_range
        metric = self.metric
        if st.session_state.index_name in data.columns:
            if time_range != False:
                data = data[data[st.session_state.time_name].between(time_range[0], time_range[1])]
            filtered_data = data[data[st.session_state.class_name].isin(selected_countries)]
            # draw linechart

            if len(filtered_data)>0:
                max_value1 = filtered_data[st.session_state.index_name].max()
                min_value1 = filtered_data[st.session_state.index_name].min()
                max_value2 = filtered_data[metric].max()
                min_value2 = filtered_data[metric].min()
                chart = alt.Chart(filtered_data).mark_line().encode(
                    x=f"{st.session_state.time_name}:O",
                    y=alt.Y(st.session_state.index_name, scale=alt.Scale(domain=[min_value1, max_value1])),
                    color=alt.Color(f"{st.session_state.class_name}:N", legend=None),
                    tooltip=[st.session_state.class_name, st.session_state.time_name,st.session_state.index_name]
                ).properties(width=300, height=300, background='transparent').interactive()
                st.altair_chart(chart)

                chart = alt.Chart(filtered_data).mark_line().encode(
                    x=f"{st.session_state.time_name}:O",
                    y=alt.Y(metric, scale=alt.Scale(domain=[min_value2, max_value2])),
                    color=alt.Color(f"{st.session_state.class_name}:N", legend=None),
                    tooltip=[st.session_state.class_name, st.session_state.time_name, metric]
                ).properties(width=300, height=300, background='transparent').interactive()
                st.altair_chart(chart)
        else:
            st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")



