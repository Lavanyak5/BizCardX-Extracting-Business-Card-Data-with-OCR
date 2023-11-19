# BizCardX-Extracting-Business-Card-Data-with-OCR


In this project we are tasked with developing a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.The extracted information should include the company name, card holder,name, designation, mobile number, email address, website URL, area, city, state,and pin code. The extracted information should then be displayed in the application's graphical user interface (GUI).

OCR :
    Optical character recognition, or OCR, defines the process of mechanically or electronically converting scanned images of handwritten, typed or printed text into machine-encoded text.


Necessary libraries:
  import streamlit as st
  from streamlit_option_menu import option_menu
  import pandas as pd
  import numpy as np
  import mysql.connector as sql
  import re
  import easyocr
  from PIL import Image
  import io


  This project will require skills in image processing, OCR, GUI development, and database management. It will also help you to carefully design and plan the application architecture to ensure that its scalable,maintainable, and extensible. This will allow the users to view the data in the table format and we will be able to modify the data.

  
