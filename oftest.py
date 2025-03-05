import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Osmotic Fragility Test", layout="wide")

st.title("An Application OFify for 13 tubes OF Test")
st.header("**Hemato unit PSU**")
st.header("13 tubes OF Test Solution and Protocol")

reagent = [1,2,3,4,5,6,7,8,9,10,11,12,13]
saline_sol = [21.2,18.75,16.25,15.0,13.75,12.5,11.25,10.0,8.75,7.5,5.0,2.5,0]
water_dil = [3.8,6.25,8.75,10,11.25,12.5,13.75,15,16.25,17.5,20,22.5,25]
nacl_conc = [0.85, 0.75, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.2, 0.1, 0]

dict = {'น้ำยา':reagent,
        '1% saline solution (มล.)':saline_sol,
        'น้ำกลั่น (มล.)':water_dil,
        '% NaCl Conc':nacl_conc}
df = pd.DataFrame(dict)

with st.expander("**OF Test Solution**"):
    st.write('''น้ำยาที่ใช้:

Stock 10% saline solution
- NaCl: 90 กรัม
- Na₂HPO₄: 8.655 กรัม
- NaH₂PO₄•2H₂O: 2.43 กรัม
- เติมน้ำกลั่นให้ครบ 1,000 มล.

1% saline solution
- Stock 10% saline solution: 20 มล.
- เติมน้ำกลั่นให้ครบ 200 มล.

Working saline solution
- ใช้ volumetric flask ขนาด 25 มล. จำนวน 12 ใบ เติมส่วนผสมตามตาราง''')
    st.dataframe(df.set_index('น้ำยา').transpose())

with st.expander("**OF Test Protocol**"):
    st.write('''วิธีทำ
- เตรียมหลอดทดลองขนาด 13x100 มม. จำนวน 13 หลอด ตามตาราง หยอดแต่ละหลอดด้วย working saline solution ความเข้มข้นลดตามลำดับ หลอดละ 5 มล. เว้นหลอดหมายเลข 13 สำหรับหลอดที่ 13 ใส่น้ำกลั่น 5 มล.
- ผสมเลือดให้เข้ากันดี ใส่เลือด 50 ไมโครลิตร ลงในหลอดทุกหลอด ปิดพาราฟิล์มแล้วผสมให้เข้ากันด้วยการกลับหลอดในแนวตั้ง 5-10 ครั้ง วางไว้ที่อุณหภูมิห้องนาน 30 นาที
- เมื่อครบเวลา ผสมเลือดทุกหลอดอีกครั้ง แล้วนำไปปั่น 2000 rpm นาน 5 นาที
- นำส่วนใส (supernatant) มาวัด OD ที่ wavelength 545 nm ในสเปกโตร โดยใช้หลอดหมายเลข 1 เป็น blank และหลอดหมายเลข 13 เป็น 100% hemolysis
- คำนวณโดยใช้สูตร % hemolysis = (OD_test/OD_13) * 100
- นำค่า %hemolysis ที่ได้ มาใส่ในกราฟ (แกน Y = %NaCl แกน X = %hemolysis)
- รายงานค่าความเข้มข้นของ NaCl ที่เกิด 50% hemolysis
- ค่าปกติ %NaCl(50% hemolysis) อยู่ที่ 0.40 - 0.45%
- ตัวอย่างการทำ osmotic fragility test''')

def validate_and_convert(data):
    result = []
    for item in data:
        if item.strip() == "":  # ถ้าช่องว่าง
            result.append(None)  # เก็บเป็น None
        else:
            try:
                result.append(round(float(item.strip()), 3))  # แปลงเป็น float และปัดทศนิยม 3 ตำแหน่ง
            except ValueError:
                result.append(None)  # ถ้ากรอกค่าที่แปลงไม่ได้ เช่น ตัวอักษร
    return result

st.header("Import Control and Test Data")

patient_hn = st.number_input("**Enter Patient HN**", min_value=0, step=1, format="%d")
if patient_hn == [""]:
    patient_hn = None

if patient_hn:
    st.write(f"Patient HN: {patient_hn}")



data_nacl = [0.85, 0.75, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.20, 0.10, 0.00]
patient_hn = []
od_control = []
od_sample = []

# แสดงข้อมูลใน 2 คอลัมน์
with st.expander("**OF Test Laboratory Data**"):
    col_1, col_2 = st.columns(2)

    # ข้อมูล Control
    with col_1:
        st.write("**_Import Control Data_**")
        od_control_raw = [st.text_input(f"Enter OD for Control tube {i+1}", value="", key=f"control_{i}") for i in range(len(data_nacl))]

    # ข้อมูล Sample
    with col_2:
        st.write("**_Import Test Data_**")
        od_sample_raw = [st.text_input(f"Enter OD for Test tube {i+1}", value="", key=f"sample_{i}") for i in range(len(data_nacl))]

# แปลงค่าที่กรอกให้เป็น float หรือ None
od_control = validate_and_convert(od_control_raw)
od_sample = validate_and_convert(od_sample_raw)

# ฟังก์ชันการคำนวณ
def calculation(od_control, od_sample):
    control_lysis = []
    sample_lysis = []

    for i in range(len(data_nacl)):
        # ตรวจสอบว่ามีค่าที่สามารถคำนวณได้
        if od_control[i] is not None and od_control[-1] is not None and od_control[-1] != 0:
            control_lysis.append((od_control[i] / od_control[-1]) * 100)
        else:
            control_lysis.append(None)

        if od_sample[i] is not None and od_sample[-1] is not None and od_sample[-1] != 0:
            sample_lysis.append((od_sample[i] / od_sample[-1]) * 100)
        else:
            sample_lysis.append(None)

    # สร้าง DataFrame สำหรับแสดงผล
    result_data = {
        'Tube No.': reagent,
        '%Nacl': nacl_conc,
        'Control OD': od_control,
        'Control %Hemolysis': control_lysis,
        'Sample OD': od_sample,
        'Sample %Hemolysis': sample_lysis,
    }
    df = pd.DataFrame(result_data)

    st.subheader("Table Summary")
    st.dataframe(df)

    # Plotting after calculation
    if all(v is not None for v in control_lysis) and all(v is not None for v in sample_lysis):
        plotting(nacl_conc, control_lysis, 'Control')
        plotting(nacl_conc, sample_lysis, 'Sample')

# ฟังก์ชันการ plot กราฟ
def plotting(nacl_data, lysis_data, label):
    nacl_data = np.array(nacl_data)
    lysis_data = np.array(lysis_data)
    
    index = np.argsort(nacl_data)
    nacl_data_sorted = nacl_data[index]
    lysis_data_sorted = lysis_data[index]
   
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(nacl_data_sorted, lysis_data_sorted, 'o-', label=f'{label} %Hemolysis')
    ax.set_xlabel('%NaCl')
    ax.set_ylabel('%Hemolysis (%)')
    ax.set_title(f'Osmotic Fragility Test')
    ax.axhline(y=50, color='r', linestyle='--', label='50% Hemolysis')
    interpolated_nacl = np.interp(50, lysis_data, nacl_data)
    ax.plot([interpolated_nacl, interpolated_nacl], [0, 50], 'r--')
    ax.plot(interpolated_nacl, 50, 'ro')
    ax.annotate(f'%NaCl = {interpolated_nacl:.2f}',
                xy=(interpolated_nacl, 0), xytext=(interpolated_nacl, -10),
                textcoords='data', ha='center', va='top', color='red')
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 100)
    st.pyplot(fig)
def show_plots():
    col1, col2 = st.columns(2)


# ปุ่มให้ทำการคำนวณ
button_calculate = st.button("Calculate", type="primary")
button_clear = st.button("Clear") 
if button_calculate:
    calculation(od_control, od_sample)

