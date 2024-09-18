import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import glob
import joblib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

def save_model(model, filename='trained_model.pkl'):
    try:
        joblib.dump(model, filename)
        logging.info(f"Model saved to {filename}")
        print(f"Model saved successfully to {filename}") 
    except Exception as e:
        logging.error(f"Failed to save model: {e}")
        print(f"Error saving model: {e}") 

file_paths = glob.glob('C:/Predict Model/*.csv')

def load_and_concatenate_csv(file_paths):
    """Load and concatenate CSV files into a single DataFrame."""
    data_list = []
    for file in file_paths:
        try:
            data_list.append(pd.read_csv(file))
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return pd.concat(data_list, ignore_index=True)

def preprocess_data(data):
    """Preprocess the data by converting date column and selecting features and target."""
    data['data'] = pd.to_datetime(data['data']).dt.date  
    X = data[['temperatura', 'umidade']]
    y = data['precipitacao']
    dates = data['data']
    return X, y, dates

def split_data(X, y, dates, test_size=0.2, random_state=42):
    """Split the data into training and testing sets."""
    return train_test_split(X, y, dates, test_size=test_size, random_state=random_state)

def train_model(X_train, y_train, n_estimators=100, random_state=42):
    """Train the RandomForestRegressor model."""
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate the model and return RMSE and R² scores."""
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    return rmse, r2, y_pred

def create_results_dataframe(dates_test, y_test, y_pred):
    """Create a DataFrame with predictions, actual values, and dates."""
    resultados = pd.DataFrame({'Data': dates_test, 'Real': y_test, 'Previsto': y_pred})
    return resultados.sort_values(by='Data')

def main():
    data = load_and_concatenate_csv(file_paths)
    X, y, dates = preprocess_data(data)
    X_train, X_test, y_train, y_test, dates_train, dates_test = split_data(X, y, dates)
    model = train_model(X_train, y_train)
    rmse, r2, y_pred = evaluate_model(model, X_test, y_test)
    save_model(model)

    print(f"RMSE (Erro Médio Quadrático): {rmse:.2f}")
    print(f"R² (Coeficiente de Determinação): {r2:.2f}")
    
    resultados = create_results_dataframe(dates_test, y_test, y_pred)
    
    print(resultados.head())

    resultados.to_csv('previsoes_resultados.csv', index=False)
    print("Previsões e resultados exportados para 'previsoes_resultados.csv'.")

if __name__ == "__main__":
    main()
