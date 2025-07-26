# 💰 Personal Expense Tracker

A simple, interactive **Streamlit** web app that helps you manage personal expenses by tracking daily spending, categorising expenses, setting monthly budgets, and exporting your data to CSV — all with a modern dark-themed UI.

---

## 📸 Screenshots

### ➕ Add New Expense  
![Add Expense](./Add%20Expense.jpg)

---

### 📄 View All Expenses  
![View Expenses](./View%20Expense.jpg)

---

### 📊 Track Monthly Budget  
![Track Budget](./Track%20Budget.jpg)

---

### 💾 Save Expense Data  
![Save Data](./Saving%20File.jpg)

---

## 🚀 Live Demo  
The app is hosted on **Streamlit Cloud**:  
👉 [Launch the App](https://share.streamlit.io/your-app-link)

---

## 🛠 Features

- ✅ Add daily expenses with date, category, amount, and optional description  
- ✅ View all saved expenses in a sortable and filterable table  
- ✅ Set and monitor your monthly budget  
- ✅ Visualise your spending progress with a budget bar  
- ✅ Download all expenses as a CSV file

---

## 🧠 How It Works

The app uses the following logic and libraries:

- `streamlit` for UI rendering  
- `pandas` for data manipulation and CSV operations  
- `datetime` and `os` for date handling and file operations  
- Data persistence is handled using `expenses.csv` stored on the server

---

## 📂 Project Structure

```bash
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
└── README.md             # Project overview (this file)
