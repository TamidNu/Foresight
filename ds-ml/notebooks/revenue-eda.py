import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Hotel Data.csv')
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S')
df_2023 = df[df['Date'].dt.year == 2023]

plt.figure(figsize=(15, 6))
plt.plot(df_2023['Date'], df_2023['TotalRevenue'])
plt.title('2023 Daily Revenue')
plt.xlabel('Date')
plt.ylabel('Revenue ($)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()