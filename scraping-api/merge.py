import pandas as pd

df1 = pd.read_csv("result/res1.csv")
df1 = df1.drop(['num','symbol'],axis=1)
df1['cik'] = df1['cik'].astype(str)

df2 = pd.read_csv("result/res2.csv")
df2 = df2.drop(['num'],axis=1)
df2['cik'] = df2['cik'].astype(str)

df3 = pd.read_csv("result/manual.csv")
df3 = df3.drop(['num'],axis=1)
df3['cik'] = df3['cik'].astype(str)


res = pd.concat([df1,df2,df3],ignore_index=True)
res.sort_values('name', ascending=True)
res['cik'] = res['cik'].astype(str)
print(res.shape)
res.to_csv('result/res.csv')
