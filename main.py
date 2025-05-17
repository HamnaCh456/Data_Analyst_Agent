import os  
import streamlit as st  
import pandas as pd  
import duckdb   
import json  
from dotenv import load_dotenv  
load_dotenv()  
from groq import Groq  
api_key=os.getenv("GROQ_API_KEY") 
#api_key = "NA"  
if not api_key:  
    raise Exception("GROQ_API_KEY not loaded. Check .env file and path!")  
  
client = Groq(api_key=api_key)  
  
# Initialize session state for dataframes and query data if they don't exist  
if 'dataframes' not in st.session_state:  
    st.session_state.dataframes = {}  
if 'user_query' not in st.session_state:  
    st.session_state.user_query = ""  
if 'query_results' not in st.session_state:  
    st.session_state.query_results = None  
  
# Add a reset button to clear all data  
if st.button("Reset All Data"):  
    st.session_state.dataframes = {}  
    st.session_state.user_query = ""  
    st.session_state.query_results = None  
    st.rerun()   
  
def file_uploading():  
    st.subheader("Upload a New File")  
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])  
      
    if uploaded_file is not None:  
        # Create a temporary dataframe  
        temp_df = None  
        if uploaded_file.name.endswith('.csv'):  
            temp_df = pd.read_csv(uploaded_file)  
        elif uploaded_file.name.endswith('.xlsx'):  
            temp_df = pd.read_excel(uploaded_file)  
          
        # Show a preview of the file  
        st.write("### Data Preview:")  
        st.dataframe(temp_df)  
          
        # Get a name for this table  
        table_name = st.text_input("Enter a name for this table:")  
          
        # Add button to confirm adding this table  
        if st.button("Add Table"):  
            if table_name and temp_df is not None:  
                st.session_state.dataframes[table_name] = temp_df  
                st.success(f"Table '{table_name}' added successfully!")  
  
def display_tables():  
    st.subheader("Available Tables")  
    if st.session_state.dataframes:  
        for table_name, df in st.session_state.dataframes.items():  
            with st.expander(f"Table: {table_name}"):  
                st.dataframe(df)  
    else:  
        st.info("No tables uploaded yet.")  
  
def query_dataframe(query, table_name=None):  
    """  
    Execute a SQL query on one or more pandas DataFrames using DuckDB.  
      
    Parameters:  
        query (str): SQL query to execute  
        table_name (str or None): Optional specific table name to query  
          
    Returns:  
        pandas.DataFrame: Result of the query as a DataFrame  
    """  
    try:  
        # Create an in-memory DuckDB connection  
        conn = duckdb.connect(database=':memory:', read_only=False)  
          
        # Register all dataframes with DuckDB  
        for name, df in st.session_state.dataframes.items():  
            conn.register(name, df)  
          
        # Execute the user's query  
        result = conn.execute(query).fetchdf()  
          
        return result  
      
    finally:  
        # Close the connection  
        if 'conn' in locals():  
            conn.close()  
  
# Define tools for Groq  
tools = [  
    {  
        "type": "function",  
        "function": {  
            "name": "query_dataframe",  
            "description": "Executes a SQL query on one or more dataframes and returns the results",  
            "parameters": {  
                "type": "object",  
                "properties": {  
                    "query": {  
                        "type": "string",  
                        "description": "SQL query which is to be executed on the DataFrames",  
                    },  
                    "table_name": {  
                        "type": "string",  
                        "description": "Optional specific table name to query. If not provided, all tables will be available.",  
                    }  
                },  
                "required": ["query"],  
            },  
        },  
    }  
]  
  
# Main app flow  
st.title("Data Analyst")  
  
# File upload section  
file_uploading()  
  
# Display all tables  
display_tables()  
  
# Query section  
st.subheader("Query Your Data")  
# Use a key to ensure the widget is recreated on rerun  
user_query = st.text_input("Enter the data you want to retrieve:", key="query_input", value="")  
  
if user_query:  
    # Create a description of all available tables  
    tables_info = ""  
    for table_name, df in st.session_state.dataframes.items():  
        tables_info += f"\nTable '{table_name}' with columns: {', '.join(f'({col},{df[col].dtype})'for col in df.columns)}"  
      
    # Call Groq API  
    response = client.chat.completions.create(  
        messages=[  
            {  
                "role": "system",  
                "content": """You are an expert data analyst and SQL specialist. Generate SQL queries to solve the user's query. Use the tool 'query_dataframe' to return the result. You can query multiple tables using JOIN operations if needed.  
                            IMPORTANT SQL FORMATTING RULE:
                            !!! NEVER use backticks (`) around table or column names — this is MySQL syntax and WILL cause an error in DuckDB. !!!
                            
                            Use ONLY:
                            - Double quotes "like_this" if necessary (for names with spaces)
                            - Or plain names: column_name, table_name         
                            Remember that DuckDB follows standard SQL syntax and does not support MySQL-style backtick identifiers.  
                            """                  
            },  
            {  
                "role": "user",  
                "content":f"User Query: {user_query}. The following tables are available in the format : table_name(column_name,column_datatype):{tables_info} . Generate a SQL query to answer the user's question.",  
            }  
        ],  
        model="llama-3.3-70b-versatile",  
        tools=tools,  
        tool_choice={"type": "function", "function": {"name": "query_dataframe"}}  
    )  
      
    # Display response  
    st.write("User Query:", user_query)  
       
    # Extract the response message and any tool calls from the response  
    response_message = response.choices[0].message  
      
    # Display tool calls and the content  
    st.subheader("Response:")  
      
    # Check if there are tool calls in the response  
    if hasattr(response_message, 'tool_calls') and response_message.tool_calls:  
        for tool_call in response_message.tool_calls:  
            if tool_call.function.name == "query_dataframe":  
                # Parse arguments  
                try:  
                    args = json.loads(tool_call.function.arguments)  
                    sql_query = args.get("query")  
                    table_name = args.get("table_name")  
                      
                    # Display the SQL query  
                    st.subheader("Generated SQL Query:")  
                    st.code(sql_query, language="sql")  
                      
                    # Execute the SQL query  
                    try:  
                        results = query_dataframe(sql_query, table_name)  
                          
                        # Display results  
                        st.subheader("Query Results:")  
                        st.dataframe(results)  
                          
                        # Store results in session state  
                        st.session_state.query_results = results  
                    except Exception as e:  
                        st.error(f"Error executing SQL query: {str(e)}")  
                except json.JSONDecodeError:  
                    st.error(f"Error parsing tool call arguments: {tool_call.function.arguments}")
