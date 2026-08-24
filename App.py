import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- 1. إعدادات الصفحة وتنسيق CSS ---
st.set_page_config(page_title="المطابقة الميدانية", page_icon="📝", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; font-family: 'Tajawal', sans-serif; }
    .card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1); border: 1px solid #ddd; margin-bottom: 20px; }
    .card-header { color: #1f77b4; font-size: 22px; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 12px; }
    .data-row { margin-bottom: 10px; font-size: 16px; }
    .data-label { font-weight: bold; color: #555; }
    /* تحسين شكل المؤشرات */
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 2. تحميل البيانات ---
FILE_NAME = "ملف المطابقة الميدانية فرع تعز.xlsx"

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_NAME)
        # معالجة القيم الفارغة في عمود المطابقة لتصبح "متبقي"
        df['المطابقة'] = df['المطابقة'].fillna("متبقي")
        df['المطابقة'] = df['المطابقة'].replace(r'^\s*$', "متبقي", regex=True)
        return df
    except FileNotFoundError:
        st.error(f"لم يتم العثور على {FILE_NAME}. يرجى التأكد من رفع الملف.")
        return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.title("📝 تطبيق المطابقة الميدانية")

if not df.empty:
    # --- 3. لوحة المتابعة والإنجاز (Dashboard) ---
    st.header("📊 ملخص الإنجاز الميداني")
    
    total_customers = len(df)
    pending_count = len(df[df['المطابقة'] == 'متبقي'])
    completed_count = total_customers - pending_count
    matched_count = len(df[df['المطابقة'] == 'مطابق'])
    unmatched_count = len(df[df['المطابقة'] == 'غير مطابق'])
    
    progress_pct = (completed_count / total_customers) * 100 if total_customers > 0 else 0

    # عرض المؤشرات الرقمية
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي العملاء", total_customers)
    col2.metric("تمت زيارتهم (منجز)", completed_count)
    col3.metric("المتبقي", pending_count)
    col4.metric("نسبة الإنجاز", f"{progress_pct:.1f}%")
    
    st.progress(progress_pct / 100.0)

    # عرض الرسم البياني
    status_counts = df['المطابقة'].value_counts().reset_index()
    status_counts.columns = ['الحالة', 'العدد']
    
    fig = px.pie(status_counts, values='العدد', names='الحالة', hole=0.4, 
                 title="توزيع حالات المطابقة",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), title_x=0.5, font=dict(family="Tajawal", size=16))
    
    # تصغير حجم الرسم البياني بوضعه في عمود أوسط
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- 4. اختيار العميل ---
    st.sidebar.header("🔍 البحث والتحديد")
    
    # فلتر اختياري لتسهيل البحث (عرض الكل، أو المتبقي فقط)
    filter_option = st.sidebar.radio("تصفية القائمة:", ["عرض كل العملاء", "العملاء المتبقين فقط"])
    if filter_option == "العملاء المتبقين فقط":
        customer_list = df[df['المطابقة'] == 'متبقي']['اســم العميــــــــــــل'].dropna().unique().tolist()
    else:
        customer_list = df['اســم العميــــــــــــل'].dropna().unique().tolist()

    selected_customer = st.sidebar.selectbox("اختر العميل:", customer_list)

    if selected_customer:
        # استخراج الفهرس والبيانات
        customer_idx = df[df['اســم العميــــــــــــل'] == selected_customer].index[0]
        c_data = df.iloc[customer_idx]

        # --- 5. عرض البطاقة ---
        st.subheader("👤 بيانات العميل")
        st.markdown(f"""
        <div class="card">
            <div class="card-header">🏢 {c_data['اســم العميــــــــــــل']}</div>
            <div class="data-row"><span class="data-label">المسلسل (م):</span> {c_data['م']}</div>
            <div class="data-row"><span class="data-label">الرصيد:</span> {c_data['الرصـــيد']:,.2f}</div>
            <div class="data-row"><span class="data-label">ما قبله:</span> {c_data['ماقبلــه']}</div>
            <div class="data-row"><span class="data-label">التسديدات:</span> {c_data['التسديدات من بداية العام']}</div>
            <div class="data-row"><span class="data-label">المسؤول:</span> {c_data['المسؤول']} | 📞 {c_data['رقم التلفون']}</div>
            <div class="data-row"><span class="data-label">المختص:</span> {c_data['اسم المختص']}</div>
        </div>
        """, unsafe_allow_html=True)

        # --- 6. نموذج المطابقة ---
        st.subheader("⚙️ تحديث حالة المطابقة")
        with st.form(key='update_form'):
            match_options = ["متبقي", "مطابق", "غير مطابق", "لم يتم الرد", "مؤجل", "يوجد فارق"]
            current_status = str(c_data['المطابقة'])
            default_index = match_options.index(current_status) if current_status in match_options else 0
            
            new_status = st.selectbox("الحالة:", match_options, index=default_index)
            new_notes = st.text_area("ملاحظات:", value=str(c_data['ملاحظات']) if pd.notna(c_data['ملاحظات']) else "")
            
            if st.form_submit_button("حفظ التعديلات 💾"):
                st.session_state.df.at[customer_idx, 'المطابقة'] = new_status
                st.session_state.df.at[customer_idx, 'ملاحظات'] = new_notes
                st.success(f"تم تحديث بيانات '{selected_customer}' بنجاح!")
                st.rerun() # إعادة تحميل الصفحة لتحديث الرسوم البيانية والأرقام فوراً

    # --- 7. تصدير الملف ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 التصدير")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.df.to_excel(writer, index=False, sheet_name='المطابقات')
    
    st.sidebar.download_button(
        label="تحميل ملف الإكسل المحدث 📊",
        data=output.getvalue(),
        file_name="ملف المطابقة الميدانية فرع تعز_محدث.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      )
