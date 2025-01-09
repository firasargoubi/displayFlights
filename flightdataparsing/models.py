import json
import pandas as pd
import requests
import datetime


class BaseDf:

    def __init__(self):
        """
        Initialize the processor with the URL and relevant columns.

        param url: str - The URL to fetch flight data.
        param columns_of_interest: list - The columns to retain in the final DataFrame.
        """
        self.columns_of_interest = None
        self.url = 'https://www.admtl.com/en/admtldata/api/flight?type=departure&sort=field_planned&direction=ASC&rule=24h'
        self.df = pd.DataFrame()
        self.raw_data = None
        self.structured_data = None
        self.initialise_base_df()

    def fetch_flight_data(self):
        """
        Fetch flight data from the provided URL.

        Returns:
        None - Assigns fetched data to raw_data attribute.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.raw_data = response.content
            print(f"HTTP Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data: {e}")
            raise

    def parse_json_content(self):
        """
        Parse JSON content from raw_data and store in structured_data.

        Returns:
        None - Assigns parsed JSON to structured_data attribute.
        """
        if self.raw_data:
            self.structured_data = json.loads(self.raw_data)
        else:
            raise ValueError("Raw data not available. Fetch data first.")

    def convert_to_dataframe(self, key='data'):
        """
        Convert structured JSON data into a pandas DataFrame and store in df attribute.

        param key: str - Key in the JSON data that contains the list of records.
        """
        if self.structured_data:
            self.df = pd.json_normalize(self.structured_data[key])
        else:
            raise ValueError("Structured data not available. Parse data first.")

    def initialise_base_df(self):
        """
        Pipeline to fetch, parse, and convert flight data to a DataFrame.
        """
        self.fetch_flight_data()
        self.parse_json_content()
        self.convert_to_dataframe()





class ViewDF(BaseDf):
    def __init__(self):
        super().__init__()
        self.columns_of_interest = ['flight', 'time', 'destination', 'gate']
        self.todays_date = datetime.date.today()
        self.process_data()


    def process_data(self):
        """Fetch flight data from the API and process it with the required filters and transformations."""
        try:
            self.df = self.filter_flights_by_gate_range(self.df)
            self.df = self.fix_time_columns(self.df)
            self.df = self.split_planned_column(self.df)
            self.df = self.filter_today_flights(self.df)
            self.df = self.filter_columns(self.df)
        except Exception as e:
            print(f"An error occurred while processing the data: {e}")
            raise

    def filter_flights_by_gate_range(self, df, min_gate=62, max_gate=68):
        """
        Filter flights by gate range.

        :param df: DataFrame - The raw DataFrame containing flight data.
        :param min_gate: int - Minimum gate number to filter by.
        :param max_gate: int - Maximum gate number to filter by.
        :return: DataFrame - Filtered DataFrame.
        """
        df['gate'] = pd.to_numeric(df['gate'], downcast='integer', errors='coerce')
        df = df.dropna(subset=['gate'])
        df['gate'] = df['gate'].astype(int)
        return df[(df['gate'] >= min_gate) & (df['gate'] <= max_gate)].reset_index(drop=True)

    def fix_time_columns(self, df):
        """
        Convert and adjust time columns for the DataFrame.

        :param df: DataFrame - DataFrame with raw time columns.
        :return: DataFrame - DataFrame with fixed time columns.
        """
        df['planned'] = pd.to_datetime(df['planned'], unit='s') - pd.Timedelta(hours=4)
        df['revised'] = pd.to_datetime(df['revised'], unit='s') - pd.Timedelta(hours=4)
        return df

    def split_planned_column(self, df):
        """
        Split the 'planned' column into 'date' and 'time' columns.

        :param df: DataFrame - DataFrame with a 'planned' column.
        :return: DataFrame - DataFrame with separate 'date' and 'time' columns.
        """
        df['date'] = df['planned'].dt.date
        df['time'] = df['planned'].dt.time
        return df

    def filter_today_flights(self, df):
        """
        Filter out flights that are not scheduled for today.

        :param df: DataFrame - The DataFrame with flight data.
        :return: DataFrame - Filtered DataFrame with only today's flights.
        """
        return df[df['date'] == self.todays_date]

    def filter_columns(self, df):
        """
        Filter out unnecessary columns from the DataFrame.

        :param df: DataFrame - The DataFrame with all columns.
        :return: DataFrame - DataFrame with only the relevant columns.
        """
        return df[self.columns_of_interest]

print(ViewDF().df.head())