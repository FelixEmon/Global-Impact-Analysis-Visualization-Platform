import pandas as pd
###废案换数据集了###
# 读取三个CSV文件
a = pd.read_csv('../data/raw/ageabove65.csv')
b = pd.read_csv('../data/raw/agebelow14.csv')
c = pd.read_csv('../data/raw/age1465.csv')

# 确保列名一致，便于后续操作
a.columns = ['Country Name', 'Year', 'Population']
b.columns = ['Country Name', 'Year', 'Population']
c.columns = ['Country Name', 'Year', 'Population']

# 合并三个数据集
merged = pd.concat([a, b, c])

# 按 'Country Name' 和 'Year' 分组，计算 Count 的和
d = merged.groupby(['Country Name', 'Year'], as_index=False)['Population'].sum()

# 保存为 d.csv
d.to_csv('Allage.csv', index=False)

print("合并完成，结果已保存到 Allage.csv")
