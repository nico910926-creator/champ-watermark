import streamlit as st
from PIL import Image, ImageOps
import io
import os

# 🌟 解除超大高畫質圖片的封印
Image.MAX_IMAGE_PIXELS = None

st.set_page_config(page_title="宸品團隊浮水印工具", page_icon="🏠", layout="wide")
st.title("🏠 宸品團隊 - 批次照片浮水印神器")
st.write("一次上傳多張照片，自動加上防盜浮水印，免解壓縮直接單張下載！")

logo_path = 'logo.png'
if not os.path.exists(logo_path):
    st.error("⚠️ 找不到 logo.png！請確認 Logo 圖檔跟這個程式放在同一個資料夾。")
    st.stop()

# 開啟多檔上傳功能
uploaded_files = st.file_uploader("請上傳房屋照片 (可以一次選取多張)", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"📁 目前已選取 {len(uploaded_files)} 張照片")

    if st.button("🚀 開始批次處理", type="primary"):
        with st.spinner(f'正在全力為 {len(uploaded_files)} 張照片加上浮水印，請稍候...'):
            try:
                # 載入並處理 Logo
                logo_image = Image.open(logo_path).convert("RGBA")
                content_w, content_h = logo_image.size
                alpha_value = 65 / 100.0
                alpha = logo_image.split()[3]
                alpha = alpha.point(lambda p: int(p * alpha_value))
                logo_image.putalpha(alpha)

                st.success(f"🎉 處理完成！請在下方瀏覽並下載照片。")
                
                # --- 🌟 關鍵修改：不打包 ZIP，直接一張一張顯示並產生下載按鈕 ---
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

                    # 將處理好的照片轉為下載格式
                    img_byte_arr = io.BytesIO()
                    final_image.save(img_byte_arr, format='JPEG', quality=95)
                    
                    # 🌟 為了排版好看，我們把照片和下載按鈕包在一個區塊裡
                    st.markdown("---") # 畫一條分隔線
                    st.image(final_image, caption=f"✅ 完成：{file.name}", use_container_width=True)
                    
                    # 產生獨立的下載按鈕 (注意這裡必須加上 key 確保每個按鈕是獨立的)
                    st.download_button(
                        label=f"💾 下載此照片 ({file.name})",
                        data=img_byte_arr.getvalue(),
                        file_name=f"浮水印_{file.name}",
                        mime="image/jpeg",
                        key=f"download_{i}" 
                    )

            except Exception as e:
                st.error(f"處理過程中發生錯誤: {e}")