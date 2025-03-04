import pandas as pd

# 创建一个国家名称标准化的映射字典
country_mapping = {
    'America': 'United States of America',
    'United States': 'United States of America',
    'United States of America': 'United States of America',
    # 可以根据需要添加更多的映射
}

# 读取所有CSV文件，添加encoding='ISO-8859-1'来处理文件编码问题
files = ['data/processed/p_pop.csv', 'data/processed/p_air2.csv', 'data/processed/p_cancer.csv', 
         'data/processed/p_gdp.csv', 'data/processed/p_infla.csv','data/processed/p_temp.csv']
dataframes = []

# 读取每个CSV文件
for file in files:
    df = pd.read_csv(file, encoding='ISO-8859-1')  # 这里使用了ISO-8859-1编码来读取文件

    # 标准化 'Country' 列
    df['Country'] = df['Country'].replace(country_mapping)

    # 保留Year和Country，以及其他列
    dataframes.append(df)

# 找到所有文件中Year和Country的交集
common_year_country = dataframes[0][['Year', 'Country']]

for df in dataframes[1:]:
    common_year_country = common_year_country.merge(df[['Year', 'Country']], on=['Year', 'Country'], how='inner')

# 将 'United States of America' 添加到交集中，即使它不存在
# 修复: 展平所有年份到单个列表后取并集
us_years = sorted(year for df in dataframes for year in df['Year'].unique()))
us_df = pd.DataFrame({'Year': us_years, 'Country': 'United States of America'})

# 合并美国数据和交集数据
common_year_country = pd.concat([common_year_country, us_df]).drop_duplicates()

# 合并所有文件的所有数据（保留Year和Country列）
merged_df = common_year_country

for df in dataframes:
    merged_df = merged_df.merge(df, on=['Year', 'Country'], how='left')

# 保存最终结果
merged_df.to_csv('data/ALL.csv', index=False)

print("处理完成，结果已保存为 ALL.csv")
