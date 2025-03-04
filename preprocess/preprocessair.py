import pandas as pd

# 读取原始 CSV 文件
a = pd.read_csv('../data/raw/air_pollution.csv')

# 确保列名一致
a.columns = ['Nitrogen_oxide_Nox', 'Sulphur_dioxide_SO2', 'Carbon_monoxide_CO',
              'Organic_carbon_OC', 'NMVOCs', 'Black_carbon_BC', 'Ammonia_NH3',
              'Country', 'Year']

# 提取污染物列（除了 'Entity' 和 'Year' 列）
pollutants = ['Nitrogen_oxide_Nox', 'Sulphur_dioxide_SO2', 'Carbon_monoxide_CO',
              'Organic_carbon_OC', 'NMVOCs', 'Black_carbon_BC', 'Ammonia_NH3']

# 计算每个污染物的最大值（用于标准化）
max_values = a[pollutants].max()

# 标准化污染物（按最大值归一化）
a[pollutants] = a[pollutants].div(max_values)
a2=a.loc[(a['Year']<=2016) & (a['Year']>=1995),]

# # 权重设置：根据每种污染物的重要性给定权重（权重值可以根据需要调整）
# weights = {
#     'Nitrogen_oxide_Nox': 0.3,
#     'Sulphur_dioxide_SO2': 0.2,
#     'Carbon_monoxide_CO': 0.1,
#     'Organic_carbon_OC': 0.1,
#     'NMVOCs': 0.1,
#     'Black_carbon_BC': 0.1,
#     'Ammonia_NH3': 0.1
# }

# 计算污染指数：每个污染物标准化值与权重的乘积求和
# a['Air Pollution Index'] = 100*a_normalized.apply(lambda row: sum(row[pollutants[i]] * weights[pollutants[i]]
#                                                             for i in range(len(pollutants))), axis=1)

# # 生成新数据框：包含 Entity（Country）、Year 和污染指数
# p_air = a[['Entity', 'Year', 'Air Pollution Index']]

# 保存为 p_air.csv
a2.to_csv('../data/processed/p_air2.csv', index=False)

print("处理完成，结果已保存为 p_air2.csv")
