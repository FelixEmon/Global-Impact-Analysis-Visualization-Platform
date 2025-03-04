import pandas as pd
import chardet

# 检测文件编码
with open('../data/raw/Global Dataset of Inflation.CSV', 'rb') as file:
    result = chardet.detect(file.read())
    encoding = result['encoding']

# 使用检测到的编码读取文件
data = pd.read_csv('../data/raw/Global Dataset of Inflation.CSV', encoding=encoding)

# 找到年份列（假设年份列都是从1970到2022的数字）
year_columns = [col for col in data.columns if col.isdigit()]

# 将年份列从宽表变成长表
data_long = data.melt(
    id_vars=["Country", "Series Name"],  # 保留非年份列
    value_vars=year_columns,            # 只转换年份列
    var_name="Year",
    value_name="Inflation"
)

# 确保年份是整数，Inflation是数值
data_long["Year"] = data_long["Year"].astype(int)
data_long["Inflation"] = pd.to_numeric(data_long["Inflation"], errors="coerce")

# 按国家和年份计算非空值的平均通胀率
result = (
    data_long
    .dropna(subset=["Inflation"])
    .groupby(["Country", "Year"], as_index=False)["Inflation"]
    .mean()
)

# 保存为新文件
result.to_csv("p_infla.csv", index=False)

print("文件已成功生成为 p_infla.csv")
