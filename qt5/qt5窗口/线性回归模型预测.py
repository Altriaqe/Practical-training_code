import pandas as pd
import joblib 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 读取数据
df = pd.read_csv(
    r"qt5\qt5窗口\Admission_Predict_CGPA.csv"
)

df = df.iloc[:,:-1]

# 划分数据
X = df.iloc[:, 1:7].values  # 特征
# 目标
Y = df.iloc[:, 0].values

 # 训练模型
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
model = LinearRegression() # 线性回归模型
model.fit(x_train, y_train) # 训练模型

features = ["GRE", "TOEFL", "大学评级", "SOP", "LOR", "CGPA"]
importances = model.coef_  # 获取特征重要性

for feature, importance in zip(features, importances):
    print(f"{feature}: {importance}")

joblib.dump(model, "cgpa_lr_model.pkl")  # 保存模型

print("模型训练完成并保存为 cgpa_lr_model.pkl")