import streamlit as st

class SampleDefault():
    def __init__(self,data,initial=True):
        self.data=data
        self.initial=initial
    
    #储存sample数据默认值
    def default_value(self):
        # 根据数据计算初始权重
        default_session_state = {
            "dataset_default": self.data,  # 假设 data_default 是之前已经定义好的变量
            "data_state": "Sample",
            "time_name":"Year",
            "class_name":"Country",
            "index_components_default":['Nitrogen_oxide_Nox', 'Sulphur_dioxide_SO2', 'Carbon_monoxide_CO',
                    'Organic_carbon_OC', 'NMVOCs', 'Black_carbon_BC', 'Ammonia_NH3'],
            "index_name_default":"Air Pollution Index",
            "variables":["GDP", "Inflation", "CancerDeath", "Population", "AvgTemperature"],
            "countries_default": ['Australia', 'China', 'United States of America', 'United Kingdom',
                                'Japan', 'India', 'Canada', 'Germany'],
        }
        
        # 设置初始值
        if self.initial==True:      
            for key, value in default_session_state.items():
                if key not in st.session_state:
                    st.session_state[key] = value
        #恢复默认值
        else:
            for key, value in default_session_state.items():
                st.session_state[key] = value

    #sample display中设置初始数据
    def sample_display_default(self):
        default_session_state = {
            "dataset": st.session_state.dataset_default,  # 假设 data_default 是之前已经定义好的变量
            "data_state_chosen": "Sample",
            "index_components": st.session_state.index_components_default,
            "index_name":st.session_state.index_name_default,
            "selected_countries":st.session_state.countries_default,
        }
        
        #设置初始值
        if self.initial==True:      
            for key, value in default_session_state.items():
                if key not in st.session_state:
                    st.session_state[key] = value
        #恢复默认值
        else:
            for key, value in default_session_state.items():
                st.session_state[key] = value
