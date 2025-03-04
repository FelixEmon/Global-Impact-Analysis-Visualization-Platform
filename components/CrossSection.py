import streamlit as st
import plotly.express as px
import altair as alt
from components.FittingModel import select_fit, fitting,plot_fit

class GlobalDisplay:
    def __init__(self,data,year,metric):
        self.data=data
        self.year=year
        self.metric=metric

    def display_country_map(self):
        data=self.data
        year=self.year
        map_attribute=self.metric

        country_data=data
        if map_attribute in country_data.columns:
            max_attribute = max(country_data[map_attribute])
            min_attribute = min(country_data[map_attribute])
            country_data = data[data[st.session_state.time_name] == year]
            st.subheader(f"Heatmap for {map_attribute}")
            # Plot the selected attribute trend on a map
            fig = px.choropleth(
                country_data,
                locations=st.session_state.class_name,
                locationmode="country names",
                color=map_attribute,
                hover_name=st.session_state.class_name,
                #animation_frame="Year",
                title=f"{map_attribute} Map in {year}",
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
            st.warning(f"Unable to display data, missing the attributes: '{st.session_state.time_name}' or '{map_attribute}'.")

    def render_barchart(self):
        data=self.data
        year=self.year
        metric=self.metric
        filtered_data = data[data[st.session_state.time_name] == year]
        if metric in filtered_data.columns:
            top_25 = filtered_data.nlargest(10, metric)
            bottom_25 = filtered_data.nsmallest(10, metric)

            # draw
            col1, col2 = st.columns([1, 1],gap='small')
            with col1:
                st.subheader(f"Top 10 {st.session_state.class_name}")
                chart = alt.Chart(top_25).mark_bar(color = "#4682B4").encode(
                    x=alt.X(metric, title=metric),
                    y=alt.Y(st.session_state.class_name, sort="-x", title=st.session_state.class_name),
                    tooltip=[st.session_state.class_name, metric]
                ).properties(width=400, height=300, background='transparent').interactive()

                st.altair_chart(chart)
            with col2:
                st.subheader(f"Bottom 10 {st.session_state.class_name}")
                chart = alt.Chart(bottom_25).mark_bar(color = "#4682B4").encode(
                    x=alt.X(metric, title=metric),
                    y=alt.Y(st.session_state.class_name, sort="x", title=st.session_state.class_name),
                    tooltip=[st.session_state.class_name, metric]
                ).properties(width=400, height=300, background='transparent').interactive()

                st.altair_chart(chart)
        else:
            st.warning(f"Unable to display data, missing the attributes: '{st.session_state.time_name}' or '{metric}'.")


    def display_scatter_country(self):
        data=self.data
        year=self.year
        metric=self.metric
        if st.session_state.index_name in data.columns:
            if data[st.session_state.index_name].empty:
                st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
            else:
                if year!= False:
                    data = data[data[st.session_state.time_name]==year]
                filtered_data=data[list(set([st.session_state.class_name,st.session_state.index_name,metric]))].dropna()
                select_fit(page="Cross-Sectopm")

                if filtered_data.shape[0]>2:
                    params, fitted_x,fitted_y,mse = fitting(filtered_data=filtered_data, metric=metric,
                                                            method=st.session_state.method,
                                                            preprocess = st.session_state.preprocess)
                    fig = plot_fit(filtered_data,fitted_x,fitted_y,metric)
                    col1, col2 =  st.columns([3,2],gap='small')
                    with col1:  # 只在中间列显示图表
                        st.plotly_chart(fig)
                    with col2:
                        st.markdown(
                            f"""
                    <p><span style='font-size:25px;font-style: italic;color:#696969;''>The fitting result is:</span> </p>
                    """,
                    unsafe_allow_html=True)
                        st.markdown(
                            f"<span style='font-size:20px;font-style: italic; color:#0000CD;'>{params}</span>",
                            unsafe_allow_html=True)
                        st.markdown(
                            f"""
                            <p><span style='font-size:25px;font-style: italic;color:#696969;''>The Loss Function (MSE) is: </span> </p>
                            """,
                            unsafe_allow_html=True)
                        st.markdown(
                            f"<p><span style='font-size:23px;font-style: italic; color:#0000CD;'> MSE = {mse:.2f}</span> </p>",
                            unsafe_allow_html=True)
                        st.markdown(
                            f"""
                            <p><span style='font-size:25px;font-style: italic;color:#696969;''>The Preprocess Method is: </span> </p>
                            """,
                            unsafe_allow_html=True)
                        st.markdown(
                            f"<p><span style='font-size:23px;font-style: italic; color:#0000CD;'> {st.session_state.preprocess}</span> </p>",
                            unsafe_allow_html=True)   
                else:
                    st.error("Not enough data for fitting.")
        else:
            st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")


                
        

