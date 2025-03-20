import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional
from services.alpha_vantage import AlphaVantageService
import logging
logger = logging.getLogger("fetch_daily_router")


alpha_vantage = AlphaVantageService()

class PricePredictionTool:
    """A tool for financial price prediction with ML capabilities."""
    
    def __init__(self, model_directory: str = 'models'):
        """Initialize the PricePredictionTool."""
        self.model_directory = model_directory
        os.makedirs(model_directory, exist_ok=True)
        self.data = None
        self.symbol = None
        self.classifier_model = None
        self.regressor_model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    async def fetch_data(self, symbol: str, period: str = '1y', interval: str = '1d', 
                  source: str = 'alphavantage') -> pd.DataFrame:
        """Fetch financial data from the specified source."""
        self.symbol = symbol
        if source.lower() == 'alphavantage':
            data = await alpha_vantage.fetch(symbol, "TIME_SERIES_INTRADAY")
            data = self._prepare_dataframe(data)
        else:
            raise ValueError(f"Unsupported data source: {source}")
        
        if data is None or data.empty:
            raise ValueError(f"No data retrieved for symbol {symbol}")
            
        self.data = data
        return data
    
    def _prepare_dataframe(self, data: dict) -> pd.DataFrame:
        columns = {
                'index' : 'timestamp',
                '1. open' : 'open',
                '2. high' : 'high',
                '3. low' : 'low',
                '4. close' : 'close',
                '5. adjusted close' : 'adjusted_close',
                '6. volume' : 'volume',
                '5. volume' : 'volume',
                '7. dividend amount' : 'dividend_amount',
                '8. split coefficient' : 'split_coefficient'
            }

        time_series_keys = [key for key in data if key.startswith("Time Series")]
        logger.info(f"Time series keys: {time_series_keys}")
        if not time_series_keys:
            raise ValueError("Time Series data not found in the input dictionary")
        time_series_key = time_series_keys[0]

        df = pd.DataFrame(data[time_series_key]).T.reset_index()
        df = df.rename(columns=columns)
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df


    def add_indicators(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        if data is None:
            if self.data is None:
                raise ValueError("No data available. Fetch data first.")
            data = self.data.copy()
        
        # Moving Averages
        data['MA5'] = data['close'].rolling(window=5).mean()
        data['MA20'] = data['close'].rolling(window=20).mean()
        data['MA50'] = data['close'].rolling(window=50).mean()
        
        # MACD
        data['EMA12'] = data['close'].ewm(span=12, adjust=False).mean()
        data['EMA26'] = data['close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        # RSI
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['close'].rolling(window=20).mean()
        data['BB_Std'] = data['close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
        data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
        
        # Stochastic Oscillator
        n = 14
        data['L14'] = data['low'].rolling(window=n, min_periods=1).min()
        data['H14'] = data['high'].rolling(window=n, min_periods=1).max()
        
        # Handle division by zero and NaN values
        denominator = data['H14'] - data['L14']
        epsilon = 1e-8  # Small value to prevent division by zero
        # data['%K'] = 100 * ((data['close'] - data['L14']) / (denominator + epsilon))
        
        # # Forward fill to handle initial NaN values
        # data['%K'] = data['%K'].fillna(method='ffill')
        # data['%D'] = data['%K'].rolling(window=3).mean().fillna(method='ffill')
        
        # Price momentum
        data['Momentum'] = data['close'].pct_change(periods=10)
        
        # Drop rows with NaN values
        data.dropna(inplace=True)
        self.data = data
        return data
    
    def identify_support_resistance(self, window: int = 10, 
                                    threshold: float = 0.02) -> Dict[str, List[float]]:
        if self.data is None:
            raise ValueError("No data available. Fetch data first.")
        
        data = self.data.copy()
        levels = {'support': [], 'resistance': []}
        
        # Find potential support levels (local lows)
        for i in range(window, len(data) - window):
            if all(data['low'].iloc[i] <= data['low'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['low'].iloc[i] <= data['low'].iloc[i+j] for j in range(1, window+1)):
                levels['support'].append(data['low'].iloc[i])
        
        # Find potential resistance levels (local highs)
        for i in range(window, len(data) - window):
            if all(data['high'].iloc[i] >= data['high'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['high'].iloc[i] >= data['high'].iloc[i+j] for j in range(1, window+1)):
                levels['resistance'].append(data['high'].iloc[i])
        
        def cluster_levels(levels_list, threshold_pct):
            if not levels_list:
                return []
            
            clustered = []
            current_price = data['close'].iloc[-1]

            levels_list = sorted(levels_list)

            current_cluster = [levels_list[0]]
            
            for level in levels_list[1:]:
                if abs(level - current_cluster[-1]) / current_price < threshold_pct:
                    current_cluster.append(level)
                else:
                    clustered.append(sum(current_cluster) / len(current_cluster))
                    current_cluster = [level]

            if current_cluster:
                clustered.append(sum(current_cluster) / len(current_cluster))
            
            return clustered
        
        # Cluster the levels
        levels['support'] = cluster_levels(levels['support'], threshold)
        levels['resistance'] = cluster_levels(levels['resistance'], threshold)
        
        return levels

    async def prepare_features(self, data: Optional[pd.DataFrame] = None, 
                         target_column: str = 'close', 
                         prediction_days: int = 5):
        if data is None:
            if self.data is None:
                raise ValueError("No data available. Fetch and process data first.")
            data = self.data.copy()
        
        target_column = 'close'
        data[f'Future_{target_column}'] = data[target_column].shift(-prediction_days)
        
        # Create target variable for classification (1 if price goes up, 0 if down)
        data['Target_Direction'] = (data[f'Future_{target_column}'] > data[target_column]).astype(int)
        
        # Drop rows with NaN in the target
        data.dropna(inplace=True)
        
        # Select feature columns
        exclude_cols = ['Date', 'Datetime', 'date', 'datetime', 'timestamp', 'index', 
                         f'Future_{target_column}', 'Target_Direction']
        feature_cols = [col for col in data.columns if col not in exclude_cols and 
                        not pd.isna(data[col]).any()]
        
        # Prepare data for training
        X = data[feature_cols].values
        y_reg = data[f'Future_{target_column}'].values
        y_cls = data['Target_Direction'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_reg_train, y_reg_test = train_test_split(
            X_scaled, y_reg, test_size=0.2, shuffle=False)
        _, _, y_cls_train, y_cls_test = train_test_split(
            X_scaled, y_cls, test_size=0.2, shuffle=False)
        
        return X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test, feature_cols
    
    async def train_models(self, n_estimators: int = 100, random_state: int = 42) -> Dict[str, float]:
        """Train machine learning models for price prediction."""
        if self.data is None:
            raise ValueError("No data available. Fetch and process data first.")
        
        # Prepare features and targets
        X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test, feature_cols = \
            await self.prepare_features()
        
        # Train regressor model (predicts price)
        regressor = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        regressor.fit(X_train, y_reg_train)
        reg_preds = regressor.predict(X_test)
        reg_rmse = np.sqrt(np.mean((y_reg_test - reg_preds) ** 2))
        
        # Train classifier model (predicts direction)
        classifier = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        classifier.fit(X_train, y_cls_train)
        cls_preds = classifier.predict(X_test)
        cls_accuracy = np.mean(cls_preds == y_cls_test)
        
        # Save models
        self.regressor_model = regressor
        self.classifier_model = classifier
        self.feature_columns = feature_cols
        
        # Save models to disk
        # model_path = os.path.join(self.model_directory, f"{self.symbol}_models.joblib")
        # scaler_path = os.path.join(self.model_directory, f"{self.symbol}_scaler.joblib")
        
        # joblib.dump({
        #     'regressor': regressor,
        #     'classifier': classifier,
        #     'feature_columns': feature_cols
        # }, model_path)
        
        # joblib.dump(self.scaler, scaler_path)
        
        return {
            'regression_rmse': reg_rmse,
            'classification_accuracy': cls_accuracy
        }

    async def predict(self, data: Optional[pd.DataFrame] = None, 
                days_ahead: int = 5) -> Dict[str, Union[float, str, List[float]]]:
        if self.regressor_model is None or self.classifier_model is None:
            raise ValueError("Models not trained or loaded. Train or load models first.")
        
        if data is None:
            if self.data is None:
                raise ValueError("No data available. Fetch data first.")
            data = self.data.copy()

        data = self.add_indicators(data)

        latest_data = data.iloc[-1:][self.feature_columns].values

        latest_scaled = self.scaler.transform(latest_data)

        price_prediction = self.regressor_model.predict(latest_scaled)[0]
        direction_proba = self.classifier_model.predict_proba(latest_scaled)[0]
        direction_prediction = 'Bullish' if direction_proba[1] > 0.5 else 'Bearish'
        
        # Get current price
        current_price = data['close'].iloc[-1]
        
        # Calculate percent change
        percent_change = ((price_prediction - current_price) / current_price) * 100
        
        # Get support and resistance levels
        levels = self.identify_support_resistance()
        
        # Find closest support and resistance
        current_supports = [level for level in levels['support'] if level < current_price]
        current_resistances = [level for level in levels['resistance'] if level > current_price]
        
        closest_support = max(current_supports) if current_supports else None
        closest_resistance = min(current_resistances) if current_resistances else None
        
        # Create prediction result
        result = {
            'symbol': self.symbol,
            'current_price': current_price,
            'prediction_date': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),
            'predicted_price': price_prediction,
            'percent_change': percent_change,
            'direction': direction_prediction,
            'bullish_probability': float(direction_proba[1]),
            'bearish_probability': float(direction_proba[0]),
            'support_levels': levels['support'],
            'resistance_levels': levels['resistance'],
            'closest_support': closest_support,
            'closest_resistance': closest_resistance,
            'indicators': {
                'rsi': data['RSI'].iloc[-1],
                'macd': data['MACD'].iloc[-1],
                'macd_signal': data['MACD_Signal'].iloc[-1],
                # 'stochastic_k': data['%K'].iloc[-1],
                # 'stochastic_d': data['%D'].iloc[-1]
            }
        }
        
        return result
    
    async def run_analysis(self, symbol: str, period: str = '1y', interval: str = '1d', 
                     train_model: bool = True, visualize_results: bool = True):
        """Run a complete analysis for a symbol."""
        # Fetch data
        await self.fetch_data(symbol, period, interval)
        
        # Add indicators
        self.add_indicators()
        
        await self.train_models()
        
        prediction = await self.predict()
        
        return prediction

if __name__ == '__main__':
    price_tool = PricePredictionTool()
    prediction = price_tool.run_analysis('AAPL')
    print(f"Current Price: ${prediction['current_price']:.2f}")
    print(f"Predicted Price: ${prediction['predicted_price']:.2f} ({prediction['percent_change']:.2f}%)")
    print(f"Direction: {prediction['direction']} (Confidence: {max(prediction['bullish_probability'], prediction['bearish_probability'])*100:.1f}%)")
    print(f"Support levels: {[f'${x:.2f}' for x in prediction['support_levels']]}")
    print(f"Resistance levels: {[f'${x:.2f}' for x in prediction['resistance_levels']]}")