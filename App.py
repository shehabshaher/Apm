import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- 1. إعدادات الصفحة وتنسيق CSS ---
st.set_page_config(page_title="المطابقة الميدانية - فرع تعز", page_icon="📝", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; font-family: 'Tajawal', sans-serif; }
    .card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1); border: 1px solid #ddd; margin-bottom: 20px; }
    .card-header { color: #1f77b4; font-size: 22px; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 12px; }
    .data-row { margin-bottom: 10px; font-size: 16px; }
    .data-label { font-weight: bold; color: #555; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #1f77b4; }
</style>
""", unsafe_allow_html=True)

# --- 2. تحميل البيانات ومعالجة الأخطاء ---
FILE_NAME = "ملف المطابقة الميدانية فرع تعز.xlsx"

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_NAME)
        
        # تنظيف أسماء الأعمدة من المسافات الزائدة المخفية (لحل مشكلة KeyError)
        df.columns = df.columns.astype(str).str.strip()
        
        # التأكد من وجود عمود المطابقة، وإعطائه قيمة افتراضية "متبقي"
        if 'المطابقة' not in df.columns:
            df['المطابقة'] = "متبقي"
        else:
            df['المطابقة'] = df['المطابقة'].fillna("متبقي")
            
        # التأكد من وجود عمود للملاحظات
        if 'ملاحظات' not in df.columns:
            df['ملاحظات'] = ""
        else:
            df['ملاحظات'] = df['ملاحظات'].fillna("")
            
        return df
    
    except FileNotFoundError:
        st.error(f"لم يتم العثور على {FILE_NAME}. يرجى التأكد من رفع الملف.")
        return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

if not df.empty:
    st.title("📝 تطبيق المطابقة الميدانية")

    # --- 3. لوحة التحكم (Dashboard) العلوية ---
    st.markdown("### 📊 لوحة الإنجاز")
    
    total_customers = len(df)
    remaining_customers = len(df[df['المطابقة'] == 'متبقي'])
    completed_customers = total_customers - remaining_customers
    completion_rate = (completed_customers / total_customers) * 100 if total_customers > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي العملاء", total_customers)
    col2.metric("تمت المطابقة", completed_customers)
    col3.metric("المتبقي", remaining_customers)
    col4.metric("نسبة الإنجاز", f"{completion_rate:.1f}%")

    # رسم بياني يوضح توزيع الحالات
    status_counts = df['المطابقة'].value_counts().reset_index()
    status_counts.columns = ['الحالة', 'العدد']
    fig = px.pie(status_counts, names='الحالة', values='العدد', hole=0.4, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # --- 4. القائمة الجانبية (الفلترة والبحث) ---
    st.sidebar.header("🔍 البحث والتحديد")
    
    # خيار لتسهيل النزول الميداني بعرض المتبقي فقط
    show_remaining_only = st.sidebar.checkbox("عرض العملاء 'المتبقين' فقط", value=True)
    
    if show_remaining_only:
        filtered_df = df[df['المطابقة'] == 'متبقي']
    else:
        filtered_df = df
        
    customer_list = filtered_df['اســم العميــــــــــــل'].dropna().unique().tolist()
    
    if not customer_list:
        st.sidebar.success("🎉 ممتاز! لا يوجد عملاء في هذه القائمة حالياً.")
    else:
        selected_customer = st.sidebar.selectbox("اختر العميل:", customer_list)

        if selected_customer:
            # استخراج الفهرس الخاص بالعميل المختار
            customer_idx = df[df['اســم العميــــــــــــل'] == selected_customer].index[0]
            c_data = df.iloc[customer_idx]

            # دالة مساعدة لتجنب ظهور "nan" في الواجهة إذا كانت الخلية فارغة
            def safe_val(val):
                return str(val) if pd.notna(val) else "-"

            # --- 5. عرض البطاقة التفصيلية ---
            st.markdown(f"""
            <div class="card">
                <div class="card-header">🏢 {c_data['اســم العميــــــــــــل']}</div>
                <div class="data-row"><span class="data-label">المسلسل (م):</span> {safe_val(c_data.get('م'))}</div>
                <div class="data-row"><span class="data-label">الرصيد:</span> {safe_val(c_data.get('الرصـــيد'))}</div>
                <div class="data-row"><span class="data-label">ما قبله:</span> {safe_val(c_data.get('ماقبلــه'))}</div>
                <div class="data-row"><span class="data-label">التسديدات من بداية العام:</span> {safe_val(c_data.get('التسديدات من بداية العام'))}</div>
                <div class="data-row"><span class="data-label">المسؤول:</span> {safe_val(c_data.get('المسؤول'))} | 📞 {safe_val(c_data.get('رقم التلفون'))}</div>
                <div class="data-row"><span class="data-label">المختص:</span> {safe_val(c_data.get('اسم المختص'))}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- 6. نموذج التحديث وحفظ التعديلات ---
            st.subheader("⚙️ تحديث حالة المطابقة")
            with st.form(key='update_form'):
                match_options = ["متبقي", "مطابق", "غير مطابق", "لم يتم الرد", "مؤجل", "يوجد فارق"]
                current_status = str(c_data['المطابقة']).strip()
                
                # إذا كانت هناك حالة مخصصة مكتوبة مسبقاً في الإكسل، أضفها للقائمة
                if current_status not in match_options:
                    match_options.append(current_status)
                    
                default_index = match_options.index(current_status)
                
                new_status = st.selectbox("الحالة:", match_options, index=default_index)
                new_notes = st.text_area("ملاحظات:", value=str(c_data.get('ملاحظات', '')))
                
                submitted = st.form_submit_button("حفظ التعديلات 💾")
                
                if submitted:
                    st.session_state.df.at[customer_idx, 'المطابقة'] = new_status
                    st.session_state.df.at[customer_idx, 'ملاحظات'] = new_notes
                    st.success(f"تم تحديث بيانات '{selected_customer}' بنجاح!")
                    # إعادة تحميل الصفحة فوراً لتحديث الأرقام والرسم البياني
                    st.rerun()

    # --- 7. زر تصدير البيانات ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 تصدير التقرير")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.df.to_excel(writer, index=False, sheet_name='المطابقات')
    
    st.sidebar.download_button(
        label="تحميل ملف الإكسل المحدث 📊",
        data=output.getvalue(),
        file_name="ملف المطابقة الميدانية فرع تعز_محدث.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
