import streamlit as st
from PIL import Image, ImageOps
import io
import os
import zipfile # 🌟 新增：用來製作 ZIP 壓縮檔的工具

# 🌟 解除超大高畫質圖片的封印
Image.MAX_IMAGE_PIXELS = None

st.set_page_config(page_title="宸品團隊浮水印工具", page_icon="🏠", layout="wide")
st.title("🏠 宸品團隊 - 批次照片浮水印神器")
st.write("一次上傳整個物件的所有照片，一鍵鋪滿浮水印並自動打包下載！")

logo_path = 'logo.png'
if not os.path.exists(logo_path):
    st.error("⚠️ 找不到 logo.png！請確認 Logo 圖檔跟這個程式放在同一個資料夾。")
    st.stop()

# --- 🌟 關鍵升級 1：開啟多檔上傳功能 (accept_multiple_files=True) ---
uploaded_files = st.file_uploader("請上傳房屋照片 (可以框選或拖曳「多張」照片)", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"📁 目前已選取 {len(uploaded_files)} 張照片")

    if st.button("🚀 一鍵批次處理全部照片", type="primary"):
        with st.spinner(f'正在全力為 {len(uploaded_files)} 張照片加上浮水印，請稍候...'):
            try:
                # 載入並處理 Logo (只需要做一次)
                logo_image = Image.open(logo_path).convert("RGBA")
                content_w, content_h = logo_image.size
                alpha_value = 65 / 100.0
                alpha = logo_image.split()[3]
                alpha = alpha.point(lambda p: int(p * alpha_value))
                logo_image.putalpha(alpha)

                # --- 🌟 關鍵升級 2：準備一個空的 ZIP 壓縮檔 ---
                zip_buffer = io.BytesIO()
                
                # 開啟壓縮檔準備把照片塞進去
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    
                    # 使用進度條讓你知道目前跑到第幾張
                    progress_bar = st.progress(0)
                    
                    for i, file in enumerate(uploaded_files):
                        # 讀取當前這張照片
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

                        # 將處理好的照片存入記憶體，然後塞進 ZIP 檔裡
                        img_byte_arr = io.BytesIO()
                        final_image.save(img_byte_arr, format='JPEG', quality=95)
                        
                        # 在壓縮檔裡的照片名稱前加上 "已加浮水印_"
                        zip_file.writestr(f"已加浮水印_{file.name}", img_byte_arr.getvalue())
                        
                        # 更新進度條
                        progress_bar.progress((i + 1) / len(uploaded_files))

                st.success(f"🎉 大功告成！已成功處理 {len(uploaded_files)} 張照片。")

                # --- 🌟 關鍵升級 3：單一 ZIP 下載按鈕 ---
                st.download_button(
                    label="📦 一鍵下載全部照片 (ZIP壓縮檔)",
                    data=zip_buffer.getvalue(),
                    file_name="宸品團隊_浮水印照片包.zip",
                    mime="application/zip",
                    type="primary"
                )

            except Exception as e:
                st.error(f"處理過程中發生錯誤: {e}")