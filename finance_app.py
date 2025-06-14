from typing import TextIO

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title='Finance Operandi', page_icon="💰", layout='wide')

category_file = "categories.json"

if 'categories' not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists(category_file):
    with open(category_file, 'r') as f:
        st.session_state.categories = json.load(f)

def save_categorises():
    with open(category_file, 'w') as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        # default all items to uncategorized if not in keywords
        if category == "Uncategorized" or not keywords:
            continue

        # convert all keywords into lowercase and remove whitespaces
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        # loop through every row in df
        for idx, row in df.iterrows():
            # retrieve transaction description
            description = row["Description"].lower().strip()
            # check if description match any category
            if description in lowered_keywords:
                # update category of that particular row
                df.at[idx, "Category"] = category
    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce')
        df['Credit'] = df['Credit'].fillna(0)
        df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='%d/%m/%Y')
        # st.write(df)
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categorises()
        return True
    return False

def main():
    st.title("Finance Dashboard")

    uploaded_file = st.file_uploader("Upload transaction CSV file", type=['csv'])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df.copy().drop('Credit', axis='columns').drop('Transaction Number', axis='columns')
            credits_df = df.copy().drop('Debit', axis='columns').drop('Transaction Number', axis='columns')

            st.session_state.debits_df = debits_df.copy()

            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categorises()
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[['Transaction Date', 'Description', 'Debit', 'Running Balance', 'Category']],
                    column_config={
                        "Transaction Date": st.column_config.DateColumn("Date", format = "DD/MM/YYYY"),
                        "Debit": st.column_config.NumberColumn("Debit"),
                        "Running Balance": st.column_config.NumberColumn("Running Balance"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )

                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    # loop through edited dataframe
                    for idx, row in edited_df.iterrows():
                        new_category = row['Category']
                        # if new_category already exists, nothing to do, continue
                        if new_category == st.session_state.debits_df.at[idx, "Category"]:
                            continue
                        # get the description
                        description = row["Description"]
                        # add the df
                        st.session_state.debits_df.at[idx, "Category"] = new_category
                        # call function and to save to json file
                        add_keyword_to_category(new_category, description)

                st.subheader('Expense Summary')
                category_totals = st.session_state.debits_df.groupby("Category")["Debit"].sum().reset_index()
                category_totals = category_totals.sort_values("Debit", ascending=False)

                st.dataframe(
                    category_totals,
                    column_config={
                        "Debit": st.column_config.NumberColumn("Debit", format = "%.2 KYD")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                fig = px.pie(
                    category_totals,
                    values = 'Debit',
                    names = 'Category',
                    title = 'Expenses by Category'
                )

                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Income Summary")
                total_payments = credits_df["Credit"].sum()
                st.metric("Total Income", f"{total_payments:,.2f} KYD")
                st.write(credits_df)
main()