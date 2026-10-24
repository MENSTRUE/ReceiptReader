import sys, json, csv, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import streamlit as st
from PIL import Image, UnidentifiedImageError
from receiptreader.inference import analyze
from receiptreader.ocr import OCRUnavailable
from receiptreader.visualization import make_preview

st.set_page_config(page_title='ReceiptReader | Review-first OCR', page_icon='🧾', layout='wide')
st.title('ReceiptReader')
st.caption('Research prototype • Tesseract baseline + field heuristics • v10 model NOT integrated • Human verification required')
upload=st.file_uploader('Upload receipt image',type=['png','jpg','jpeg','webp'])
if upload is None:
    st.info('Upload a receipt to start. OCR fields are suggestions; correct them before export.')
    st.stop()
try:
    image=Image.open(upload).convert('RGB')
except (UnidentifiedImageError, OSError):
    st.error('Unsupported or corrupted image.')
    st.stop()
col1,col2=st.columns([1,1],gap='large')
with col1:
    st.image(make_preview(image),caption='Receipt input',use_container_width=True)
with col2:
    if st.button('Run OCR',type='primary'):
        try:
            raw, fields = analyze(image)
        except OCRUnavailable as exc:
            st.error(str(exc))
        else:
            st.session_state['last_file'] = upload.name
            st.session_state['raw_text'] = raw
            st.session_state['fields'] = fields
    if st.session_state.get('last_file') != upload.name:
        st.info('Select Run OCR to extract the text.')
    else:
        guessed=st.session_state.get('fields',{})
        with st.form('review'):
            company=st.text_input('Company / Merchant',value=guessed.get('company',''))
            date=st.text_input('Date',value=guessed.get('date',''))
            address=st.text_area('Address (manual review)',value=guessed.get('address',''))
            total=st.text_input('Total (verify currency)',value=guessed.get('total',''))
            verified=st.checkbox('I have checked these fields against the receipt')
            submit=st.form_submit_button('Confirm reviewed values')
            if submit:
                if not verified:
                    st.warning('Please check and confirm values before export.')
                else:
                    st.session_state['reviewed']={'company':company,'date':date,'address':address,'total':total,'verified_by_user':True,'filename':upload.name}
        with st.expander('Raw OCR text'):
            st.code(st.session_state.get('raw_text',''),language='text')
        reviewed=st.session_state.get('reviewed')
        if reviewed and reviewed.get('filename') == upload.name:
            st.success('Human reviewed. You can export the corrected values.')
            st.download_button('Download JSON',json.dumps(reviewed,ensure_ascii=False,indent=2).encode('utf-8'),'receipt_reviewed.json','application/json')
            f=io.StringIO();writer=csv.DictWriter(f,fieldnames=reviewed.keys());writer.writeheader();writer.writerow(reviewed)
            st.download_button('Download CSV',f.getvalue().encode('utf-8-sig'),'receipt_reviewed.csv','text/csv')
