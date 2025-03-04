import pandas as pd

# 读取原始 CSV 文件
a = pd.read_csv('../data/raw/Cancer Deaths by Country and Type Dataset.csv')

# 确保列名一致，选取非癌症相关的列作为 ID 列
id_columns = ['Country', 'Code', 'Year']
cancer_columns = [col for col in a.columns if col not in id_columns]

# 计算所有癌症相关列的总和，作为每年的总死亡数
a['CancerDeath'] = a[cancer_columns].sum(axis=1)

# 选取需要的列生成新表
p_cancer = a[['Country', 'Year', 'CancerDeath']]

# 保存结果为 p_cancer.csv
p_cancer.to_csv('p_cancer.csv', index=False)

print("处理完成，结果已保存为 p_cancer.csv")
