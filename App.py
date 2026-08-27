import streamlit as st
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="أداة هندسة الأوامر الاحترافية", page_icon="✨", layout="centered")

# الواجهة الأمامية
st.title("✨ صانع الأوامر الاحترافية (Prompt Generator)")
st.write("حول أفكارك البسيطة إلى أوامر (Prompts) دقيقة واحترافية للحصول على أفضل النتائج من نماذج الذكاء الاصطناعي.")

# إعدادات شريط الجانب (Sidebar) لمفتاح الـ API
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")
    st.markdown("[احصل على مفتاح API من هنا](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    st.write("💡 **نصيحة:** عند رفع التطبيق على Streamlit Cloud، يمكنك إعداد الـ API Key في قسم Secrets لتجنب إدخاله يدوياً كل مرة.")

# خيارات نوع الأمر
prompt_type = st.selectbox(
    "ما هو نوع الذكاء الاصطناعي الذي تستهدفه؟", 
    [
        "توليد الصور (Midjourney / DALL-E)", 
        "تصميم الهويات والتغليف التجاري",
        "توليد النصوص والمقالات", 
        "برمجة وأكواد"
    ]
)

# إدخال النص العادي
user_input = st.text_area("النص العادي (الفكرة):", placeholder="اكتب فكرتك هنا... مثال: عطر رجالي فخم بخلفية داكنة...")

# زر التحويل
if st.button("توليد الأمر الاحترافي 🚀"):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
    elif not user_input.strip():
        st.warning("⚠️ يرجى إدخال الفكرة أولاً.")
    else:
        try:
            # تهيئة الاتصال بـ Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # تحديد التعليمات المسبقة بناءً على اختيار المستخدم
            if prompt_type == "توليد الصور (Midjourney / DALL-E)":
                system_prompt = "أنت خبير محترف في هندسة الأوامر لـ Midjourney و DALL-E. حول الفكرة التالية إلى Prompt احترافي باللغة الإنجليزية. قم بتضمين تفاصيل الإضاءة (Cinematic lighting)، زاوية الكاميرا (Wide angle, Macro)، النمط الفني (Photorealistic, 8k, Unreal Engine 5). قدم النتيجة كـ Prompt جاهز للنسخ."
            elif prompt_type == "تصميم الهويات والتغليف التجاري":
                system_prompt = "أنت خبير في هندسة الأوامر لتصميم الهويات البصرية والتغليف (Mockups). حول الفكرة التالية إلى Prompt باللغة الإنجليزية يركز على تصميم عبوات منتجات تجارية بدون تشويه، مع التركيز على نظافة التصميم، الإضاءة الاستوديو، والواقعية العالية."
            elif prompt_type == "توليد النصوص والمقالات":
                system_prompt = "أنت خبير في صياغة الأوامر لـ ChatGPT و Gemini. حول الفكرة التالية إلى Prompt دقيق وشامل يحدد (الدور المطلوب، النبرة، الجمهور المستهدف، وهيكل الإجابة)."
            else:
                system_prompt = "أنت خبير برمجي. حول الفكرة التالية إلى Prompt برمجي دقيق يحدد اللغة المطلوبة، إطار العمل، والشروط لضمان الحصول على كود نظيف بدون أخطاء."

            # دمج التعليمات مع مدخلات المستخدم
            final_request = f"{system_prompt}\n\nالفكرة العادية:\n{user_input}"

            with st.spinner("جاري هندسة الأمر وصياغته... ⏳"):
                response = model.generate_content(final_request)
                
            st.success("✨ تم التوليد بنجاح!")
            
            # عرض النتيجة في مربع كود لسهولة النسخ
            st.code(response.text, language="markdown")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
