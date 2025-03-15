# Interactice 3D Globe Model
https://global-impact-analysis-visualization-platform-c4bkttmkdwjxkcpk.streamlit.app/
## Setup Instructions
## Before running, please combine the city_temperature1 and city_temperature2 into city_temperature.csv

### 1. Setting up the Environment

To set up the environment for this project, it is recommended to use a virtual environment to avoid conflicts with other Python packages. You can create and activate a virtual environment using the following steps:

- **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

- **Activate the virtual environment**:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

- **Install dependencies**:
    Once the virtual environment is activated, install the required packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Running the Project

After setting up the environment, you can run the project by entering the following command in the terminal:

```bash
streamlit run app.py
```
### 3.Streamlit Mode

The project is configured to open in Streamlit's wide mode by default. If needed, you can manually turn off the wide mode within the Streamlit UI in your browser.

### 4.Data Coverage
Please note that the dataset used in this project is based on the intersection of all available data, meaning it does not cover data for every country in the world. Some countries may be missing due to this limitation.

### 5.Data Processing
The data preprocessing steps have already been performed. The related code is located in the preprocess folder. You do not need to re-run the data preprocessing.

### 6.Data Folder
The data folder contains both processed and unprocessed data. You can find the processed data ready for use in the project, and the raw data files that were used for preprocessing.

### 7. Components Folder
The core functionality of the website is implemented in the components folder. This folder contains the key modules that define the various features and behavior of the application.

### 8. Acknowledgements
The primary developers of this web application are Ge Chang and Mai Wenxuan.
Special thanks to the other team members for their valuable contributions, particularly in data collection.

# License

This project is licensed under the **Unlicense**. 

The Unlicense is a public domain dedication, meaning you can do anything with this code without any restrictions.

## You can:

- Use the code for any purpose.
- Modify the code.
- Distribute the code.
- Sublicense the code.
- Combine it with other projects.
- Sell copies of the code.

## No warranty

This software is provided "as is", without any express or implied warranty. In no event shall the authors be held liable for any damages arising from the use of this software.

## Full Text

The full text of the Unlicense is as follows:

