# DriftWatch

DriftWatch is a Streamlit app for detecting and visualizing data drift between training and new datasets.

## Features

- Upload a CSV dataset
- Automatically split data into training and new partitions
- Calculate feature drift metrics
- View training and new dataset statistics
- Compare distributions with histograms and box plot style visualizations

## Requirements

- Python 3.8+
- `venv` or another virtual environment tool

## Setup

1. Open a terminal in the project folder.

2. Create and activate the virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

## Run the app

```powershell
python -m streamlit run app.py
```

Then open the local URL shown in the terminal, typically `http://localhost:8501`.

## Notes

- If `streamlit run app.py` fails because the launcher is broken, use:
  ```powershell
  python -m streamlit run app.py
  ```

- The sample dataset is included in `dataset.csv`.

## Deployment

Live app: https://sukrptxcv8pobpcof5dp2j.streamlit.app/

## GitHub

Repository: https://github.com/SwaraMishra07/DriftWatch
