import datetime
import os
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Grit Tracker", page_icon="⚡", layout="centered"
)

# --- İOS TARZI KART VE BUTON STİLLERİ ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
    }
    
    /* Streamlit butonlarını iOS tarzı yuvarlak butonlara dönüştürme */
    .stButton button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        padding: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: rgba(255, 255, 255, 0.25) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.4) !important;
        border-color: white !important;
    }

    /* Su dolum animasyonu */
    .water-bar-background {
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        height: 6px;
        width: 100%;
        margin-top: 6px;
        overflow: hidden;
    }
    
    .water-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #ffffff 0%, #e0f7fa 100%);
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- VERİ DOSYASI YÖNETİMİ ---
VERI_DOSYASI = "veri.csv"


def verileri_yukle():
  if os.path.exists(VERI_DOSYASI):
    return pd.read_csv(VERI_DOSYASI)
  else:
    return pd.DataFrame(columns=["Tarih", "Uyku"])


def verileri_kaydet(df):
  df.to_csv(VERI_DOSYASI, index=False)


if "data" not in st.session_state:
  st.session_state["data"] = verileri_yukle()

# Başlangıç Hedefleri
if "custom_goals" not in st.session_state:
  st.session_state["custom_goals"] = {
      "Su Tüketimi": {
          "emoji": "💧",
          "renk": "#374151",
          "tip": "Miktar (Sayısal)",
          "hedef_deger": 3.0,
          "birim": "L",
      },
      "Python / Yapay Zeka": {
          "emoji": "💻",
          "renk": "#2E7D32",
          "tip": "Onay (Tik)",
          "hedef_deger": 1.0,
      },
      "Antrenman": {
          "emoji": "🏋️",
          "renk": "#EF6C00",
          "tip": "Onay (Tik)",
          "hedef_deger": 1.0,
      },
      "Kitap Okuma": {
          "emoji": "📖",
          "renk": "#C62828",
          "tip": "Miktar (Sayısal)",
          "hedef_deger": 30.0,
          "birim": "sayfa",
      },
  }

bugun = datetime.date.today()
str_bugun = str(bugun)

# Otomatik veri çerçevesi hazırlığı
df = st.session_state["data"]
df["Tarih"] = df["Tarih"].astype(str)

if df[df["Tarih"] == str_bugun].empty:
  yeni_satir = {"Tarih": str_bugun, "Uyku": 7}
  for h in st.session_state["custom_goals"].keys():
    yeni_satir[h] = 0.0
  df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
  st.session_state["data"] = df
  verileri_kaydet(df)


def veri_guncelle(kolon, deger):
  global df
  df.loc[df["Tarih"] == str_bugun, kolon] = deger
  st.session_state["data"] = df
  verileri_kaydet(df)


# --- ÜST MENÜ / SEKMELER ---
tab_gunluk, tab_hedef_yonetimi, tab_haftalik, tab_aylik, tab_yillik = st.tabs(
    [
        "📅 Bugün",
        "⚙️ Hedef Yönetimi",
        "📊 Haftalık",
        "📈 Aylık",
        "🏆 Yıllık",
    ]
)

# ==========================================
# 1. SEKME: BUGÜN
# ==========================================
with tab_gunluk:
  st.header("Günlük Hedefler")
  st.caption(f"Tarih: {bugun.strftime('%d.%m.%Y')}")

  aktif_satir = df[df["Tarih"] == str_bugun].iloc[0]

  for hedef_adi, detay in st.session_state["custom_goals"].items():
    emoji = detay["emoji"]
    renk = detay["renk"]
    tip = detay["tip"]
    hedef_deger = detay["hedef_deger"]
    birim_etiketi = detay.get("birim", "")

    mevcut_deger = (
        aktif_satir[hedef_adi] if hedef_adi in aktif_satir else 0.0
    )
    if pd.isna(mevcut_deger):
      mevcut_deger = 0.0

    # iOS Tarzı Tek Parça Renkli Baloncu Yapısı (Yazı sol, Buton sağ içinde)
    st.markdown(
        f"""
        <div style="background-color: {renk}; padding: 12px 18px; border-radius: 20px; color: white; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 14px; flex-grow: 1;">
                <span style="font-size: 26px;">{emoji}</span>
                <div style="display: flex; flex-direction: column; justify-content: center; width: 100%;">
                    <div style="font-size: 16px; font-weight: 600; color: white; line-height: 1.2;">{hedef_adi}</div>
        """,
        unsafe_allow_html=True,
    )

    if tip == "Onay (Tik)":
      durum_metni = (
          "Her gün, Tamamlandı" if mevcut_deger > 0 else "Her gün, 0/1"
      )
      st.markdown(
          f"<div style='font-size: 12px; opacity: 0.8; color: white; margin-top: 2px;'>{durum_metni}</div>",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          f"<div style='font-size: 12px; opacity: 0.8; color: white; margin-top: 2px;'>Her gün, {mevcut_deger}/{hedef_deger} {birim_etiketi}</div>",
          unsafe_allow_html=True,
      )
      if hedef_adi == "Su Tüketimi":
        yuzde = min(int((mevcut_deger / hedef_deger) * 100), 100)
        st.markdown(
            f"""
            <div class="water-bar-background">
                <div class="water-bar-fill" style="width: {yuzde}%;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div></div>", unsafe_allow_html=True
    )  # Sol taraf (emoji + metinler) kapandı

    # Sağ taraftaki yuvarlak etkileşim butonu
    if tip == "Onay (Tik)":
      buton_etiketi = "✓" if mevcut_deger > 0 else "+"
      if st.button(buton_etiketi, key=f"btn_{hedef_adi}"):
        yeni_val = 0.0 if mevcut_deger > 0 else 1.0
        veri_guncelle(hedef_adi, yeni_val)
        st.rerun()
    else:
      artis_miktari = 0.5 if birim_etiketi == "L" else 1.0
      if st.button("+", key=f"btn_inc_{hedef_adi}"):
        yeni_val = mevcut_deger + artis_miktari
        veri_guncelle(hedef_adi, yeni_val)
        st.rerun()

  # Uyku Takibi Kartı
  mevcut_uyku = int(aktif_satir["Uyku"]) if "Uyku" in aktif_satir else 7
  st.markdown(
      """
      <div style="background-color: #37474F; padding: 14px 18px; border-radius: 20px; color: white; margin-bottom: 12px;">
          <div style="font-size: 16px; font-weight: 600; color: white; margin-bottom: 6px;">😴 Uyku Süresi</div>
      </div>
      """,
      unsafe_allow_html=True,
  )
  yeni_uyku = st.slider(
      "Uyku",
      0,
      12,
      mevcut_uyku,
      key="slider_uyku",
      label_visibility="collapsed",
  )
  if yeni_uyku != mevcut_uyku:
    veri_guncelle("Uyku", yeni_uyku)
    st.rerun()

# ==========================================
# 2. SEKME: HEDEF YÖNETİMİ
# ==========================================
with tab_hedef_yonetimi:
  st.header("Hedefleri ve Görsel Detayları Düzenle")

  with st.form("yeni_hedef_form"):
    st.subheader("Yeni Hedef Ekle")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
      yeni_ad = st.text_input("Hedef Adı (Örn: Kreatin)")
      yeni_emoji = st.text_input("Emoji (Örn: ⚡)", value="🎯")
    with col_h2:
      yeni_tip = st.selectbox(
          "Hedef Tipi", ["Onay (Tik)", "Miktar (Sayısal)"]
      )
      yeni_renk = st.color_picker("Hedef Rengi", value="#37474F")

    yeni_birim = ""
    yeni_hedef_deger = 1.0
    if yeni_tip == "Miktar (Sayısal)":
      col_b1, col_b2 = st.columns(2)
      with col_b1:
        yeni_birim = st.text_input("Birim (Örn: gr, adet)", value="gr")
      with col_b2:
        yeni_hedef_deger = st.number_input(
            "Hedeflenen Miktar", min_value=0.1, value=3.0
        )

    hedef_ekle_buton = st.form_submit_button("Sisteme Ekle")

    if hedef_ekle_buton and yeni_ad:
      if yeni_ad not in st.session_state["custom_goals"]:
        st.session_state["custom_goals"][yeni_ad] = {
            "emoji": yeni_emoji,
            "renk": yeni_renk,
            "tip": yeni_tip,
            "hedef_deger": yeni_hedef_deger,
            "birim": yeni_birim,
        }
        if yeni_ad not in df.columns:
          df[yeni_ad] = 0.0
          st.session_state["data"] = df
          verileri_kaydet(df)

        st.success(f"'{yeni_emoji} {yeni_ad}' başarıyla eklendi!")
        st.rerun()
      else:
        st.warning("Bu isimde bir hedef zaten var.")

  st.divider()
  st.subheader("Mevcut Hedefleri Yönet")
  if st.session_state["custom_goals"]:
    silinecek_hedef = st.selectbox(
        "Silmek istediğin hedefi seç:", list(st.session_state["custom_goals"].keys())
    )
    if st.button("Seçili Hedefi Kalıcı Olarak Sil"):
      if len(st.session_state["custom_goals"]) > 1:
        del st.session_state["custom_goals"][silinecek_hedef]
        st.success(f"'{silinecek_hedef}' listeden kaldırıldı.")
        st.rerun()
      else:
        st.error("En az bir hedef kalmak zorunda.")

# ==========================================
# 3. SEKME: HAFTALİK İSTATİSTİKLER
# ==========================================
with tab_haftalik:
  st.header("Haftalık İlerleme")
  df_w = st.session_state["data"]
  if df_w.empty or len(df_w.columns) <= 2:
    st.info("Henüz yeterli veri girilmedi.")
  else:
    st.subheader("Kayıtlı Veri Tablosu")
    st.dataframe(df_w)

# ==========================================
# 4. SEKME: AYLIK İSTATİSTİKLER
# ==========================================
with tab_aylik:
  st.header("Aylık Rapor")
  df_m = st.session_state["data"]
  if not df_m.empty and "Uyku" in df_m.columns:
    ortalama_uyku = df_m["Uyku"].mean()
    st.metric("😴 Ortalama Uyku Süresi", f"{ortalama_uyku:.1f} Saat")

# ==========================================
# 5. SEKME: YILLIK İSTATİSTİKLER
# ==========================================
with tab_yillik:
  st.header("Yıllık Büyük Resim")
  st.info("Uzun vadeli disiplin ve istikrar paneli.")
