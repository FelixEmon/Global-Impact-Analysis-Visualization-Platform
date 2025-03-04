import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 读取原始 CSV 文件
a = pd.read_csv('../data/raw/city_temperature.csv')

# 确保列名一致
a.columns = ['Region', 'Country', 'State', 'City', 'Month', 'Day', 'Year', 'AvgTemperature']

# 替换异常值 -99 为 np.nan
a['AvgTemperature'] = a['AvgTemperature'].replace(-99, np.nan)
a = a[(a['Year'] != 200) & (a['Year'] != 201)]

# 检查缺失值分布
# 按国家和年份统计缺失率
missing_summary = a.groupby(['Country', 'Year'])['AvgTemperature'].apply(lambda x: x.isna().mean()).reset_index()
missing_summary.columns = ['Country', 'Year', 'MissingRate']

# 可视化缺失值分布
plt.figure(figsize=(15, 6))
sns.heatmap(a.pivot_table(index='Country', columns='Year', values='AvgTemperature', aggfunc='mean').isna(), cbar=False)
plt.title("Missing Value Heatmap by Country and Year")
plt.xlabel("Year")
plt.ylabel("Country")
plt.show()

# 填充缺失值：按国家和年份进行线性插值
a['AvgTemperature'] = (
    a.groupby('Country', group_keys=False)['AvgTemperature']
    .apply(lambda x: x.interpolate(method='linear'))
    .reset_index(drop=True)
)

# 将温度从华氏度转换为摄氏度 (C = (F - 32) * 5/9)
a['AvgTemperature'] = (a['AvgTemperature'] - 32) * 5 / 9

# 按 Country 和 Year 分组，计算每年平均温度
p_temp = (
    a.groupby(['Country', 'Year'], as_index=False)
    .agg({'AvgTemperature': 'mean'})  # 计算每年温度的平均值
)

# 保存结果为 p_temp.csv
p_temp.to_csv('../data/processed/p_temp.csv', index=False)

print("处理完成，结果已保存为 p_temp.csv")
