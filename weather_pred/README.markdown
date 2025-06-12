# Weather Forecasting for New Delhi Using LSTM 🌦️

This project develops a deep learning model to predict the next day's temperature in New Delhi using historical weather data. The model employs a stacked Long Short-Term Memory (LSTM) neural network trained on preprocessed weather features, achieving a **validation RMSE of 3.5350°C** and a **test RMSE of ~4.3767°C** 📈.

## **Project Overview** 🚀

The goal is to forecast the daily temperature (`next_day_temp`) in New Delhi using a time-series approach. The pipeline includes:
- **Data Preprocessing**: Cleaning, feature engineering, and scaling 🧹.
- **Exploratory Data Analysis (EDA)**: Visualizing trends, correlations, seasonality, and stationarity 📊.
- **Model Training**: Building and training a stacked LSTM model with time-series cross-validation 🧠.
- **Prediction**: Forecasting the next 5 days' temperatures using the trained model 🔮.

## **Dataset** 📂

The dataset consists of historical weather data for New Delhi, preprocessed into three CSV files:
- `New Delhi_train_preprocessed.csv`: Training set (~80% of data).
- `New Delhi_val_preprocessed.csv`: Validation set (~10% of data).
- `New Delhi_test_preprocessed.csv`: Test set (~10% of data).

### Features
- **Key Features**: `temperature_celsius`, `humidity`, `pressure_mb`, `wind_kph`, `precip_mm`, `cloud`, `feels_like_celsius`, `visibility_km`, `uv_index`, `gust_kph`, `air_quality_PM2.5`, `air_quality_us-epa-index`.
- **Engineered Features**: `temp_lag_1`, `temp_lag_2`, `temp_rolling_mean_3`, `temp_rolling_std_7`, `month`, `day_of_week`, `hour`, `season_Winter`, `season_Spring`, `season_Summer`, `season_Fall`, `wind_direction_sin`, `wind_direction_cos`.
- **Target**: `next_day_temp` (next day's temperature in °C, unscaled).

Features are scaled using `StandardScaler`, except for `next_day_temp`.


## **Prerequisites** ⚙️

- **Environment**: Google Colab (recommended) or local Python environment with GPU support.
- **Libraries**:
  ```bash
  pip install pandas numpy matplotlib seaborn statsmodels tensorflow scikit-learn
  ```

## **Setup** 🛠️

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/new-delhi-weather-forecast.git
   cd new-delhi-weather-forecast
   ```

2. **Upload Datasets**:
   - Place `New Delhi_train_preprocessed.csv`, `New Delhi_val_preprocessed.csv`, and `New Delhi_test_preprocessed.csv` in the `/content/` directory of Google Colab.
   - Ensure datasets match the feature set used in training.

3. **Install Dependencies**:
   Run in Colab:
   ```bash
   !pip install pandas numpy matplotlib seaborn statsmodels tensorflow scikit-learn
   ```

## **Usage** ▶️

### **Step 1: Exploratory Data Analysis (EDA)** 📊

**Outputs** (console):
- Temperature trend plot 🌡️.
- Correlation heatmap.
- Monthly temperature patterns (if `month` exists).
- Feature distribution histograms.
- Humidity vs. precipitation scatter plot.
- Augmented Dickey-Fuller (ADF) test for stationarity.
- Summary statistics and correlation matrix.

### **Step 2: Model Training** 🧠

**Model Details**:
- **Architecture**: Stacked LSTM (2 layers, 50 units each), dropout (0.2), dense output layer.
- **Optimizer**: Adam (learning_rate=0.001).
- **Loss**: Mean Squared Error (MSE).
- **Time Steps**: 7 days.
- **Epochs**: 10.
- **Cross-Validation**: 5-fold walk-forward validation.

**Outputs** (console):
- Training/validation loss plot 📈.
- Validation MSE: 12.4960, RMSE: 3.5350°C ✅.
- Test MSE: 19.1555, RMSE: ~4.3767°C ✅.
- Predictions vs. actuals plot.
- Cross-validation MSE scores.

**Saved**:
- `New Delhi_lstm_model.h5`: Trained model.

### **Step 3: Predict Next 5 Days** 🔮

**Outputs** (console):
- Predicted temperatures (e.g., "Day 1: 25.50°C") 🌡️.
- Actual temperatures (if available).
- Plot of predicted (and actual) temperatures 📊.

## **Results** 📈

- **Validation Performance**:
  - MSE: 12.4960
  - RMSE: 3.5350°C
- **Test Performance**:
  - MSE: 19.1555
  - RMSE: ~4.3767°C

- **Analysis**:
  - The model achieves decent performance, with predictions off by ~3.5–4.4°C on average ✅.
  - Test RMSE is higher than validation, suggesting potential overfitting or distribution shift.
  - Compared to a persistence baseline (RMSE ~3–5°C), the model offers limited improvement.

## **Future Improvements** 💡

- **Increase Epochs**: Train for 20–50 epochs with `EarlyStopping`.
- **Tune Hyperparameters**: Test more LSTM units (e.g., 100) or lower learning rate (e.g., 0.0001).
- **Feature Engineering**: Incorporate external data (e.g., weather forecasts).
- **Model Variants**: Try GRU or Transformer models.
- **Reduce Overfitting**: Increase dropout (e.g., 0.3) or add regularization.

## **Troubleshooting** 🛠️

- **Crashes in Colab**:
  - Verify files: `!ls /content/`.
  - Reduce `time_steps` (e.g., 3) for small datasets.
  - Clear memory: `!rm -rf /content/*.h5` (except datasets).
  - Use Colab Pro for larger datasets.
- **Feature Mismatch**:
  - Check: `print(df_test.columns)`.
- **Model Loading Issues**:
  - Ensure `New Delhi_lstm_model.h5` matches `time_steps` and features.

## **Contributing** 🤝

Contributions are welcome! Please:
1. Fork the repository.
2. Create a branch: `git checkout -b feature-name`.
3. Commit: `git commit -m 'Add feature'`.
4. Push: `git push origin feature-name`.
5. Open a pull request.

## **License** 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file.

## **Contact** 📬

For questions, contact [Your Name] at [your.email@example.com] or open a GitHub issue.

---

*Generated on June 12, 2025* 🕒