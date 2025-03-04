import pandas as pd

# 读取原始文件
data = pd.read_csv("../data/raw/gdp.csv")

# 提取年份列（假设年份列都是从1960到2020的数字）
year_columns = [col for col in data.columns if col.isdigit()]

# 将年份列从宽表变成长表
data_long = data.melt(
    id_vars=["Country Name"],  # 保留 Country Name 列
    value_vars=year_columns,  # 只转换年份列
    var_name="Year",          # 新的列名为 Year
    value_name="GDP"          # 新的值列名为 GDP
)

# 确保年份是整数，GDP是数值
data_long["Year"] = data_long["Year"].astype(int)
data_long["GDP"] = pd.to_numeric(data_long["GDP"], errors="coerce")

# 重命名列名为要求格式
data_long.rename(columns={"Country Name": "Country"}, inplace=True)

# 保存为新文件
data_long.to_csv("p_gdp.csv", index=False)

print("文件已成功生成为 p_gdp.csv")
