## 📊 AI-Powered SQL Data Analyst

This Streamlit app enables users to upload CSV or Excel files and perform **automated SQL-based data analysis** using [Groq's LLM API](https://groq.com). The app uses **DuckDB** to execute SQL queries generated from natural language inputs, making data exploration and analytics seamless for non-technical users.

---
###🎥 Demo
[watch the demo](https://youtu.be/-23Tb1Gmv1A)

### 🔧 Features

* 🗂 Upload and manage multiple datasets (CSV, Excel)
* 🧠 Ask questions in plain English — the app generates and executes SQL queries using Groq’s LLM
* 🐥 Lightweight SQL execution engine (DuckDB)
* 🚀 Instant results and table previews

---

### 🧪 Example Use Case

Upload a dataset like sales.csv and ask:

> "What is the total revenue grouped by region?"

The app will:

1. Convert your question into an SQL query using Groq
2. Execute the query using DuckDB
3. Show the results in a clean table format

---

### 🛠️ Technologies Used

* **Python**
* **Streamlit** – for web UI
* **DuckDB** – in-memory SQL execution engine
* **Groq API** – LLM-based SQL generation
* **dotenv** – environment variable management
* **pandas** – for data manipulation

---

### 🚀 Getting Started

#### 1. Install dependencies

```bash
pip install -r requirements.txt
```

#### 2. Add your Groq API Key

Create a `.env` file in the root directory and include:

```
GROQ_API_KEY=your_actual_api_key_here
```

#### 3. Run the App

```bash
streamlit run your_script_name.py
```

---

### 📂 File Structure

```bash
.
├── app.py
├── requirements.txt
├── .env
└── README.md
```

---

### 📌 Notes

* Only `.csv` and `.xlsx` files are supported
* Make sure to name tables meaningfully when uploading
* The SQL queries are generated based on column names and data types
