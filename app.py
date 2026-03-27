import streamlit as st
from PIL import Image, ImageOps
import io
import os
import zipfile

# 解除超大高畫質圖片的封印
Image.MAX_IMAGE_PIXELS = None

st.set_page_config(page_title="宸品團隊浮水印工具", page_icon="🏠", layout="wide")
st.title("🏠 宸品團隊 - 批次照片浮水印神器")
st.write("上傳多張物件照片，一鍵鋪滿浮水印並自動打包，省時最高效！")

st.sidebar.header("⚙️ 浮水印微調設定")
opacity = st.sidebar.slider("1. 不透明度 (越高越清楚)", min_value=10, max_value=100, value=60, step=5)
logo_scale = st.sidebar.slider("2. 浮水印大小", min_value=5, max_value=40, value=15, step=1)
spacing = st.sidebar.slider("3. 排列間距 (越小越密)", min_value=1.0, max_value=3.0, value=1.5, step=0.1)

logo_path = 'logo.png'
if not os.path.exists(logo_path):
    st.error("⚠️ 找不到 logo.png！請確認 Logo 圖檔跟這個程式放在同一個資料夾。")
    st.stop()

# 開啟多檔上傳功能
uploaded_files = st.file_uploader("請上傳房屋照片 (可以一次選取多張)", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"📁 目前已選取 {len(uploaded_files)} 張照片")

    if st.button("🚀 一鍵批次處理全部照片", type="primary"):
        with st.spinner(f'正在全力為 {len(uploaded_files)} 張照片加上浮水印，請稍候...'):
            try:
                # 1. 處理 Logo
                logo_image = Image.open(logo_path).convert("RGBA")
                content_w, content_h = logo_image.size
                alpha_value = 65 / 100.0
                alpha = logo_image.split()[3]
                alpha = alpha.point(lambda p: int(p * alpha_value))
                logo_image.putalpha(alpha)

                # 2. 準備空的 ZIP 壓縮檔
                zip_buffer = io.BytesIO()
                
                # 開啟壓縮檔準備塞照片
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    
                    progress_bar = st.progress(0)
                    
                    for i, file in enumerate(uploaded_files):
                        image = Image.open(file)
                        image = ImageOps.exif_transpose(image).convert("RGBA")

                        width, height = image.size
                        logo_width_target = int(width * (25 / 100.0))
                        logo_height_target = int((logo_width_target / content_w) * content_h)
                        
                        logo_resized = logo_image.resize((logo_width_target, logo_height_target), Image.Resampling.LANCZOS)
                        logo_rotated = logo_resized.rotate(15, expand=True, resample=Image.Resampling.BICUBIC)
                        rot_w, rot_h = logo_rotated.size

                        transparent_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                        step_x = int(rot_w * 1.2)
                        step_y = int(rot_h * 0.55)

                        for row, y in enumerate(range(-rot_h, height, step_y)):
                            offset_x = int(step_x / 2) if row % 2 != 0 else 0
                            for x in range(-rot_w - offset_x, width, step_x):
                                transparent_layer.paste(logo_rotated, (x, y), mask=logo_rotated)

                        combined_image = Image.alpha_composite(image, transparent_layer)
                        final_image = combined_image.convert("RGB")

                        # 存入記憶體並塞進 ZIP 檔
                        img_byte_arr = io.BytesIO()
                        final_image.save(img_byte_arr, format='JPEG', quality=95)
                        zip_file.writestr(f"宸品浮水印_{file.name}", img_byte_arr.getvalue())
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))

                st.success(f"🎉 處理完畢！請點擊下方按鈕一次下載全部。")

                # 3. 唯一的終極下載按鈕
                st.download_button(
                    label=f"📦 一鍵下載全部 {len(uploaded_files)} 張照片 (ZIP包)",
                    data=zip_buffer.getvalue(),
                    file_name="宸品團隊_浮水印美照.zip",
                    mime="application/zip",
                    type="primary"
                )

            except Exception as e:
                st.error(f"處理過程中發生錯誤: {e}")