import streamlit as st
import pandas as pd
import numpy as np
from components.UploadDoc import auto_read_file_to_dataframe,Display_FileUpload
from components.SampleInfo import SampleDefault
from components.FittingModel import preprocessing
from geotext import GeoText
from datetime import datetime
import random

class MySelect:
    def __init__(self):
        self.data = pd.DataFrame()  # 确保self.data是一个DataFrame对象
        self.update_data()  # 初始化数据

    def update_data(self):
        self.data = st.session_state.dataset.copy() if 'dataset' in st.session_state else pd.DataFrame() 

    def state_data(self):
        option = st.sidebar.radio(
                "Please Select One Attribute:",
                options=["Sample","Custom"]
            )
        option
        if option == "Sample":
            st.session_state.data_state = "Sample"
            st.session_state.dataset = st.session_state.dataset_default
            sample = SampleDefault(st.session_state.dataset_default,initial=False)
            sample.default_value()
            sample.sample_display_default()
            self.update_data()  # 确保数据是最新的
            st.write("Current Data State:", st.session_state.data_state)
            Display_FileUpload(st.session_state.dataset)
        if option == "Custom":
            st.session_state.data_state = "Custom"
            self.select_data()

    
    def select_data(self):
        if True:
            uploaded_file = st.file_uploader("Feel free to upload your file (.csv, .xls, .xlsx, .xlsm, .xlsb, .txt)~", 
                                accept_multiple_files=False, 
                                type=["csv", "xls", "xlsx", "txt",'xlsm','xlsb'])
            if uploaded_file:
                try:
                    #file_path = uploaded_file.getvalue().decode("utf-8")
                    df = auto_read_file_to_dataframe(uploaded_file)         
                    st.session_state.dataset = df
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                except Exception as e:
                    st.error(f"Failed to read file '{uploaded_file.name}': {e}")
        
        self.update_data()  # 确保数据是最新的
        st.write("Current Data State:", st.session_state.data_state)
        Display_FileUpload(st.session_state.dataset)
        
    def can_convert_to_type(self, value, target_types):
        """
        判断一个值是否可以转化为指定的类型之一。
        
        参数:
        value: 要检查的值。
        target_types: 一个包含类型的元组，例如 (datetime, float, int)。
        
        返回:
        一个元组，包含布尔值，指示值是否可以转化为每种类型。
        """
        conversion_results = []
        record="str"

        if isinstance(value,target_types):
            conversion_results=True
            record = type(value)
        else:
            for t in target_types:
                try:
                    # 尝试将值转换为目标类型
                    
                    if t == datetime:
                        datetime.strptime(value, format="%Y-%m")
                    else:
                        t(value)  # 其他类型直接转换
                    conversion_results.append(True)
                    if record == "str":
                        record=t
                    
                except (ValueError, TypeError):
                    conversion_results.append(False)
            conversion_results=any(conversion_results)
        
        return conversion_results,record
 

    def select_names(self):
        self.update_data()
        names = self.data.columns
 
        # Select time column and class column
        #Sample Data default "Year", "Country"
        if st.session_state.data_state=="Sample": 
            st.session_state.time_name = st.sidebar.selectbox(
            "Please Select Time Column:",
            options=names,index=names.get_loc('Year')
        )
            
            names = [name for name in names if name != st.session_state.time_name]
            if "Country" in names:
                st.session_state.class_name = st.sidebar.selectbox(
                "Please Select Class Column:",
                options=names,index=names.index('Country')
            )
            else:
                st.session_state.class_name = st.sidebar.selectbox(
                "Please Select Class Column:",
                options=names
            )
        else:
            st.session_state.time_name = st.sidebar.selectbox(
            "Please Select Time Column:",
            options=names
        )
            d,type_time=self.can_convert_to_type(st.session_state.dataset[st.session_state.time_name][0], (int, float,datetime))
            if d:            
                if type_time == datetime:
                    st.session_state.dataset[st.session_state.time_name] = pd.to_datetime(st.session_state.dataset[st.session_state.time_name], format="%Y-%m")
                else:
                    st.session_state.dataset[st.session_state.time_name] = pd.to_numeric(st.session_state.dataset[st.session_state.time_name])

            names = [name for name in names if name != st.session_state.time_name]
            st.session_state.class_name = st.sidebar.selectbox(
            "Please Select Class Column:",
            options=names
            )
            st.session_state.dataset[st.session_state.class_name]=st.session_state.dataset[st.session_state.class_name].astype(str)
        if st.session_state.dataset[st.session_state.class_name].dtype == np.int64:
            st.session_state.dataset[st.session_state.class_name] = st.session_state.dataset[st.session_state.class_name].astype(str)
 

        
    def select_index(self):
        self.update_data()
        names = self.data.columns  # 假设data.columns是有效的，并且包含了您想要的选项
        #去除class name 和 time name
        names = [name for name in names if (name != st.session_state.class_name) and (name != st.session_state.time_name)]
        
        if (st.session_state.data_state=="Sample") and (st.session_state.class_name=="Country") and (st.session_state.time_name == "Year"): 
            st.session_state.index_components = st.sidebar.multiselect(
                f"Please Select Index Components:",
                names,
                key="plotchart_multiselect",
                default=st.session_state.index_components_default
            )
            st.session_state.index_name = st.sidebar.text_input(
                "Please Define the Index:",
                value=st.session_state.index_name
            )
            
        else:
            st.session_state.index_components = st.sidebar.multiselect(
                f"Please Select Index Components:",
                names,
                key="plotchart_multiselect"
            )
            st.session_state.index_name = st.sidebar.text_input(
                "Please Define the Index:"
            )
        st.session_state.variables = [name for name in names if name not in st.session_state.index_components and 
                                      name != st.session_state.class_name and name != st.session_state.time_name]

    def calculate_initial_weights(self):
        """
        计算初始权重：可以根据污染物的标准差来计算。
        这个方法将返回一个根据标准差计算的权重列表。
        """
        # 计算每个污染物的标准差
        self.update_data()
        data = self.data
        cols = st.session_state.index_components
        std_devs = data[cols].std()
        total_std = std_devs.sum()
        
        # 计算每个污染物的权重，权重根据标准差的比例来确定
        weights = [std / total_std for std in std_devs]
        return weights

    def select_weight(self):
        self.update_data()
        # Selection==============
        st.sidebar.title(f"{st.session_state.index_name}")    # 设置侧边栏标题
        # Index Components
        data = self.data
        cols = st.session_state.index_components
        n = len(cols)

        # 根据数据计算初始权重
        initial_weights = self.calculate_initial_weights()
        #st.write(initial_weights)
        weights = []
        preprocesses = []

        # 权重选择 - 默认值为根据标准差计算的初始权重
        if "weights_raw" not in st.session_state:
            st.session_state.weights_raw = initial_weights
    
        if "slider_version" not in st.session_state:
            st.session_state["slider_version"] = 1

        # 定义重置函数
        def reset_sliders():
            st.session_state["slider_version"] = st.session_state["slider_version"] + random.randint(1, 100)

        for i in range(n):
            weight = st.sidebar.slider(f'Importance of {cols[i]}', min_value=0.0, max_value=1.0, step=0.01,
                                        value=float(initial_weights[i]) ,
                                        key = f"weight_{i}_{st.session_state.slider_version}") # 设置默认值为计算得出的权重
            weights.append(weight)
            st.session_state.weights_raw[i] = weight
            st.sidebar.button("Reset", on_click=reset_sliders,key=f"reset_weight_{i}")

            preprocess = st.sidebar.radio("Please Select a Data Preprocessing Method:",
                                          options=["none", "normalization"],key = f"fitting_preprocess_{i}")
            preprocesses.append(preprocess)
            data[f"{cols[i]}_preprocessed"] = preprocessing(data,preprocesses[i],cols[i])
        
        st.session_state.preprocess_index = preprocesses

        # 计算权重的总和
        total_weights = sum(weights)
        # 标准化权重，使得它们的和为1
        normalized_weights = [w / total_weights for w in weights]
        st.session_state.weights = normalized_weights

        # 计算空气污染指数
        # 构造新的列名列表
        new_cols = [f"{col}_preprocessed" for col in cols]
        data[st.session_state.index_name] = 100 * data[new_cols].apply(
                lambda row: sum(row[new_cols[i]] * normalized_weights[i] for i in range(n)), axis=1
            )
        data = data.drop(new_cols,axis=1)
        # 储存选择的指数
        st.session_state.dataset = data

    def select_class(self):
        self.update_data()
        countries = sorted(self.data[st.session_state.class_name].unique())
        country_decide = ', '.join([f'{country}' for country in countries])
        places = GeoText(country_decide)
          # 识别文本中的国家
        if len(places.countries)==0:
            st.warning(f"Class {st.session_state.class_name} can not be recognized as Country. Map display may fail.")
        st.session_state.selected_country = st.sidebar.selectbox(f"Please Select one {st.session_state.class_name}:", 
                                                                    ["Global"] + list(countries))
        return(f"{st.session_state.selected_country}")


        
    def select_class_compare(self):
        self.update_data()
        countries = self.data[st.session_state.class_name]
        countries = sorted(countries.unique())
        country_decide = ', '.join([f'{country}' for country in countries])
        places = GeoText(country_decide)
          # 识别文本中的国家
        if len(places.countries)==0:
            st.warning(f"Class {st.session_state.class_name} can not be recognized as Country. Map display may fail.")
        # get session_state
        st.session_state.country1 = st.sidebar.selectbox(f"Choose Left Side {st.session_state.class_name} (Blue)", 
                                                         countries,index=0)
        st.session_state.country2 = st.sidebar.selectbox(f"Choose Right Side {st.session_state.class_name} (Orange)", 
                                                         countries,index=1)
        
        data1=self.data[self.data[st.session_state.class_name]==st.session_state.country1]
        data2=self.data[self.data[st.session_state.class_name]==st.session_state.country2]
        
        time1 = data1[st.session_state.time_name]
        time2 = data2[st.session_state.time_name]
        min1, max1 = min(time1), max(time1)
        min2, max2 = min(time2), max(time2)
        min_value = max(min1,min2)
        max_value = min(max1,max2)
        if isinstance(min_value, pd.Timestamp):
            min_value = data1[st.session_state.time_name][0]
        else:
            min_value = min_value

        # 检查列中最大值的类型，如果它是Pandas Timestamp，则转换为datetime对象
        if isinstance(max_value, pd.Timestamp):
            min_value = data1[st.session_state.time_name][-1]
        else:
            max_value = max_value


        if isinstance(min_value,(int,float,datetime)) and isinstance(max_value,(int,float,datetime)):            
            st.session_state.year = st.sidebar.slider("Please Select one Time", min_value= min_value, 
                                                    max_value=max_value, value=min_value)
            selected_countries = list(set([st.session_state.country1,st.session_state.country2]))
            selected_countries = [st.session_state.year]+selected_countries
            spans = ', '.join([f'<span style="color: #800000;">{country}</span>' for country in selected_countries])

            return(spans)
        else:
            st.session_state.year = False
            st.warning(f"Time selection is not allowed. Make sure {st.session_state.time_name}  is a time name.")
         

    def select_classes(self):
        self.update_data()
        data = self.data
        # Get country
        countries = sorted(data[st.session_state.class_name].unique())
        country_decide = ', '.join([f'{country}' for country in countries])
        places = GeoText(country_decide)
          # 识别文本中的国家
        if len(places.countries)==0:
            st.warning(f"Class {st.session_state.class_name} can not be recognized as Country. Map display may fail.")
        
        def reset_sliders():
            st.session_state["slider_version"] = st.session_state["slider_version"] + random.randint(1, 100)

        # Multi-choice with session_state
        if len(places.countries)!=0:
            selected_countries = st.sidebar.multiselect(
                f"Please Select Multiple {st.session_state.class_name}:",
                countries,
                #default=st.session_state.selected_countries,
                key=f"slider_{st.session_state['slider_version']}"
            )
        else:
            selected_countries = st.sidebar.multiselect(
                f"Please Select Multiple {st.session_state.class_name}:",
                countries,
                key=f"slider_{st.session_state['slider_version']}"
            )
        st.session_state.selected_countries = selected_countries
        # Choose ALL/Cancel All/Default
        col1, col2,col3 = st.sidebar.columns(3)
        if col1.button("Choose ALL", key="plotchart_select_all",on_click=reset_sliders,):
            st.session_state.selected_countries = countries
        if col2.button("Cancel ALL", key="plotchart_deselect_all",on_click=reset_sliders,):
            st.session_state.selected_countries = []
        if st.session_state.class_name in ["Country","country"]:
            if col3.button("Default", key="plotchart_default",on_click=reset_sliders,):
                st.session_state.selected_countries = st.session_state.countries_default

        country_spans = ', '.join([f'<span style="color: #800000;">{country}</span>' for country in selected_countries])
        return(country_spans)
    
    # Attribute Selection
    def select_attribute(self,include=True):
        attributes = st.session_state.variables
        if include == True:
            index = st.session_state.index_name
            attributes = [index]+attributes
            map_option = st.sidebar.radio(
                "Please Select One Attribute:",
                options=attributes
            )
        if include == False:
            map_option = st.sidebar.radio(
                "Please Select one Attribute:",
                options=attributes
            )
        st.session_state.selected_attribute = map_option
        return(f"{st.session_state.selected_attribute}")
    
        # Attribute Selection
    def select_attributes(self,include=True):
        attributes = st.session_state.variables
        if include == True:
            index = st.session_state.index_name
            attributes = [index]+attributes
            map_option = st.sidebar.multiselect(
                "Please Select Multiple Attributes:",
                options=attributes,key="include_attribute",default=attributes
            )
        if include == False:
            map_option = st.sidebar.multiselect(
                "Please Select Multiple Attributes:",
                options=attributes,key="exclude_attribute",default=attributes
            )
        st.session_state.selected_attributes = map_option
        attribute_spans = ', '.join([f'<span style="color: #800000;">{i}</span>' for i in map_option])

        return(f"({attribute_spans})")               
        

    def select_time(self):
        self.update_data()
        data = self.data
        data = data.dropna() #去除缺失值以查看合理的时间范围
        if isinstance(min(data[st.session_state.time_name]), pd.Timestamp):
            min_value = data[st.session_state.time_name][0]
        else:
            min_value = min(data[st.session_state.time_name])

        # 检查列中最大值的类型，如果它是Pandas Timestamp，则转换为datetime对象
        if isinstance(max(data[st.session_state.time_name]), pd.Timestamp):
            max_value = data[st.session_state.time_name][-1]
        else:
            max_value = max(data[st.session_state.time_name])

        if isinstance(min_value,(int,float,datetime)) and isinstance(max_value,(int,float,datetime)):            
            selected_year = st.sidebar.slider('Please Select one Time:',                                           
                                              min_value=min_value, max_value=max_value)
            st.session_state.year = selected_year
            return(f"{st.session_state.year}")
        else:
            st.session_state.year = False
            st.warning(f"Time selection is not allowed. Make sure {st.session_state.time_name}  is a time name.")

    def select_time_range(self):
        self.update_data()
        data = self.data
        data = data.dropna() #去除缺失值以查看合理的时间范围
        # Get country
        if isinstance(min(data[st.session_state.time_name]), pd.Timestamp):
            min_value = data[st.session_state.time_name][0]
        else:
            min_value = min(data[st.session_state.time_name])

        # 检查列中最大值的类型，如果它是Pandas Timestamp，则转换为datetime对象
        if isinstance(max(data[st.session_state.time_name]), pd.Timestamp):
            max_value = data[st.session_state.time_name][1]
        else:
            max_value = max(data[st.session_state.time_name])

        if isinstance(min_value,(int,float,datetime)) and isinstance(max_value,(int,float,datetime)):            
            selected_range = st.sidebar.slider("Please Select Time Range:", min_value, max_value, (min_value, max_value))
            st.session_state.time_range = selected_range
            return(f"{st.session_state.time_range}")
        else:
            st.session_state.time_range = False
            st.warning(f"Time selection is not allowed. Make sure {st.session_state.time_name}  is a time name.")

    def components_select(self,one_class=False,classes=False,compare=False,
                          time=False,time_range=False,attribute=False,include_i=True,attributes=False,include_j=True):
        st.sidebar.title("Custom Components")
        c=[]
        if one_class:
            c_i=self.select_class()
            c.append(c_i)
        if classes:
            c_i=self.select_classes()
            c.append(c_i)
        if compare:
            c_i=self.select_class_compare()
            c.append(c_i)
        if time:
            c_i=self.select_time()
            c.append(c_i)
        if time_range:
            c_i=self.select_time_range()
            c.append(c_i)
        if attribute:
            c_i=self.select_attribute(include_i)
            c.append(c_i)
        if attributes:
            c_i=self.select_attributes(include_j)
            c.append(c_i)

        components =  ', '.join([f'<span style="color: #800000;">{i}</span>' for i in c])
        html_string = f"""
    <p style="font-size:25px;font-style: italic; color: #708090;">
        Sir/Mme, YOU have chosen <span style="color: #800000;">{components}</span>. Here is the information!
    </p>
    """
        st.markdown(html_string, unsafe_allow_html=True)

            # Weight display
        weight_spans = ', '.join([f'<span style="color: #0000CD;">{st.session_state.index_components[i]} * {st.session_state.weights[i]:.2f}</span>' 
                                  for i in range(len(st.session_state.index_components))])
        st.markdown(f"""<p>
                The chosen weight of {st.session_state.index_name} is: {weight_spans}
                </p>
                """,unsafe_allow_html=True)



