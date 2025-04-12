import os
import pandas as pd
from bs4 import BeautifulSoup
import re

def extract_financial_tables(file_path, output_dir="financial_tables_aapl"):
    """
    Extract and save only the key financial tables (balance sheet, income statement, cash flow)
    from an XBRL/HTML document.
    
    Args:
        file_path (str): Path to the XBRL/HTML file
        output_dir (str): Directory to save the CSV files
        
    Returns:
        dict: Dictionary of financial DataFrames with table identifiers as keys
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables in the document")
    
    # Dictionary to store financial DataFrames
    financials = {}
    
    # Process each table
    for i, table in enumerate(tables):
        try:
            # Generate a table identifier
            # Try to find a caption or a title for better identification
            caption = table.find('caption')
            title_element = table.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5'] and tag.text.strip())
            
            if caption and caption.text.strip():
                table_id = f"table_{i}_{clean_title(caption.text.strip())}"
            elif title_element and title_element.text.strip():
                table_id = f"table_{i}_{clean_title(title_element.text.strip())}"
            else:
                # Try to find nearby headings
                prev_heading = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5'])
                if prev_heading and prev_heading.text.strip():
                    table_id = f"table_{i}_{clean_title(prev_heading.text.strip())}"
                else:
                    table_id = f"table_{i}"
            
            # Parse the table into a pandas DataFrame
            df = parse_table_to_dataframe(table)
            
            # Skip empty tables and very small tables (likely not financial statements)
            if df.empty or (df.shape[0] < 5 and df.shape[1] < 3):
                continue
                
            # Convert DataFrame to string for keyword search
            df_text = df.to_string().lower()
            
            # Check for specific financial tables using key phrases
            if "total liabilities and shareholders' equity" in df_text:
                financials["balance_sheet"] = df
                print(f"FOUND BALANCE SHEET: {table_id}")
            elif "cash and cash equivalents at end of period" in df_text:
                financials["cash_flow_statement"] = df
                print(f"FOUND CASH FLOWS: {table_id}")
            elif "total operating expenses" in df_text and "net income per share" in df_text:
                financials["income_statement"] = df
                print(f"FOUND INCOME STATEMENT: {table_id}")
                
        except Exception as e:
            print(f"Error parsing table {i}: {str(e)}")
    
    # Create output directory if specified and financials found
    if output_dir and financials:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each financial table as CSV
        for table_name, df in financials.items():
            csv_path = os.path.join(output_dir, f"{table_name}.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved: {csv_path}")
    
    # Print summary of found financial tables
    print(f"\nFound {len(financials)} financial tables:")
    for table_name in financials.keys():
        print(f"- {table_name}")
    
    return financials

def clean_title(title):
    """Clean a title string to make it suitable for a filename or dict key"""
    # Replace multiple spaces with a single underscore
    title = re.sub(r'\s+', '_', title)
    # Remove special characters
    title = re.sub(r'[^\w]', '', title)
    # Truncate long titles
    return title[:50].lower()

def parse_table_to_dataframe(table):
    """
    Parse an HTML table into a pandas DataFrame.
    
    Args:
        table (bs4.element.Tag): BeautifulSoup table element
        
    Returns:
        pandas.DataFrame: DataFrame containing the table data
    """
    # Extract headers
    headers = []
    header_row = table.find('tr')
    
    # If there's a thead, use it for headers
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
    
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
    
    # Extract rows
    rows = []
    tbody = table.find('tbody')
    if tbody:
        # If tbody exists, get rows from there
        table_rows = tbody.find_all('tr')
    else:
        # Otherwise get all rows and skip the header if it exists
        table_rows = table.find_all('tr')
        if headers and len(table_rows) > 0:
            table_rows = table_rows[1:]
    
    for row in table_rows:
        cells = [td.text.strip() for td in row.find_all(['td', 'th'])]
        if cells:  # Skip empty rows
            rows.append(cells)
    
    # Create DataFrame
    if headers and rows:
        # Make sure all rows have the same length as headers
        for i, row in enumerate(rows):
            if len(row) < len(headers):
                # Pad with empty strings
                rows[i] = row + [''] * (len(headers) - len(row))
            elif len(row) > len(headers):
                # Truncate
                rows[i] = row[:len(headers)]
                
        df = pd.DataFrame(rows, columns=headers)
    elif rows:
        # No headers, use generic column names
        max_cols = max(len(row) for row in rows)
        cols = [f'Column_{i}' for i in range(max_cols)]
        
        # Ensure all rows have the same length
        for i, row in enumerate(rows):
            if len(row) < max_cols:
                rows[i] = row + [''] * (max_cols - len(row))
                
        df = pd.DataFrame(rows, columns=cols)
    else:
        # Empty table
        df = pd.DataFrame()
    
    return df

# Example usage
if __name__ == "__main__":
    # Path to the XBRL file
    # file_path = "../filings/sec-edgar-filings/NVDA/10-K/0001045810-25-000023/nvda_primary-document.html"
    file_path = "../filings/sec-edgar-filings/AAPL/10-K/0000320193-24-000123/primary-document.html"
    
    # Extract and save financial tables
    financial_tables = extract_financial_tables(file_path)
    
    # Display the found tables
    for table_name, df in financial_tables.items():
        print(f"\n{table_name.upper()}:")
        print(df.head())