import pandas as pd
import pyodbc
import json
import os
import re

server = os.environ.get("serverGFT")
database = os.environ.get("databaseGFT")
username = os.environ.get("usernameINVGFT")
password = os.environ.get("passwordINVGFT")
username = os.environ.get("usernameINVGFT")
password = os.environ.get("passwordINVGFT")
SQLaddress = os.environ.get("addressGFT")

parameter_value = "230524-0173"

SQL_INJECTION_PATTERNS = re.compile(
    r"""(?ix)           # Case-insensitive, verbose
    (?:--|;|/\*|\*/|     # SQL meta-characters
    ['"]|                # Quotes
    \b(exec|drop|delete|insert|update|select|union|sleep|benchmark|xp_|sp_)\b)
    """
)

def sanitize_input(value):
    """
    Recursively sanitize input against SQL injection attempts.
    Raises ValueError if suspicious content is detected.
    """
    if isinstance(value, str):
        if SQL_INJECTION_PATTERNS.search(value):
            raise ValueError(f"Potential SQL injection detected in input: {value}")
        return value

    elif isinstance(value, (list, tuple)):
        return [sanitize_input(v) for v in value]

    elif isinstance(value, dict):
        return {k: sanitize_input(v) for k, v in value.items()}

    elif isinstance(value, (int, float, bool)) or value is None:
        return value

    else:
        raise TypeError(f"Unsupported input type for SQL sanitization: {type(value)}")
        
def inventory_Part(user_input):
    user_input = sanitize_input(user_input)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Stored procedure expects @Search, not @SearchPattern
    sql_query = "EXEC [CF_PART_LOOK_UP] @Search = ?"
    search_pattern = f"%{user_input}%"  # Add LIKE wildcards
    cursor.execute(sql_query, (search_pattern,))  # Pass parameter safely

    # Stored procedure expects @Search, not @SearchPattern
    sql_query = "EXEC [CF_PART_LOOK_UP] @Search = ?"
    search_pattern = f"%{user_input}%"  # Add LIKE wildcards
    cursor.execute(sql_query, (search_pattern,))  # Pass parameter safely

    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    if not rows:
        return pd.DataFrame(), columns

    if not rows:
        return pd.DataFrame(), columns

    columns_transposed = list(zip(*rows))
    data = {col: col_data for col, col_data in zip(columns, columns_transposed)}
    partNameDf = pd.DataFrame(data)

    cursor.close()
    conn.close()
    return partNameDf, columns

def inventory_Item(input):
    input = sanitize_input(input)
    input = sanitize_input(input)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        sql_query = f"""EXEC [CF_PART_Search] '{input}';"""
        cursor.execute(sql_query)
        sql_query = cursor.fetchall()
        rows_transposed = [sql_query for sql_query in zip(*sql_query)]
        partNameDf = pd.DataFrame(dict(zip(['ITEMNMBR', 'ITEMDESC', "Location", "QTY"], rows_transposed)))
        return partNameDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        sql_query = f"""EXEC [CF_PART_Search] '{input}';"""
        cursor.execute(sql_query)
        sql_query = cursor.fetchall()
        rows_transposed = [sql_query for sql_query in zip(*sql_query)]
        partNameDf = pd.DataFrame(dict(zip(['ITEMNMBR', 'ITEMDESC', "Location", "QTY"], rows_transposed)))
        return partNameDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getBinddes(input):
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        sql_query = """Exec [CF_PART_LOOK_UP_streamlit] @Search = ?;"""
        cursor.execute(sql_query, input)
        sql_query = cursor.fetchall()
        rows_transposed = [sql_query for sql_query in zip(*sql_query)]
        partNameDf = pd.DataFrame(dict(zip(['ITEMNMBR', 'ITEMDESC'], rows_transposed)))
        return partNameDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        sql_query = """Exec [CF_PART_LOOK_UP_streamlit] @Search = ?;"""
        cursor.execute(sql_query, input)
        sql_query = cursor.fetchall()
        rows_transposed = [sql_query for sql_query in zip(*sql_query)]
        partNameDf = pd.DataFrame(dict(zip(['ITEMNMBR', 'ITEMDESC'], rows_transposed)))
        return partNameDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getPartsPrice(partInfoDf):
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        pricingDf = pd.DataFrame(columns=['ITEMNMBR', 'ITEMDESC', 'SellingPrice'])
        for index, row in partInfoDf.iterrows():
            item_num = row['ITEMNMBR']
            customer_num = row['Bill_Customer_Number']
            sql_query = """Exec [CF_Univ_Quote_Pricing_streamlit] @ItemNum = ?, @CUSTNMBR = ?;"""
            cursor.execute(sql_query, item_num, customer_num)
            result = cursor.fetchall()
            row_dict = {
                'ITEMNMBR': item_num,
                'ITEMDESC': "no Info",
                'SellingPrice': 0
            }
            if result:
                row_dict = {
                    'ITEMNMBR': result[0][0],
                    'ITEMDESC': result[0][1],
                    'SellingPrice': result[0][2]
                }
            pricingDf = pricingDf.append(row_dict, ignore_index=True)
        return pricingDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        pricingDf = pd.DataFrame(columns=['ITEMNMBR', 'ITEMDESC', 'SellingPrice'])
        for index, row in partInfoDf.iterrows():
            item_num = row['ITEMNMBR']
            customer_num = row['Bill_Customer_Number']
            sql_query = """Exec [CF_Univ_Quote_Pricing_streamlit] @ItemNum = ?, @CUSTNMBR = ?;"""
            cursor.execute(sql_query, item_num, customer_num)
            result = cursor.fetchall()
            row_dict = {
                'ITEMNMBR': item_num,
                'ITEMDESC': "no Info",
                'SellingPrice': 0
            }
            if result:
                row_dict = {
                    'ITEMNMBR': result[0][0],
                    'ITEMDESC': result[0][1],
                    'SellingPrice': result[0][2]
                }
            pricingDf = pricingDf.append(row_dict, ignore_index=True)
        return pricingDf
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getAllPrice(ticketN):
    ticketN = sanitize_input(ticketN)
    ticketN = sanitize_input(ticketN)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    sql_query = """Exec [CF_Univ_Quote_Ticket] @Service_TK = ?;"""
    cursor.execute(sql_query, ticketN)
    sql_query = cursor.fetchall()
    rows_transposed = [sql_query for sql_query in zip(*sql_query)]
    ticketDf = pd.DataFrame(dict(zip(["LOC_Address", "LOC_CUSTNMBR", "LOC_LOCATNNM", "LOC_ADRSCODE", "LOC_CUSTNAME", "LOC_PHONE", "CITY", "STATE", "ZIP", "Pricing_Matrix_Name", "BranchName", "CUST_NAME", "CUST_ADDRESS1", "CUST_ADDRESS2", "CUST_ADDRESS3", "CUST_CITY", "CUST_State", "CUST_Zip", "Tax_Rate", "MailDispatch", "Purchase_Order", "Bill_Customer_Number"], rows_transposed)))
    sql_query = """Exec [CF_Univ_Quote_LRates] @Service_TK = ?;"""
    cursor.execute(sql_query, ticketN)
    sql_query = cursor.fetchall()
    rows_transposed = [sql_query for sql_query in zip(*sql_query)]
    LRatesDf = pd.DataFrame(dict(zip(["Billing_Amount", "Pay_Code_Description"], rows_transposed)))
    
    sql_query = """Exec [CF_Univ_Quote_TRates] @Service_TK = ?;"""
    cursor.execute(sql_query, ticketN)
    sql_query = cursor.fetchall()
    rows_transposed = [sql_query for sql_query in zip(*sql_query)]
    TRatesDf = pd.DataFrame(dict(zip([
    "Billing_Amount", "Pay_Code_Description"], rows_transposed)))

    sql_query = """Exec [CF_Univ_Quote_Fees] @Service_TK = ?;"""
    cursor.execute(sql_query, ticketN)
    sql_query = cursor.fetchall()
    rows_transposed = [sql_query for sql_query in zip(*sql_query)]
    misc_ops_df = pd.DataFrame(dict(zip([
    "Fee_Charge_Type", "Fee_Amount"], rows_transposed)))
    cursor.close()
    conn.close()
    return ticketDf, LRatesDf, TRatesDf, misc_ops_df


def getDesc(ticket):
    ticketN = sanitize_input(ticketN)
    ticketN = sanitize_input(ticketN)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    select_query = "Exec CF_Univ_GetWorkDescription @TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    cursor.close()
    conn.close()
    data = [list(row) for row in dataset]
    workDes = pd.DataFrame(data, columns=["Incurred", "Proposed"])
    return workDes
    
    
def getAllTicket(ticket):
    ticketN = sanitize_input(ticketN)
    ticketN = sanitize_input(ticketN)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    select_query = "Exec CF_Univ_GetWorkLabor @TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]

    ticketLaborDf = pd.DataFrame(data, columns=["Incurred/Proposed", "Description", "Nums of Techs", "Hours per Tech", "QTY", "Hourly Rate", "EXTENDED"])
    columns_to_round = ["Hourly Rate", "Hours per Tech", "EXTENDED"] 
    for column in columns_to_round:
        ticketLaborDf[column] = pd.to_numeric(ticketLaborDf[column]).round(2)
    # print(ticketLaborDf)
    select_query = "Exec CF_Univ_GetTravelLabor @TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    ticketTripDf = pd.DataFrame(data, columns=["Incurred/Proposed", "Description", "QTY", "UNIT Price", "EXTENDED"])

    select_query = "Exec CF_Univ_GetParts @TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    ticketPartsDf = pd.DataFrame(data, columns=["Incurred/Proposed", "Description", "QTY", "UNIT Price", "EXTENDED"])

    select_query = "Exec CF_Univ_GetMiscCharge @TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    ticketMiscDf = pd.DataFrame(data, columns=["Description", "QTY", "UNIT Price", "EXTENDED"])

    select_query = "SELECT Description, QTY, CAST([UNIT_Price] AS FLOAT) AS [UNIT_Price], CAST(EXTENDED AS FLOAT) AS EXTENDED FROM [CF_Universal_materials_rentals_insert] WHERE TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    ticketMaterialsDf = pd.DataFrame(data, columns=["Description", "QTY", "UNIT Price", "EXTENDED"])

    select_query = "SELECT Description, QTY, CAST([UNIT_Price] AS FLOAT) AS [UNIT_Price], CAST(EXTENDED AS FLOAT) AS EXTENDED FROM [CF_Universal_subcontractor_insert] WHERE TicketID = ?"
    cursor.execute(select_query, (ticket,))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    ticketSubDf = pd.DataFrame(data, columns=["Description", "QTY", "UNIT Price", "EXTENDED"])

    cursor.close()
    conn.close()
    columns_to_round = ["QTY", "UNIT Price", "EXTENDED"] 
    for df in [ticketTripDf, ticketPartsDf, ticketMiscDf, ticketMaterialsDf, ticketSubDf]:
        for column in columns_to_round:
            df[column] = pd.to_numeric(df[column]).round(2)
    return ticketLaborDf, ticketTripDf, ticketPartsDf, ticketMiscDf, ticketMaterialsDf, ticketSubDf
# getAllTicket("230215-0004")
def updateAll(ticket, incurred, proposed, laborDf,  tripDf, partsDf, miscDf, materialDf, subDf):
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    delete_query = "DELETE FROM [CF_Universal_workdescription_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()

    insert_query = "INSERT INTO [CF_Universal_workdescription_insert] (TicketID, Incurred_Workdescription, Proposed_Workdescription) VALUES (?, ?, ?)"
    insert_data = [(ticket, incurred, proposed)]
    cursor.executemany(insert_query, insert_data)
    conn.commit()

    delete_query = "DELETE FROM [CF_Universal_labor_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()

    laborDf = laborDf.dropna()
    data = laborDf[["Incurred/Proposed","Description", "Nums of Techs", "Hours per Tech", "QTY", "Hourly Rate", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data]
    insert_query = "INSERT INTO [CF_Universal_labor_insert] (Incurred, Description, Nums_of_Techs, Hours_per_Tech, QTY, Hourly_Rate, EXTENDED, TicketID) VALUES (?,?,?,?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()

    delete_query = "DELETE FROM [CF_Universal_trip_charge_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()

    tripDf = tripDf.dropna()
    data = tripDf[["Incurred/Proposed","Description", "QTY", "UNIT Price", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data]
    insert_query = "INSERT INTO [CF_Universal_trip_charge_insert] (Incurred, Description, QTY, UNIT_Price, EXTENDED, TicketID) VALUES (?,?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()

    delete_query = "DELETE FROM [CF_Universal_parts_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()
    partsDf = partsDf.dropna()
    data = partsDf[["Incurred/Proposed","Description", "QTY", "UNIT Price", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data if all(x is not None for x in row)]
    insert_query = "INSERT INTO [CF_Universal_parts_insert] (Incurred, Description, QTY, UNIT_Price, EXTENDED, TicketID) VALUES (?,?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()

    
    delete_query = "DELETE FROM [CF_Universal_misc_charge_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()
    miscDf = miscDf.dropna()
    data = miscDf[["Description", "QTY", "UNIT Price", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data if all(x is not None for x in row)]
    insert_query = "INSERT INTO [CF_Universal_misc_charge_insert] (Description, QTY, UNIT_Price, EXTENDED, TicketID) VALUES (?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()
    
    delete_query = "DELETE FROM [CF_Universal_materials_rentals_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()
    materialDf = materialDf.dropna()
    data = materialDf[["Description", "QTY", "UNIT Price", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data if all(x is not None for x in row)]
    insert_query = "INSERT INTO [CF_Universal_materials_rentals_insert] (Description, QTY, UNIT_Price, EXTENDED, TicketID) VALUES (?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()
    
    delete_query = "DELETE FROM [CF_Universal_subcontractor_insert] WHERE TicketID = ?"
    cursor.execute(delete_query, (ticket,))
    conn.commit()
    subDf = subDf.dropna()
    data = subDf[["Description", "QTY", "UNIT Price", "EXTENDED"]].values.tolist()
    data = [row + [ticket] for row in data if all(x is not None for x in row)]
    insert_query = "INSERT INTO [CF_Universal_subcontractor_insert] (Description, QTY, UNIT_Price, EXTENDED, TicketID) VALUES (?,?,?,?,?)"
    if data:
        cursor.executemany(insert_query, data)
    conn.commit()

def getBranch():
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    sql_query = '''
        SELECT DISTINCT RTrim(Wennsoft_Branch) as Wennsoft_Branch , Rtrim(BranchName) as BranchName FROM [dbo].[GFT_SV00077_Ext]
        WHERE Wennsoft_Branch <> 'Pensacola' AND BranchName NOT IN ('Pensacola', 'Corporate', 'Guardian Connect')
        '''    
    cursor.execute(sql_query)
    result = cursor.fetchall()
    rows_transposed = [result for result in zip(*result)]
    branchDf = pd.DataFrame(dict(zip(['Wennsoft_Branch', 'BranchName'], rows_transposed)))
    cursor.close()
    conn.close()
    return branchDf

def getParentByTicket(ticket):
    ticketN = sanitize_input(ticketN)
    ticketN = sanitize_input(ticketN)
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    select_query = '''
        SELECT [TicketID]
               ,[Status]
               ,[NTE_QUOTE]
               ,[Editable]
               ,[Insertdate]
               ,[Approvedate]
               ,[Declinedate]
        FROM [GFT].[dbo].[CF_Universal_Quote_Parent]
        WHERE TicketID = ?
    '''
    cursor.execute(select_query, (ticket))
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    parentDf = pd.DataFrame(data, columns=["TicketID", "Status", "NTE_QUOTE", "Editable", "Insertdate", "Approvedate", "Declinedate"])
    conn.close()
    # ticket_prefix, ticket_number = ticket.split('-')
    # lower_bound = int(ticket_number) - 10
    # upper_bound = int(ticket_number) + 10
    # lower_ticket = f"{ticket_prefix}-{lower_bound:04d}"
    # upper_ticket = f"{ticket_prefix}-{upper_bound:04d}"
    # if parentDf.empty:
    #     start_ticket = 173 
    #     num_rows = 10
    #     data = {
    #         'TicketID': [f'230524-{str(start_ticket + i).zfill(4)}' for i in range(num_rows)],
    #         'Status': ['Open', 'Closed', 'Pending', 'Closed', 'Open', 'Pending', 'Closed', 'Open', 'Pending', 'Closed'],
    #         'NTE_QUOTE': [random.randint(0, 1) for _ in range(num_rows)],
    #         'Editable': [random.randint(0, 1) for _ in range(num_rows)],
    #         'Insertdate': [datetime(2023, 8, 15), datetime(2023, 8, 10), datetime(2023, 8, 20), datetime(2023, 8, 25),
    #                     datetime(2023, 8, 5), datetime(2023, 8, 18), datetime(2023, 8, 12), datetime(2023, 8, 22),
    #                     datetime(2023, 8, 8), datetime(2023, 8, 28)],
    #         'Approvedate': [datetime(2023, 8, 14), datetime(2023, 8, 9), datetime(2023, 8, 19), datetime(2023, 8, 24),
    #                         datetime(2023, 8, 4), datetime(2023, 8, 17), datetime(2023, 8, 11), datetime(2023, 8, 21),
    #                         datetime(2023, 8, 7), datetime(2023, 8, 27)],
    #         'Declinedate': [datetime(2023, 8, 13), datetime(2023, 8, 8), datetime(2023, 8, 18), datetime(2023, 8, 23),
    #                         datetime(2023, 8, 3), datetime(2023, 8, 16), datetime(2023, 8, 10), datetime(2023, 8, 20),
    #                         datetime(2023, 8, 6), datetime(2023, 8, 26)],
    #     }
    #     parentDf = pd.DataFrame(data)
    return parentDf
def getParent(branchName):
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    select_query = '''
       SELECT [TicketID]
            ,[Status]
            ,[NTE_QUOTE]
            ,[Editable]
            ,[Insertdate]
            ,[Approvedate]
            ,[Declinedate]
        FROM [GFT].[dbo].[CF_Universal_Quote_Parent]
        WHERE BranchName IN ({})
        ORDER BY
        COALESCE([Approvedate], [Declinedate]) DESC
        OFFSET 0 ROWS
        FETCH NEXT 10 ROWS ONLY;
    '''.format(', '.join(['?'] * len(branchName)))
    
    cursor.execute(select_query, branchName)
    dataset = cursor.fetchall()
    data = [list(row) for row in dataset]
    parentDf = pd.DataFrame(data, columns=["TicketID", "Status", "NTE_QUOTE", "Editable", "Insertdate", "Approvedate", "Declinedate"])
    mapping = {1: 'QUOTE', 3: 'NTE'}
    parentDf['NTE_QUOTE'] = parentDf['NTE_QUOTE'].replace(mapping)
    conn.close()
    return parentDf

def execute_query(query, params):
    conn_str = f"DRIVER={SQLaddress};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;"
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()