import unittest
import pandas as pd
import numpy as np
from main import DataProcessingModule, DataAnalysisModule


class TestSalesDashboard(unittest.TestCase):

    def setUp(self):
        # Load real CSV data
        self.data = pd.read_csv("supermarket_sales.csv")

        # Ensure 'Date' is in datetime format
        self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')

        # Process and initialize modules
        self.processed_df = DataProcessingModule(self.data).process_data()
        self.analysis_module = DataAnalysisModule(self.processed_df)

    # 1. Unit Test Development
    def test_data_processing_creates_total_price(self):
        """Test if 'TotalPrice' column is added and calculated correctly"""
        self.assertIn("TotalPrice", self.processed_df.columns)
        expected_total = self.data["Quantity"].iloc[0] * self.data["PriceperUnit"].iloc[0]
        self.assertEqual(self.processed_df.loc[0, "TotalPrice"], expected_total)

    def test_date_column_is_datetime(self):
        """Test if 'Date' column is converted to datetime format"""
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.processed_df["Date"]))

    def test_no_missing_or_duplicate_data(self):
        """Test for no missing or duplicate rows after processing"""
        self.assertFalse(self.processed_df.isnull().values.any())
        self.assertEqual(len(self.processed_df), len(self.processed_df.drop_duplicates()))

    # 2. Integration Testing
    def test_analysis_on_processed_data(self):
        """Test that analysis works correctly on processed data"""
        result = self.analysis_module.analyze()
        self.assertIn("best_selling_products", result)
        self.assertIn("monthly_sales", result)
        self.assertIn("regional_sales", result)

    # 3. System Testing
    def test_system_behavior(self):
        """Test the overall system to check if it performs as expected"""
        # Test customer recency analysis
        result = self.analysis_module.customer_recency_analysis()

        # Print result to inspect the structure
        print(result)

        # Check that the result is a Series
        self.assertTrue(isinstance(result, pd.Series))

        # Print the type of the index to check it
        print("Index Type:", type(result.index[0]))

        import numpy as np

        # Check if the index is of integer type (including numpy.int64)
        self.assertTrue(isinstance(result.index[0], (int, np.int64)),
                        "Index is not of expected type (int or numpy.int64)")

        # Check if the values are of datetime type (since they represent dates)
        self.assertTrue(isinstance(result.iloc[0], pd.Timestamp), "Values are not of expected type (datetime)")

        # Test best-selling product analysis
        result = self.analysis_module.analyze()["best_selling_products"]
        self.assertIsInstance(result.idxmax(), str)
        self.assertGreater(result.max(), 0)

    # Additional specific tests for different analyses
    def test_best_selling_product_exists(self):
        """Test that best-selling product by quantity is returned and is a string"""
        result = self.analysis_module.analyze()["best_selling_products"]
        self.assertIsInstance(result.idxmax(), str)
        self.assertGreater(result.max(), 0)

    def test_monthly_sales_grouping(self):
        """Test monthly sales returns expected format and more than 0 months"""
        result = self.analysis_module.analyze()["monthly_sales"]
        self.assertTrue(isinstance(result.index[0], pd.Period))
        self.assertGreater(len(result), 0)

    def test_region_with_highest_sales_exists(self):
        """Test if region with highest total sales is correctly identified"""
        result = self.analysis_module.analyze()["regional_sales"]
        self.assertIsInstance(result.idxmax(), str)
        self.assertGreater(result.max(), 0)

    def test_customer_purchase_frequency_valid(self):
        """Test customer frequency analysis returns a valid result"""
        result = self.analysis_module.customer_purchase_frequency_analysis()
        self.assertTrue(result.index[0])
        self.assertGreater(result.max(), 0)

    def test_average_purchase_value_has_values(self):
        """Test average purchase value returns Series with valid values"""
        result = self.analysis_module.average_purchase_value_analysis()
        self.assertIsInstance(result, pd.Series)
        self.assertTrue(all(v > 0 for v in result.values))

    def test_customer_recency_valid(self):
        """Test that the most recent customer ID is not empty when converted to string"""
        result = self.analysis_module.customer_recency_analysis()
        recent_customer = str(result.index[0])
        self.assertTrue(recent_customer.strip() != "")


if __name__ == "__main__":
    unittest.main()
