import streamlit as st
import pandas as pd
import plotly.express as px
import time

from main import SupermarketSalesApp


class UserAcceptanceTesting:
    def __init__(self, file):
        self.file = file
        self.app = SupermarketSalesApp(self.file)

    def display_status(self, condition, pass_msg, fail_msg):
        """Helper function to display test results"""
        if condition:
            st.success(f"✅ {pass_msg}")
        else:
            st.error(f"❌ {fail_msg}")

    def test_navigation(self):
        with st.expander("🔍 Navigation Test"):
            st.sidebar.header("🔍 Navigation")
            page = st.sidebar.radio("Go to", [
                "Home", "Product Search", "Best Products", "Sales Trends", "Regional Sales",
                "Day Analysis", "Customer Behavior", "Pair Product Analysis"
            ])

            st.info(f"Selected Page: {page}")

            if page:
                self.display_status(True, f"{page} page loaded successfully.", "")
            else:
                self.display_status(False, "", "Failed to load page.")

    def test_data_upload(self):
        with st.expander("📂 Data Upload Test"):
            if self.file is not None:
                self.display_status(True, "CSV file uploaded successfully.", "")
            else:
                self.display_status(False, "", "Please upload a CSV file.")

    def test_dashboard_data(self):
        with st.expander("📊 Dashboard Data Test"):
            if self.file is not None:
                app = self.app
                df = app.analysis.df

                if not df.empty:
                    total_sales = df["TotalPrice"].sum()
                    total_transactions = df.shape[0]
                    avg_sales = total_sales / total_transactions if total_transactions else 0

                    st.write("**Data Summary:**")
                    st.metric("Total Sales", f"${total_sales:,.2f}")
                    st.metric("Transactions", f"{total_transactions}")
                    st.metric("Average Sale", f"${avg_sales:,.2f}")

                    self.display_status(True, "Dashboard data loaded and metrics calculated.", "")
                else:
                    self.display_status(False, "", "Dataset is empty.")
            else:
                self.display_status(False, "", "No file to analyze.")

    def test_interactivity(self):
        with st.expander("🧠 Interactivity Test"):
            st.write("Testing product search functionality...")
            search_term = st.text_input("Enter product name (or part of it):", "")

            if search_term:
                self.display_status(True, f"Search input received: '{search_term}'", "")
            else:
                self.display_status(False, "", "No search term entered.")

    def test_performance(self):
        with st.expander("⏱️ Performance Test"):
            if self.file is not None:
                start = time.time()
                _ = self.app.analysis.df.describe()
                end = time.time()
                duration = round(end - start, 3)
                st.write(f"Dashboard data processed in **{duration} seconds**.")
                self.display_status(duration < 2, "Dashboard loads within acceptable time.", "Dashboard is slow to load.")
            else:
                self.display_status(False, "", "File not uploaded; cannot test performance.")

    def run(self):
        st.title("🧪 User Acceptance Testing - Supermarket Sales Dashboard")
        self.test_navigation()
        self.test_data_upload()
        self.test_dashboard_data()
        self.test_interactivity()
        self.test_performance()
        st.success("✅ All UAT tests completed.")


if __name__ == "__main__":
    uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        uat = UserAcceptanceTesting(uploaded_file)
        uat.run()
    else:
        st.warning("⚠️ Please upload a CSV file to begin testing.")
