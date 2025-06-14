import streamlit as st
import pandas as pd
import socket
import smtplib
import requests
from email.message import EmailMessage
from PIL import Image
import fitz
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
import io
import base64
from reportlab.lib.pagesizes import letter
from servertest import getAllPrice
from servertest import updateAll
from servertest import getAllTicket
from servertest import getDesc
from servertest import getBinddes
from servertest import inventory_Part
from servertest import inventory_Item
from servertest import getPartsPrice
from servertest import getBranch
from servertest import getParent
from servertest import getParentByTicket
from datetime import datetime
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph
import numpy as np
import re
import json
from reportlab.graphics.renderPM import PMCanvas
from decimal import Decimal
import os
from twilio.rest import Client
# ["+19046767222","+13213770708"]

def notify_it_on_error(ip_address, user_input):
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("account_sid")
        auth_token = os.environ.get("auth_token")
        from_number = os.environ.get("twilio_from") 
        to_numbers = os.environ.get("twilio_to")

        client = Client(account_sid, auth_token)

        message_body = (
            f"⚠️ Inventory Search Failed.\n"
            f"IP: {ip_address}\n"
            f"Input: {user_input}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        to_numbers = json.loads(to_numbers)

        # Send SMS to each recipient
        for to_number in to_numbers:
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )
            print(f"SMS sent to {to_number}")

    except Exception as sms_error:
        print(f"SMS failed to send: {sms_error}")


current_date = datetime.now()
formatted_date = current_date.strftime("%m/%d/%Y")
if "ticketN" not in st.session_state:
    st.session_state.ticketN = None
if "pricingDf" not in st.session_state:
    st.session_state.pricingDf = None
if "pricingCol" not in st.session_state:
    st.session_state.pricingCol = None
if "partsDF" not in st.session_state:
    st.session_state.partsDF = None
if "ticketDf" not in st.session_state:
    st.session_state.ticketDf = None
if "TRatesDf" not in st.session_state:
    st.session_state.TRatesDf = None
if "LRatesDf" not in st.session_state:
    st.session_state.LRatesDf = None
if "misc_ops_df" not in st.session_state:
    st.session_state.misc_ops_df = None
if "edit" not in st.session_state:
    st.session_state.edit = None
if "workDescription" not in st.session_state:
    st.session_state.workDescription = ""
if "NTE_Quote" not in st.session_state:
    st.session_state.NTE_Quote = ""
if "editable" not in st.session_state:
    st.session_state.editable = None
if "refresh_button" not in st.session_state:
    st.session_state.refresh_button = None
if "workDesDf" not in st.session_state:
    st.session_state.workDesDf = None
if "selected_rows" not in st.session_state:
    st.session_state.selected_rows = None
if 'selected_branches' not in st.session_state:
    st.session_state.selected_branches = []
if 'prev_input_letters' not in st.session_state:
    st.session_state.prev_input_letters = ""
if 'previnputParts' not in st.session_state:
    st.session_state.previnputParts = ""
# if "branch" not in st.session_state:
#     st.session_state.branch = getBranch()
# if "parentDf" not in st.session_state:
#     st.session_state.parentDf = getBranch()
if 'expand_collapse_state' not in st.session_state:
    st.session_state.expand_collapse_state = True
# if 'filtered_ticket' not in st.session_state:
#     st.session_state.filtered_ticket = [event for event in st.session_state.filtered_ticket if event['BranchShortName'] in st.session_state.selected_branches]

def inventoryPage():
    st.error("Union is a SQL key word please input itemNMBR directly for all union related search, maxchar is 30 characters")
    if st.session_state.selected_rows is None or len(st.session_state.selected_rows) == 0:
        st.session_state.input_letters = st.text_input("First enter Part Id or Parts Desc:", max_chars=30, key="ItemDES").upper()
        
        if st.session_state.input_letters != st.session_state.prev_input_letters and len(st.session_state.input_letters) > 0:
            try:
                st.session_state.pricingDf, st.session_state.pricingCol = inventory_Part(st.session_state.input_letters)
            except Exception as e:
                st.error("Search failed: text provided invalid")

                # Get user IP (if possible; fallback to hostname IP)
                try:
                    ip_address = requests.get("https://api.ipify.org").text
                except:
                    ip_address = socket.gethostbyname(socket.gethostname())

                notify_it_on_error(ip_address, st.session_state.input_letters)
                return

            st.session_state.prev_input_letters = st.session_state.input_letters

        if st.session_state.pricingDf is not None and st.session_state.pricingDf.empty:
            st.error("Please enter a valid Part Desc.")
        elif st.session_state.pricingDf is not None:
            df = pd.DataFrame(st.session_state.pricingDf)
            gb = GridOptionsBuilder.from_dataframe(df[st.session_state.pricingCol])
            gb.configure_selection(selection_mode="single")
            gb.configure_side_bar()
            gridOptions = gb.build()

            data = AgGrid(df,
                        gridOptions=gridOptions,
                        enable_enterprise_modules=True,
                        allow_unsafe_jscode=True,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            st.session_state.selected_rows = data["selected_rows"]
            if len(st.session_state.selected_rows) != 0:
                st.table(st.session_state.selected_rows)
                st.experimental_rerun()
    else:
        if len(st.session_state.selected_rows) != 0:
            # st.table(st.session_state.selected_rows)
            st.session_state.partsDF = inventory_Item(st.session_state.selected_rows[0]["ITEMNMBR"])
            
            if(len(st.session_state.partsDF) == 0):
                st.write("no parts available/ contact parts department")
            else:
                df = st.session_state.partsDF.drop('ITEMDESC', axis=1)
                # st.session_state.partsDF['QTY'] = st.session_state.partsDF['QTY'].apply(lambda x: f'{x:,.2f}' if isinstance(x, (int, float)) else str(x))
            
                gb = GridOptionsBuilder.from_dataframe(df[["ITEMNMBR", "QTY", "Location"]])
                gb.configure_selection(selection_mode="single")
                gb.configure_side_bar()
                gridOptions = gb.build()

                data = AgGrid(df,
                            gridOptions=gridOptions,
                            enable_enterprise_modules=True,
                            allow_unsafe_jscode=True,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    # st.write("Search by the Item Number")
    # st.session_state.inputParts = st.text_input("Second enter ITEM Number:", max_chars=15, key="itemID").upper()
    # if st.session_state.inputParts != st.session_state.previnputParts and len(st.session_state.input_letters) > 0:
    #     st.session_state.partsDF = inventory_Item(st.session_state.inputParts.strip())
    #     st.session_state.previnputParts = st.session_state.inputParts
    # if st.session_state.partsDF is not None and st.session_state.partsDF.empty:
    #     st.error("Please enter a valid Part Desc.")
    # elif st.session_state.partsDF is not None:
    #     with st.expander("Item Description", expanded=True):
    #         st.session_state.partsDF['QTY'] = st.session_state.partsDF['QTY'].apply(lambda x: f'{x:,.2f}' if isinstance(x, (int, float)) else str(x))
    #         st.table(st.session_state.partsDF)

def main():
    st.set_page_config("Inventory Search", layout="wide")
    inventoryPage()
if __name__ == "__main__":
    main()