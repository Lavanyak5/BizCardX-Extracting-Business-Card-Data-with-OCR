import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import mysql.connector as sql
import re
import easyocr
from PIL import Image
import io


st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR </h1>", unsafe_allow_html=True)

#option menu
with st.sidebar:
    selected = option_menu(
    menu_title=None,
    options=["Home", "Upload Business Card","Data Modify"],
    icons=["house","file-earmark","list"],
    default_index=0,
#    orientation="horizontal"
)

# Home Page Data 

if selected == "Home":
    st.write(" ")
    st.title(" :violet[About BizcardX:]")
    st.markdown("BizCardX is a Streamlit web application designed to effortlessly extract data from business cards using Optical Character Recognition (OCR) technology. With BizCardX, users can easily upload images of business cards, and the application leverages the powerful easyOCR library to extract pertinent information from the cards. The extracted data is then presented in a user-friendly format and can be stored in a MySQL database for future reference and management.")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.title(" :violet[Overview:]")
    st.markdown("In this app you will be able to see a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.")


# Creating connection with mysql Database
mydb = sql.connect(host="localhost",
                   user="root",
                   password="12345",
                   database= "BizCardX"
                  )
mycursor = mydb.cursor(buffered=True)
mycursor.execute("CREATE DATABASE IF NOT EXISTS BizCardX")
mycursor.execute("create table  IF NOT EXISTS Bizcard_data (Name varchar(100), Designation varchar(100), Mobile_number varchar(50), email_address varchar(100), website_URL varchar(250), Address varchar(100), State varchar(100),Pincode varchar(30),CompanyName varchar(100))")


if selected == "Upload Business Card":
    image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'])

    def extract_data(Picture):
        ext_dict = {'Name':[],'Designation':[],'Mobile_number':[],'email_address':[],'website_URL':[],'Address':[],'State':[],'Pincode':[],'CompanyName':[]}
        ext_dict['Name'].append(result[0])
        ext_dict['Designation'].append(result[1])
    
        for a in range(2,len(result)):
        
            if (result[a].startswith('+') or (re.sub(r'[+-]','',result[a]).isdigit())) and len(result[a]) > 6:
                ext_dict['Mobile_number'].append(result[a])
        
            elif '@' in result[a] and '.com' in result[a]:
                s = result[a].lower()
                ext_dict['email_address'].append(s)
        
            elif 'www' in result[a] or 'WWW' in result[a] or '.com' in result[a]:
                small = result[a].lower()
                ext_dict['website_URL'].append(small)
        
            elif 'TamilNadu'in result[a] or 'Tamil Nadu' in result[a]:
                
                removed_colon = re.sub(r'[,;]','',result[a])
                
               # st.write(removed_colon)
                
                if 'TamilNadu' in result[a]:
                    addr = removed_colon.split('TamilNadu')
                    #st.write(addr)
                elif 'Tamil Nadu' in result[a]:
                    addr = removed_colon.split('Tamil Nadu')
                    #st.write(addr)
                    
                ext_dict['Address'].append(addr[0])
                    
                ext_dict['State'].append('Tamil Nadu') # Golmal
                
                n1 = re.findall(r'\d+', result[a])
                n2 = str(n1[0])
                ext_dict['Pincode'].append(n2)
                        
            elif re.match(r'^[A-Za-z]',result[a]):
                if "," in result[a]:
                    removed_colon2 = re.sub(r'[,;]','',result[a])
                    ext_dict['Address'].append(removed_colon2)                
                else:
                    ext_dict['CompanyName'].append(result[a])
            
            else:
                if len(result[a]) == 6 and result[a].isdigit():
                    ext_dict['Pincode'].pop(0)
                    ext_dict['Pincode'].append(result[a])
                else:
                    removed_colon3 = re.sub(r'[,;]','',result[a])
                    ext_dict['Address'].append(removed_colon3)
                 
        for key,value in ext_dict.items():
            if len(value) > 0:
                concatened_string = ' '.join(value)
                ext_dict[key] = [concatened_string]
            else :
                value = 'NA'
                ext_dict[key] = [value]
        return ext_dict
    
    
    # INITIALIZING THE EasyOCR READER
    @st.cache_data
    def load_image():
        reader = easyocr.Reader(['en'], model_storage_directory=".")
        return reader


    reader_1 = load_image()
    if image is not None:
        input_image = Image.open(image)
        # Setting Image size
        st.image(input_image, width=350, caption='Uploaded Image')
#            f'<style>.css-1aumxhk img {{ max-width: 300px; }}</style>',
        #    unsafe_allow_html=True
       # )

        result = reader_1.readtext(np.array(input_image), detail=0)#, paragraph= True)
        #st.write(result)
        
    # creating dataframe
        ext_text = extract_data(result)
        df = pd.DataFrame(ext_text)
        st.dataframe(df)
            # Converting image into bytes
        image_bytes = io.BytesIO()
        input_image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
            #Creating dictionary
        data = {"Image": [image_data]}
        df_1 = pd.DataFrame(data)
        concat_df = pd.concat([df, df_1], axis=1)
    
    if st.button("Upload to Database"):
        for i,row in df.iterrows():
                # here %S means string values
            sql_stmt = """INSERT INTO bizcard_data(Name,Designation,Mobile_number,email_address,website_URL,Address,State,Pincode,CompanyName)
                                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            mycursor.execute(sql_stmt, tuple(row))
            mydb.commit()
            st.success("#### Uploaded to database successfully!")
		
if selected == "Data Modify":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alteration or Deletion of the data")
    column1,column2 = st.columns(2,gap="small")
    try:
        with column1:
            mycursor.execute("SELECT Name FROM Bizcard_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown(":violet[Update or modify any data below]")
            mycursor.execute("select Name,Designation,Mobile_number,email_address,website_URL,Address,State,Pincode,CompanyName from Bizcard_data WHERE Name=%s",
                            (selected_card,))
            result = mycursor.fetchone()
            
            #Displaying all the information
            Name = st.text_input("Name", result[0])
            Designation = st.text_input("Designation", result[1])
            Mobile_number = st.text_input("Mobile_number", result[2])
            email_address = st.text_input("email_address", result[3])
            website = st.text_input("website_URL", result[4])
            Address = st.text_input("Address", result[5])
            State = st.text_input("State", result[6])
            Pincode = st.text_input("Pincode", result[7])
            CompanyName = st.text_input("CompanyName", result[8])
            
            if st.button("Update changes to DB"):
                #st.write(selected_card)
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE Bizcard_data SET Name = %s, Designation = %s, Mobile_number = %s, email_address = %s,
                    website_URL = %s, Address = %s, State = %s, Pincode = %s, CompanyName = %s
                    WHERE Name=%s""",
                    (Name,Designation,Mobile_number,email_address,website,Address,State,Pincode,CompanyName, selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")
                
    except:
       st.warning("There is no data available in the database") 

    if st.button("View updated data"):
        mycursor.execute("""select Name,Designation,Mobile_number,email_address,website_URL,Address,State,Pincode,CompanyName from Bizcard_data WHERE name = %s""",(selected_card,))
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Name","Designation","Mobile_number","email_address","website_URL","Address","State","Pincode","CompanyName"])
        st.write(updated_df)
        
    with column2:
        mycursor.execute("SELECT Name FROM Bizcard_data")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
        st.write(f"### You have selected [**{selected_card}'s**] card to delete")
        st.write("#### Proceed to delete this card?")

        if st.button("Yes Delete Business Card"):
            mycursor.execute(f"DELETE FROM Bizcard_data WHERE Name='{selected_card}'")
            mydb.commit()
            st.success("Business card information deleted from database.")

        

# Close the database connection
mycursor.close()
