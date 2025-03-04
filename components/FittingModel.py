import streamlit as st
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
from scipy.stats import boxcox
from sklearn.preprocessing import StandardScaler
from scipy.interpolate import CubicSpline
import plotly.express as px
import plotly.graph_objects as go

def select_fit(page):
       # 绘制拟合曲线
    if "method" not in st.session_state:
        st.session_state.method =  "linear"
    method = st.sidebar.radio(
        "Please Select a Fitting Function:",
        options=[ "linear", "polynomial","exponential","logarithmic", 
                 "power law", "gaussian","lorentzian","cubic spline"],
                 key = f"fitting_method_{page}")
    st.session_state.method = method
    if "preprocess" not in st.session_state:
        st.session_state.preprocess =  "none"
    preprocess = st.sidebar.radio(
        "Please Select a Data Preprocessing Method:",
        options=["none", "log","box-cox","normalization"],
                 key = f"fitting_preprocess_{page}")
    st.session_state.preprocess = preprocess
    st.subheader(f"The Fitting Function is {method}:")

def preprocessing(filtered_data, preprocess, metric):
    column = filtered_data[metric]
    if preprocess=="none":
        column=column
    elif preprocess == "log":
        column = np.log(column)
    elif preprocess == "box-cox":
        column, lambda_1 = boxcox(column)
    elif preprocess == "normalization":
        scaler = StandardScaler()
        column = scaler.fit_transform(filtered_data[[metric]])
    return(column)

def fitting(filtered_data,metric,method,preprocess):    
    # 定义函数模型  
    def linear_fit(x, a, b): #简单线性拟合
        return a * x + b
    
    def polynomial_fit(x, a, b, c): #多项式拟合
        return a * x**2 + b * x + c
    
    def exponential_fit(x, a, b): #指数拟合
        return a * np.exp(b * x)
    
    def logarithmic_fit(x, a, b): #对数拟合
        return a + b * np.log(x)
    
    def power_law_fit(x, a, b): #幂律拟合
        return a * x ** b
    
    def gaussian_fit(x, a, b, c): #高斯拟合 
        return a * np.exp(-((x - b) ** 2) / (2 * c ** 2))
    
    def lorentzian_fit(x, a, b, c): #洛伦兹拟合
        return a / (1 + ((x - b) / c) ** 2)

    # 调用curve_fit并传入优化选项
    fitting_opts = {'maxfev': 800,  # 设置最大迭代次数为1000次
                    }
    def func(filtered_data=filtered_data,method=method):
        fitted_x = np.linspace(min(filtered_data[st.session_state.index_name]), 
                               max(filtered_data[st.session_state.index_name]), 100)
        y = filtered_data[metric]
        if method == "linear":
            params, covariance = curve_fit(linear_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1], **fitting_opts)
            fitted_y = linear_fit(fitted_x, *params)
            predict_y = linear_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$(p1) \cdot x + (p2)$$"""
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            model=formula
        elif method == "polynomial":
            params, covariance = curve_fit(polynomial_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1,1], **fitting_opts)
            fitted_y = polynomial_fit(fitted_x, *params)
            predict_y = polynomial_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$(p1) \cdot x^2 + (p2) \cdot x + (p3)$$"""
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            formula = formula.replace("p3", f"{params[2]:.2f}")
            model=formula
        elif method == "exponential":
            params, covariance = curve_fit(exponential_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1], **fitting_opts)
            fitted_y = exponential_fit(fitted_x, *params)
            predict_y = exponential_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$p1 \cdot \exp^{p2 \cdot x}$$"""
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            model=formula
        elif method == "logarithmic":
            params, covariance = curve_fit(logarithmic_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1], **fitting_opts)
            fitted_y = logarithmic_fit(fitted_x, *params)
            predict_y = logarithmic_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$(p1) + (p2) \cdot \log(x)$$"""
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            model=formula
        elif method == "power law":
            params, covariance = curve_fit(power_law_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1], **fitting_opts)
            fitted_y = power_law_fit(fitted_x, *params)
            predict_y = power_law_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$p1 \cdot x^{p2}$$"""
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            model=formula
        elif method == "gaussian":
            params, covariance = curve_fit(gaussian_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[1,1,1], **fitting_opts)
            fitted_y = gaussian_fit(fitted_x, *params)
            predict_y = gaussian_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$(p1) \cdot \exp\\left(-\\frac{(x - (p2))^2}{2 \cdot (p3)^2}\\right)$$"""
            # 替换公式中的参数为实际值
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            formula = formula.replace("p3", f"{params[2]:.2f}")
            model=formula
        elif method == "lorentzian":
            params, covariance = curve_fit(lorentzian_fit,filtered_data[st.session_state.index_name], 
                                   filtered_data[metric], p0=[10,1,1], **fitting_opts)
            fitted_y = lorentzian_fit(fitted_x, *params)
            predict_y = lorentzian_fit(filtered_data[st.session_state.index_name], *params)
            formula = """$$\\frac{ p1}{{1 + \\left(\\frac{{x - p2}}{ p3}\\right)^2}}$$"""
            # 替换公式中的参数为实际值
            formula = formula.replace("p1", f"{params[0]:.2f}")
            formula = formula.replace("p2", f"{params[1]:.2f}")
            formula = formula.replace("p3", f"{params[2]:.2f}")
            model=formula
        elif method == "cubic spline":
            data=filtered_data.sort_values(by = st.session_state.index_name, ascending=True)
            y = data[metric]
            cubic_spline = CubicSpline(data[st.session_state.index_name], filtered_data[metric],
                                        bc_type='natural')
            # coeffs = cubic_spline.c
            # for i in range(len(filtered_data["Air Pollution Index"]) - 1):
            #     st.write(f"[{filtered_data["Air Pollution Index"][i]}, {filtered_data["Air Pollution Index"][i+1]}] have function:")
            #     st.write(f"S(x) = {coeffs[3]:.4f} + {coeffs[2]:.4f}(x - {filtered_data["Air Pollution Index"][i]:.4f}) +
            #            {coeffs[1]:.4f}(x - {filtered_data["Air Pollution Index"][i]:.4f})^2 + 
            #            {coeffs[0]:.4f}(x - {filtered_data["Air Pollution Index"][i]:.4f})^3")
            fitted_y = cubic_spline(fitted_x)
            predict_y = cubic_spline(filtered_data[st.session_state.index_name])
            model  = "Sorry, too complicated."
        
        squared_errors = (y - predict_y) ** 2# 计算均方误差
        mse = np.mean(squared_errors)
        return [model,fitted_x,fitted_y,mse]
    

    if filtered_data[st.session_state.index_name].empty:
        st.error(f"{st.session_state.index_name} has not been declared. Make sure to custom the index on homepage.")
    else:
        filtered_data[metric]=preprocessing(filtered_data=filtered_data, preprocess=preprocess,metric=metric)
        return (func(filtered_data=filtered_data,method=method))

def plot_fit(filtered_data,fitted_x,fitted_y,metric,height=380,width=1200,
             marker_color="#FF8C00",line_color="#D2691E"):
    x_name = st.session_state.index_name
    fit_df = pd.DataFrame({
        x_name: fitted_x,
        metric: fitted_y
    })
    max_x=max(max(filtered_data[x_name]),max(fitted_x))
    min_x=min(min(filtered_data[x_name]),min(fitted_x))
    max_y=max(max(filtered_data[metric]),max(fitted_y))
    min_y=min(min(filtered_data[metric]),min(fitted_y))
    range_x=max_x-min_x
    range_y=max_y-min_y

    fig = px.scatter(filtered_data, x=x_name, y=metric, 
                     hover_data=[st.session_state.class_name],
                     range_x=[min_x-range_x/10,max_x+range_x/10],
                     range_y=[min_y-range_y/10,max_y+range_y/10]
                    )
    fig.update_traces(marker=dict(size=20,opacity=0.5),marker_color=marker_color)  # 将点的大小设置为12，可以根据需要调整这个值
    # 添加拟合曲线到散点图
    fig.add_traces(go.Scatter(x=fit_df[x_name], 
                              y=fit_df[metric], 
                              mode='lines', line=dict(color=line_color, width=2),
                                                      showlegend=False))
    # 设置背景为透明
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',coloraxis_showscale=False ,       
        height=height, 
        width=width, margin=dict(l=0, r=0, t=0, b=0),)
    return (fig)
