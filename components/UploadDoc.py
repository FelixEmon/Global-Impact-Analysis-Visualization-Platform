import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def auto_read_file_to_dataframe(uploaded_file):
    """
    自动识别文件类型并读取文件到Pandas DataFrame。

    参数:
    uploaded_file: UploadedFile, 上传的文件对象。

    返回:
    DataFrame, 读取的文件内容。
    """
    # 确定文件类型
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension in ['.csv', '.txt']:
        return pd.read_csv(uploaded_file)
    elif file_extension in ['.xls', '.xlsx']:
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"不支持的文件类型: {file_extension}")

def Display_FileUpload(df):
        st.write("### Preview of Uploaded Data")
        st.dataframe(df)

        # Display basic statistics
        st.write("### Basic Statistics")
        numeric_cols = df.select_dtypes(include='number')
        if not numeric_cols.empty:
            # Compute basic statistics
            summary_stats = numeric_cols.describe().T
            summary_stats['variance'] = numeric_cols.var()

            st.write(summary_stats)

            # Distribution Bar Chart
            st.write("### Attribute Distribution Visualization")
            attribute = st.selectbox(
                "Select an attribute to visualize its distribution:",
                numeric_cols.columns,
            )

            # Bar Chart for Distribution
            fig = px.histogram(
                df, x=attribute, title=f"Distribution of {attribute}", nbins=30
            )
            fig.update_layout(xaxis_title=attribute, yaxis_title="Count" ,
                                plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
                                paper_bgcolor='rgba(0,0,0,0)',)
            st.plotly_chart(fig)

            # Dual-Axis Chart for Mean and Variance
            st.write("### Dual-Axis Chart of Mean and Variance")
            mean_variance_chart_data = pd.DataFrame({
                "Attribute": numeric_cols.columns,
                "Mean": numeric_cols.mean(),
                "Variance": numeric_cols.var()
            }).reset_index(drop=True)

            fig_dual = go.Figure()

            # Add Mean as a Bar
            fig_dual.add_trace(go.Bar(
                x=mean_variance_chart_data["Attribute"],
                y=mean_variance_chart_data["Mean"],
                name="Mean",
                marker_color="blue",
                yaxis="y1"
            ))

            # Add Variance as a Line
            fig_dual.add_trace(go.Scatter(
                x=mean_variance_chart_data["Attribute"],
                y=mean_variance_chart_data["Variance"],
                name="Variance",
                mode="lines+markers",
                yaxis="y2"
            ))

            fig_dual.update_layout(
                title="Mean and Variance of Numeric Attributes",
                xaxis_title="Attribute",
                yaxis=dict(title="Mean", titlefont=dict(color="blue"), tickfont=dict(color="blue")),
                yaxis2=dict(
                    title="Variance",
                    titlefont=dict(color="red"),
                    tickfont=dict(color="red"),
                    overlaying="y",
                    side="right"
                ),
                legend=dict(x=0.1, y=1.1),
                plot_bgcolor='rgba(0,0,0,0)',  # 设置图表背景为透明
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_dual)
            ############################################
            #download button
            st.write("### Download your report here~")
            if st.download_button(
                label="Download your as .csv file",
                data=summary_stats.to_csv(index=True, header=True).encode('utf-8'),
                file_name='data summary.csv',
                help='click to download',
                mime='text/csv'
            ):
                st.write("## Download Successfully~")
                st.balloons()
            else:
                pass
        else:
            st.warning("No numeric columns found in the uploaded dataset for visualization.")
    
