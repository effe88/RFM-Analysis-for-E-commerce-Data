# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 17:16:25 2024

@author: efeme
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
# Set display options to show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', None)

# Load the dataset (Carefull about the name of your file)
df = pd.read_csv(r'C:/Users/efeme/Downloads/archive (11)/e_com.csv', encoding='ISO-8859-1')

# Check the first 5 rows to ensure data is loaded correctly
print(df.head())

# Data cleaning and transformation
df = df.dropna(subset=['Description'])  # Drop rows with missing Description values
df['CustomerID'] = df['CustomerID'].fillna('Unknown')  # Fill missing CustomerID with 'Unknown'
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])  # Convert InvoiceDate to datetime
df['CustomerID'] = df['CustomerID'].astype('category')  # Convert CustomerID to categorical type

# Check for missing values after cleaning
print("Missing values after cleaning:")
print(df.isnull().sum())

# Remove negative Quantity and UnitPrice values
df = df[df['Quantity'] > 0]
df = df[df['UnitPrice'] > 0]

# Check descriptive statistics after filtering out negative values
print("Descriptive statistics after filtering:")
print(df.describe())

# Create new columns
df['TotalSales'] = df['Quantity'] * df['UnitPrice']  # Total sales
df['Year'] = df['InvoiceDate'].dt.year  # Extract year from InvoiceDate
df['Month'] = df['InvoiceDate'].dt.month  # Extract month as a number from InvoiceDate
df['MonthName'] = df['InvoiceDate'].dt.strftime('%B')  # Extract month as name from InvoiceDate

# Set month order for proper display in graphs
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
df['MonthName'] = pd.Categorical(df['MonthName'], categories=month_order, ordered=True)

# Check the first few rows after transformations
print("Data after transformations:")
print(df.head())

# RFM analysis (Recency, Frequency, Monetary)
current_date = df['InvoiceDate'].max()
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (current_date - x.max()).days,  # Recency: days since last purchase
    'InvoiceNo': 'count',  # Frequency: number of purchases
    'TotalSales': 'sum'  # Monetary: total spending
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

# Check RFM summary statistics
print("RFM summary statistics:")
print(rfm.describe())

# Score RFM using quartiles
rfm['R_Quartile'] = pd.qcut(rfm['Recency'], 5, ['5', '4', '3', '2', '1'])
rfm['F_Quartile'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, ['1', '2', '3', '4', '5'])
rfm['M_Quartile'] = pd.qcut(rfm['Monetary'], 5, ['1', '2', '3', '4', '5'])
rfm['RFM_Score'] = rfm['R_Quartile'].astype(str) + rfm['F_Quartile'].astype(str) + rfm['M_Quartile'].astype(str)

# Check the first few rows of RFM analysis
print("RFM analysis with scores:")
print(rfm.head())

# Plot total yearly sales
df.groupby('Year')['TotalSales'].sum().plot(kind='bar')
plt.title('Total Sales by Year')
plt.ylabel('Total Sales')
plt.xlabel('Year')
plt.show()

# Plot monthly sales trends
monthly_sales = df.groupby(['Year', 'MonthName'])['TotalSales'].sum()
monthly_sales = monthly_sales[monthly_sales > 0]

fig, ax = plt.subplots()
monthly_sales.plot(kind='line', ax=ax)
plt.title('Monthly Sales Trends')
plt.xlabel('Months of 2021')
plt.ylabel('Total Sales')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{int(x/1e3)}K'))  # Format y-axis in thousands
plt.xticks(rotation=45)
plt.show()

# Most sold products
top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
top_products.plot(kind='bar')
plt.title('Top 10 Most Sold Products')
plt.xlabel('Product')
plt.ylabel('Quantity Sold')
plt.show()

# Total sales by country (top 10 countries)
country_sales = df.groupby('Country')['TotalSales'].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots()
country_sales.plot(kind='bar', ax=ax)
plt.title('Top 10 Countries by Sales')
plt.xlabel('Country')
plt.ylabel('Total Sales')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{int(x/1e6)}M'))  # Format y-axis in millions
plt.show()
