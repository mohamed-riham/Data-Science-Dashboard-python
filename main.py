import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from abc import ABC, abstractmethod
from typing import Type
from collections import Counter
from itertools import combinations
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit App Styling
st.set_page_config(page_title="Supermarket Sales Dashboard", page_icon="📊", layout="wide")
st.markdown("""
    <style>
    /* Importing Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    /* Global Styles */
    html, body, [class*="st-"] {
    
        
        color: #ffffff;
    }

    /* Smooth Scroll */
    html {
        scroll-behavior: smooth;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(30, 30, 45, 0.85);
        color: white;
    }

    /* Sidebar Button */
    .sidebar .stButton>button {
        background-color: #1f8ef1;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
    }

    /* Title Styling */
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #00d4ff;
        text-shadow: 0px 4px 8px rgba(0, 212, 255, 0.6);
    }

    /* Section Headers */
    .stSubheader {
        color: #00d4ff;
        font-weight: bold;
        font-size: 24px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1f8ef1;
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
    }

    /* DataFrame/Table */
    .stDataFrame {
        background: rgba(50, 50, 60, 0.6);
        border-radius: 10px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
        color: white;
    }

    /* Plot Background */
    .stPlotlyChart {
        background: rgba(30, 30, 45, 0.85);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
    }

    /* Footer */
    footer {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)




# Data Ingestion Module (Factory Pattern)
class DataIngestionModule:
    @staticmethod
    def load_data(file):
        try:
            df = pd.read_csv(file)
            logging.info("Data successfully ingested.")
            return df
        except Exception as e:
            logging.error(f"Data ingestion failed: {str(e)}")
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()


# Data Processing Module
class DataProcessingModule:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def process_data(self):
        try:
            self.df["Date"] = pd.to_datetime(self.df["Date"], format='%m/%d/%Y', errors='coerce')
            self.df.drop_duplicates(inplace=True)
            self.df.dropna(inplace=True)
            self.df["TotalPrice"] = self.df["Quantity"] * self.df["PriceperUnit"]
            logging.info("Data processed successfully.")
            return self.df
        except Exception as e:
            logging.error(f"Data processing error: {str(e)}")
            st.error(f"Data processing error: {str(e)}")
            return pd.DataFrame()


# Singleton Pattern for Data Storage Module
class DataStorageModule:
    _instance = None

    def __new__(cls, df: pd.DataFrame):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.df = df
        return cls._instance


# Observer Pattern for Data Analysis
class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass


class DataAnalysisModule(Observer):
    def __init__(self, df):
        self.df = df

    def update(self, df):
        self.df = df

    def analyze(self):
        try:
            return {
                "best_selling_products": self.df.groupby("ProductName")["Quantity"].sum().sort_values(
                    ascending=False).head(10),
                "monthly_sales": self.df.groupby(self.df["Date"].dt.to_period("M"))["TotalPrice"].sum(),
                "regional_sales": self.df.groupby("Region")["TotalPrice"].sum().sort_values(ascending=False),
                "sales_by_day": self.df.groupby(self.df["Date"].dt.day_name())["TotalPrice"].sum().sort_values(
                    ascending=False),
                "frequent_customers": self.frequent_customers_analysis(),
                "average_purchase_value": self.average_purchase_value_analysis(),
                "customer_recency": self.customer_recency_analysis(),
                "customer_purchase_frequency": self.customer_purchase_frequency_analysis(),
                "top_product_pairs": self.top_product_pairs_analysis()
            }
        except Exception as e:
            logging.error(f"Error in data analysis: {str(e)}")
            st.error(f"Error in data analysis: {str(e)}")
            return {}

    def frequent_customers_analysis(self):
        """Analyzing frequent customers by total amount spent"""
        return self.df.groupby("CustomerID")["TotalPrice"].sum().sort_values(ascending=False).head(10)

    def average_purchase_value_analysis(self):
        """Analyzing the average purchase value per customer"""
        return self.df.groupby("CustomerID")["TotalPrice"].mean().sort_values(ascending=False).head(10)

    def customer_recency_analysis(self):
        """Analyzing customer recency by the date of their last purchase"""
        return self.df.groupby("CustomerID")["Date"].max().sort_values(ascending=False).head(10)

    def customer_purchase_frequency_analysis(self):
        """Analyzing how frequently each customer makes a purchase"""
        return self.df.groupby("CustomerID")["TransactionID"].count().sort_values(ascending=False).head(10)

    from itertools import combinations
    from collections import Counter

    from itertools import combinations
    from collections import Counter

    def top_product_pairs_analysis(self):
        try:
            customer_products = self.df.groupby("CustomerID")["ProductName"].apply(list)
            pair_counter = Counter()

            for products in customer_products:
                pairs = combinations(sorted(set(products)), 2)
                pair_counter.update(pairs)

            pair_df = pd.DataFrame(pair_counter.items(), columns=["Product Pair", "Frequency"])
            pair_df = pair_df.sort_values(by="Frequency", ascending=False).head(10)
            pair_df["Label"] = pair_df["Product Pair"].apply(lambda x: f"{x[0]} & {x[1]}")
            return pair_df
        except Exception as e:
            logging.error(f"Error in product pair analysis: {str(e)}")
            st.error(f"Error in product pair analysis: {str(e)}")
            return pd.DataFrame()


# User Interface Module
class UserInterfaceModule:
    def __init__(self, processed_data: dict):
        self.processed_data = processed_data

    def display_best_selling_products(self):
        st.subheader("🏆 Best-Selling Products")
        products = self.processed_data["best_selling_products"]
        fig = px.bar(products, x=products.index, y=products.values, color=products.values,
                     labels={'x': 'Product', 'y': 'Quantity Sold'}, title="Top 10 Best-Selling Products")
        st.plotly_chart(fig, use_container_width=True)

    def display_monthly_sales(self):
        st.subheader("📈 Monthly Sales Trend")
        monthly_sales = self.processed_data["monthly_sales"]
        fig = px.line(monthly_sales, x=monthly_sales.index.astype(str), y=monthly_sales.values, markers=True,
                      labels={'x': 'Month', 'y': 'Total Sales'}, title="Monthly Sales Over Time")
        st.plotly_chart(fig, use_container_width=True)

    def display_regional_sales(self):
        st.subheader("📍 Regional Sales Analysis")
        regional_sales = self.processed_data["regional_sales"]
        fig = px.bar(regional_sales, x=regional_sales.index, y=regional_sales.values, color=regional_sales.values,
                     labels={'x': 'Region', 'y': 'Total Sales'}, title="Total Sales Per Region")
        st.plotly_chart(fig, use_container_width=True)

    def display_sales_by_day_of_week(self):
        st.subheader("📅 Sales by Day of the Week")
        sales_by_day = self.processed_data["sales_by_day"]
        fig = px.bar(sales_by_day, x=sales_by_day.index, y=sales_by_day.values, color=sales_by_day.values,
                     labels={'x': 'Day', 'y': 'Total Sales'}, title="Sales Performance by Day of the Week")
        st.plotly_chart(fig, use_container_width=True)

    def display_customer_behavior(self):
        st.subheader("👤 Customer Behavior Analysis")

        # Display Top 10 Frequent Customers by Total Spend
        st.write("### 🔝 Top 10 Frequent Customers (Total Spend)")
        frequent_customers = self.processed_data["frequent_customers"]
        st.bar_chart(frequent_customers)

        # Display Average Purchase Value per Customer
        st.write("### 💳 Average Purchase Value per Customer")
        avg_purchase_value = self.processed_data["average_purchase_value"]
        st.bar_chart(avg_purchase_value)

        # Display Customer Recency (Last Purchase Date)
        st.write("### ⏳ Customer Recency (Last Purchase Date)")
        recency = self.processed_data["customer_recency"]
        st.dataframe(recency)

        # Display Customer Purchase Frequency
        st.write("### 🔄 Customer Purchase Frequency")
        purchase_frequency = self.processed_data["customer_purchase_frequency"]
        st.bar_chart(purchase_frequency)

    def display_product_search(self):
        st.subheader("🔎 Product Search and Analysis")
        filtered_df = self.processed_data['full_data']

        # 🛍️ Display full product list
        st.markdown("### 📋 Available Products")
        product_table = (
            filtered_df.groupby("ProductName")
            .agg(
                Total_Quantity=("Quantity", "sum"),
                Total_Sales=("TotalPrice", "sum"),
                Transactions=("TransactionID", "count")
            )
            .sort_values("Total_Sales", ascending=False)
            .reset_index()
        )
        st.dataframe(product_table, use_container_width=True)

        # 🔍 Search input
        st.markdown("---")
        st.markdown("### 🔍 Search Specific Product")
        search_term = st.text_input("Enter product name (or part of it):", "")

        if not search_term:
            st.info("Please enter a product name to search.")
            return

        matching_products = filtered_df[
            filtered_df['ProductName'].str.contains(search_term, case=False, na=False)
        ]

        if matching_products.empty:
            st.warning("No matching products found.")
            return

        st.success(f"Found {matching_products['ProductName'].nunique()} matching product(s).")

        # 💰 Total sales and quantity
        total_sales = matching_products['TotalPrice'].sum()
        total_quantity = matching_products['Quantity'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,.2f}")
        st.metric("📦 Total Quantity Sold", f"{total_quantity:,}")

        # 📍 Regional breakdown
        st.write("### 📍 Regional Breakdown")
        region_data = matching_products.groupby("Region")["TotalPrice"].sum().sort_values(ascending=False)
        st.bar_chart(region_data)

        # 📅 Monthly trend
        st.write("### 📅 Monthly Sales Trend")
        monthly_data = matching_products.groupby(
            matching_products["Date"].dt.to_period("M")
        )["TotalPrice"].sum()
        st.line_chart(monthly_data)

    def display_top_product_pairs(self):
        st.subheader("🛒 Most Frequent Product Pairs")
        pair_df = self.processed_data["top_product_pairs"]

        if not pair_df.empty:
            fig = px.bar(
                pair_df,
                x="Frequency",
                y="Label",
                orientation="h",
                color="Frequency",
                title="Top 10 Product Pairs Bought Together",
                labels={"Label": "Product Pair", "Frequency": "Times Bought Together"}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product pair data available.")


# Main Application
class SupermarketSalesApp:
    def __init__(self, file):
        # Data Pipeline
        raw_data = DataIngestionModule.load_data(file)
        processed_data = DataProcessingModule(raw_data).process_data()
        storage = DataStorageModule(processed_data)

        # Analysis
        self.analysis = DataAnalysisModule(storage.df)
        self.processed_data = self.analysis.analyze()
        self.processed_data["full_data"] = storage.df

        # UI
        self.ui_module = UserInterfaceModule(self.processed_data)

    def run(self):
        st.markdown("<h1 style='text-align: center; color: #2E86C1;'>📊 Supermarket Sales Dashboard</h1>", unsafe_allow_html=True)
        st.sidebar.header("🔍 Navigation")
        page = st.sidebar.radio("Go to", [
            "Home","Product Search", "Best Products", "Sales Trends", "Regional Sales",
            "Day Analysis", "Customer Behavior", "Pair Product Analysis"
        ])

        if page == "Home":

            st.write("👋 Welcome to the **Supermarket Sales Dashboard**. Use the sidebar to navigate different sections.")

            # Display Key Metrics
            col1, col2, col3 = st.columns(3)
            total_sales = self.analysis.df["TotalPrice"].sum()
            total_transactions = self.analysis.df.shape[0]
            avg_sales = total_sales / total_transactions if total_transactions else 0

            col1.metric("💰 Total Revenue", f"${total_sales:,.2f}")
            col2.metric("🛒 Total Transactions", f"{total_transactions:,}")
            col3.metric("📊 Average Sale", f"${avg_sales:,.2f}")

            st.markdown("---")
        elif page == "Product Search":
            self.ui_module.display_product_search()
        elif page == "Best Products":
            self.ui_module.display_best_selling_products()
        elif page == "Sales Trends":
            self.ui_module.display_monthly_sales()
        elif page == "Regional Sales":
            self.ui_module.display_regional_sales()
        elif page == "Day Analysis":
            self.ui_module.display_sales_by_day_of_week()
        elif page == "Customer Behavior":
            self.ui_module.display_customer_behavior()
        elif page == "Pair Product Analysis":
            self.ui_module.display_top_product_pairs()

        st.write("This Application is made by Mohamed Riham - A Software Engineering Student From BCAS CAMPUS")

# Run the app
if __name__ == "__main__":
    uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        app = SupermarketSalesApp(uploaded_file)
        app.run()
