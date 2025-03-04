import pandas as pd

# 读取原始 CSV 文件
a1 = pd.read_csv('../data/processed/p_air2.csv')
a2 = pd.read_csv('../data/processed/ALL.csv')
merged_df = pd.merge(a2, a1, on=['Year', 'Country'],how="inner")
merged_df.to_csv('../data/ALL.csv', index=False)
print("处理完成，结果已保存为 ALL.csv")