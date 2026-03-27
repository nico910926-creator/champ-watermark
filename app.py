import streamlit as st
from PIL import Image
import io
import os

# 🌟 解除超大高畫質圖片的封印
Image.MAX_IMAGE_PIXELS = None

# --- 網頁的標題與外觀設定 ---
st.set_page_config(page_title="宸品團隊浮水印工具", page_icon="🏠")
st.title("🏠 宸品團隊 - 照片浮水印神器")
st.write("上傳房屋照片，一鍵鋪滿專屬防盜浮水印！手機、電腦皆可使用。")

# 檢查 Logo 是否存在
logo_path = 'logo.png'
if not os.path.exists(logo_path):
    st.error("⚠️ 找不到 logo.png！請確認 Logo 圖檔跟這個程式放在同一個資料夾。")
    st.stop() # 停止執行

# --- 1. 建立上傳照片的區塊 ---
uploaded_file = st.file_uploader("請上傳要處理的房屋照片 (支援 JPG, PNG)", type=['png', 'jpg', 'jpeg', 'webp'])

if uploaded_file is not None:
    # 顯示使用者上傳的原始照片
    image = Image.open(uploaded_file).convert("RGBA")
    st.image(image, caption="你上傳的原始照片", use_container_width=True)

    # --- 2. 建立處理按鈕 ---
    if st.button("🚀 一鍵加上浮水印", type="primary"):
        with st.spinner('處理中，請稍候...'):
            try:
                # 載入並處理 Logo
                logo_image = Image.open(logo_path).convert("RGBA")
                content_w, content_h = logo_image.size

                # 半透明化 (30%)
                alpha = logo_image.split()[3]
                alpha = alpha.point(lambda p: p * 0.65)
                logo_image.putalpha(alpha)

                # 影像處理核心邏輯 (滿版斜向)
                width, height = image.size
                logo_width_target = int(width * 0.2)
                logo_height_target = int((logo_width_target / content_w) * content_h)
                
                logo_resized = logo_image.resize((logo_width_target, logo_height_target), Image.Resampling.LANCZOS)
                logo_rotated = logo_resized.rotate(20, expand=True, resample=Image.Resampling.BICUBIC)
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

                # --- 3. 顯示完成的照片 ---
                st.success("大功告成！")
                st.image(final_image, caption="處理完成的照片", use_container_width=True)

                # --- 4. 建立下載按鈕 ---
                buf = io.BytesIO()
                final_image.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()

                st.download_button(
                    label="💾 下載加好浮水印的照片",
                    data=byte_im,
                    file_name="watermarked_photo.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"處理過程中發生錯誤: {e}")