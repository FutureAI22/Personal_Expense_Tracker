import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Constants ---
EXPENSE_FILE = 'expenses.csv'
DATE_FORMAT = '%Y-%m-%d'

# --- Helper Functions ---
def load_expenses():
    """Loads expenses from a CSV file. Creates an empty file if it doesn't exist."""
    if not os.path.exists(EXPENSE_FILE):
        # Create an empty CSV with headers if it doesn't exist
        df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        df.to_csv(EXPENSE_FILE, index=False)
        return []
    try:
        df = pd.read_csv(EXPENSE_FILE)
        # Convert DataFrame rows to list of dictionaries
        return df.to_dict(orient='records')
    except pd.errors.EmptyDataError:
        return [] # Return empty list if CSV is empty but exists
    except Exception as e:
        st.error(f"Error loading expenses: {e}")
        return []

def save_expenses(expenses):
    """Saves expenses to a CSV file on the server (for app persistence)."""
    if not expenses:
        # If no expenses, create an empty DataFrame with headers
        df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
    else:
        df = pd.DataFrame(expenses)
        # Ensure correct column order
        df = df[['Date', 'Category', 'Amount', 'Description']]
    try:
        df.to_csv(EXPENSE_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving expenses to server: {e}")

def validate_expense(expense):
    """Validates an expense entry."""
    if not all(k in expense and expense[k] for k in ['Date', 'Category', 'Amount']):
        return False, "Missing Date, Category, or Amount."
    try:
        # Attempt to convert amount to float
        float(expense['Amount'])
    except ValueError:
        return False, "Amount must be a valid number."
    try:
        # Attempt to parse date
        datetime.strptime(expense['Date'], DATE_FORMAT)
    except ValueError:
        return False, "Date format should be YYYY-MM-DD."
    return True, ""

# --- Streamlit App Layout ---
def main():
    st.set_page_config(layout="wide", page_title="Personal Expense Tracker")

    # Initialize session state for expenses and budget if not already present
    if 'expenses' not in st.session_state:
        st.session_state.expenses = load_expenses()
    if 'monthly_budget' not in st.session_state:
        st.session_state.monthly_budget = 0.0

    st.title("💰 Personal Expense Tracker")

    # Sidebar for navigation with a dropdown menu
    st.sidebar.header("Navigation")
    menu_selection = st.sidebar.selectbox(
        "Go to",
        ("Add Expense", "View Expenses", "Track Budget", "Save Data")
    )

    # --- Add Expense Section ---
    if menu_selection == "Add Expense":
        st.header("Add New Expense")
        with st.form("expense_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.today(), format="YYYY-MM-DD")
            # Example categories, you can make this dynamic or a text input
            category_options = ["Food", "Transport", "Shopping", "Entertainment", "Bills", "Health", "Other"]
            category = st.selectbox("Category", category_options)
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            description = st.text_area("Description (Optional)")

            submitted = st.form_submit_button("Add Expense")

            if submitted:
                new_expense = {
                    "Date": date.strftime(DATE_FORMAT),
                    "Category": category,
                    "Amount": amount,
                    "Description": description
                }
                is_valid, message = validate_expense(new_expense)
                if is_valid:
                    st.session_state.expenses.append(new_expense)
                    st.success("Expense added successfully!")
                else:
                    st.error(f"Failed to add expense: {message}")

    # --- View Expenses Section ---
    elif menu_selection == "View Expenses":
        st.header("View All Expenses")
        if st.session_state.expenses:
            # Filter out invalid entries for display, but keep them in session_state for now
            valid_expenses_for_display = []
            for exp in st.session_state.expenses:
                is_valid, _ = validate_expense(exp)
                if is_valid:
                    valid_expenses_for_display.append(exp)
                else:
                    st.warning(f"Skipping incomplete or invalid entry: {exp}")

            if valid_expenses_for_display:
                df_expenses = pd.DataFrame(valid_expenses_for_display)
                # Ensure 'Amount' is numeric for sorting/calculations
                df_expenses['Amount'] = pd.to_numeric(df_expenses['Amount'], errors='coerce')
                # Sort by date
                df_expenses['Date'] = pd.to_datetime(df_expenses['Date'])
                df_expenses = df_expenses.sort_values(by='Date', ascending=False)
                df_expenses['Date'] = df_expenses['Date'].dt.strftime(DATE_FORMAT) # Convert back to string for display
                st.dataframe(df_expenses, use_container_width=True)
            else:
                st.info("No valid expenses to display.")
        else:
            st.info("No expenses added yet. Add some in the 'Add Expense' section!")

    # --- Track Budget Section ---
    elif menu_selection == "Track Budget":
        st.header("Monthly Budget Tracking")

        # Input for monthly budget
        current_budget = st.session_state.monthly_budget
        new_budget = st.number_input("Set Monthly Budget", value=current_budget, min_value=0.0, format="%.2f")
        if new_budget != current_budget:
            st.session_state.monthly_budget = new_budget
            st.success(f"Monthly budget set to £{st.session_state.monthly_budget:,.2f}")

        # Calculate total spending for the current month
        total_spending = 0.0
        current_month = datetime.now().strftime('%Y-%m') # e.g., '2025-07'

        for expense in st.session_state.expenses:
            is_valid, _ = validate_expense(expense)
            if is_valid and expense['Date'].startswith(current_month):
                try:
                    total_spending += float(expense['Amount'])
                except ValueError:
                    # This case should ideally be caught by validate_expense, but as a safeguard
                    st.warning(f"Invalid amount found for an expense: {expense['Amount']}")

        st.subheader(f"Current Month's Spending ({current_month})")
        st.write(f"Total Spending: **£{total_spending:,.2f}**")
        st.write(f"Monthly Budget: **£{st.session_state.monthly_budget:,.2f}**")

        if st.session_state.monthly_budget > 0:
            remaining_budget = st.session_state.monthly_budget - total_spending
            budget_percentage = (total_spending / st.session_state.monthly_budget) * 100

            st.progress(min(100, int(budget_percentage)), text=f"{int(budget_percentage)}% of budget used")

            if remaining_budget >= 0:
                st.success(f"Remaining Budget: **£{remaining_budget:,.2f}**")
            else:
                st.error(f"You are **£{-remaining_budget:,.2f}** over budget!")
        elif total_spending > 0:
            st.info("Set a monthly budget to track your spending against it.")
        else:
            st.info("No spending recorded for this month yet, or no budget set.")

    # --- Save Data Section ---
    elif menu_selection == "Save Data":
        st.header("Save Expense Data")

        # Option 2: Download to local machine (user chooses location)
        st.subheader("Download to Your Computer")
        st.write("Generate a CSV file of your expenses and download it to your local machine.")

        # Get valid expenses for download
        valid_expenses_for_download = [exp for exp in st.session_state.expenses if validate_expense(exp)[0]]
        if valid_expenses_for_download:
            df_download = pd.DataFrame(valid_expenses_for_download)
            csv_data = df_download.to_csv(index=False).encode('utf-8')
            download_filename = st.text_input("Enter desired filename (e.g., my_expenses.csv)", value="my_expenses.csv")

            st.download_button(
                label="Download Expenses CSV",
                data=csv_data,
                file_name=download_filename,
                mime="text/csv",
                help="Click to download your expenses as a CSV file to your computer."
            )
        else:
            st.info("No valid expenses to download yet.")


    # --- Initial load message (Optional, for first run) ---
    if not st.session_state.expenses and menu_selection != "Add Expense":
        st.info("Welcome! Start by adding your expenses in the 'Add Expense' section.")

if __name__ == "__main__":
    main()
