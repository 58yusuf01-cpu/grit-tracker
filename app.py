import datetime
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Grit Tracker", page_icon="⚡", layout="centered"
)

# --- VERİ VE HEDEF YÖNETİMİ BAŞLANGICI ---
# Her hedefin detaylı yapılandırması: Ad, Emoji, Renk, Tür (checkbox veya miktar/sayısal)
if "custom_goals" not in st.session_state:
  st.session_state["custom_goals"] = {
      "Python / Yapay Zeka": {
          "emoji": "💻",
          "renk": "#1f77b4",
          "tip": "Onay (Tik)",
          "hedef_deger": 1.0,
      },
      "Antrenman": {
          "emoji": "🏋️",
          "renk": "#ff7f0e",
          "tip": "Onay (Tik)",
          "hedef_deger": 1.0,
      },
      "Su Tüketimi": {
          "emoji": "💧",
          "renk": "#2ca02c",
          "tip": "Miktar (Sayısal)",
          "hedef_deger": 3.0,
          "birim": "L",
      },
      "Kitap Okuma": {
          "emoji": "📖",
          "renk": "#d62728",
          "tip": "Miktar (Sayısal)",
          "hedef_deger": 30.0,
          "birim": "sayfa",
      },
  }

# Günlük kayıt veritabanı simülasyonu
if "data" not in st.session_state:
  st.session_state["data"] = pd.DataFrame(columns=["Tarih", "Uyku"])

bugun = datetime.date.today()

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
# 1. SEKME: BUGÜN (Kişiselleştirilmiş Girişler)
# ==========================================
with tab_gunluk:
  st.header("Günlük Hedefler")
  st.caption(f"Tarih: {bugun.strftime('%d.%m.%Y')}")

  with st.form("gunluk_form"):
    st.subheader("Disiplin Takibi")

    # Dinamik olarak oluşturulan hedef girdileri (emoji, renk ve tipe göre)
    girilen_veriler = {}
    for hedef_adi, detay in st.session_state["custom_goals"].items():
      baslik = f"{detay['emoji']} {hedef_adi}"

      if detay["tip"] == "Onay (Tik)":
        girilen_veriler[hedef_adi] = st.checkbox(baslik)
      else:
        # Miktar bazlı hedefler için sayısal giriş alanı (varsayılan hedef değerini başlangıç yapar)
        birim_etiketi = detay.get("birim", "")
        girilen_veriler[hedef_adi] = st.number_input(
            f"{baslik} ({birim_etiketi})",
            min_value=0.0,
            step=1.0,
            value=float(detay["hedef_deger"]),
        )

    # Sabit Kreatin Kuralı (3 gr)
    st.checkbox("⚡ Kreatin (3 gr) - Sabit", value=True, disabled=True)

    st.subheader("Sayısal Veriler")
    uyku_suresi = st.slider("😴 Uyku Süresi (Saat)", 0, 12, 7)

    kaydet_buton = st.form_submit_button("Bugünü Kaydet / Güncelle")

    if kaydet_buton:
      yeni_veri = {"Tarih": bugun, "Uyku": uyku_suresi}
      yeni_veri.update(girilen_veriler)

      df = st.session_state["data"]

      # Eksik sütunları dataframe'e ekle
      for col in yeni_veri.keys():
        if col not in df.columns:
          df[col] = 0

      # Bugünün kaydı varsa güncelle, yoksa ekle
      if not df[df["Tarih"] == bugun].empty:
        for col, val in yeni_veri.items():
          df.loc[df["Tarih"] == bugun, col] = val
      else:
        st.session_state["data"] = pd.concat(
            [df, pd.DataFrame([yeni_veri])], ignore_index=True
        )

      st.success("Veriler başarıyla işlendi, disiplin bozulmasın! 💪")

# ==========================================
# 2. SEKME: HEDEF YÖNETİMİ (Emoji, Renk ve Birim Ayarları)
# ==========================================
with tab_hedef_yonetimi:
  st.header("Hedefleri ve Görsel Detayları Düzenle")
  st.write(
      "Buradan hedeflerinin adını, emojisjni, rengini ve birimini"
      " kişiselleştirebilirsin."
  )

  # Yeni Hedef Ekleme Formu
  with st.form("yeni_hedef_form"):
    st.subheader("Yeni Hedef Ekle")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
      yeni_ad = st.text_input("Hedef Adı (Örn: Su Tüketimi)")
      yeni_emoji = st.text_input("Emoji (Örn: 💧)", value="🎯")
    with col_h2:
      yeni_tip = st.selectbox(
          "Hedef Tipi", ["Onay (Tik)", "Miktar (Sayısal)"]
      )
      yeni_renk = st.color_picker("Hedef Rengi", value="#1f77b4")

    yeni_birim = ""
    yeni_hedef_deger = 1.0
    if yeni_tip == "Miktar (Sayısal)":
      col_b1, col_b2 = st.columns(2)
      with col_b1:
        yeni_birim = st.text_input("Birim (Örn: L, sayfa, dk)", value="adet")
      with col_b2:
        yeni_hedef_deger = st.number_input(
            "Hedeflenen Miktar", min_value=0.1, value=2.0
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
  df = st.session_state["data"]

  if df.empty or len(df.columns) <= 2:
    st.info("Henüz yeterli veri girilmedi.")
  else:
    st.subheader("Haftalık Veri Tablosu")
    st.dataframe(df)

# ==========================================
# 4. SEKME: AYLIK İSTATİSTİKLER
# ==========================================
with tab_aylik:
  st.header("Aylık Rapor")
  df = st.session_state["data"]
  if not df.empty and "Uyku" in df.columns:
    ortalama_uyku = df["Uyku"].mean()
    st.metric("😴 Ortalama Uyku Süresi", f"{ortalama_uyku:.1f} Saat")

# ==========================================
# 5. SEKME: YILLIK İSTATİSTİKLER
# ==========================================
with tab_yillik:
  st.header("Yıllık Büyük Resim")
  st.info("Uzun vadeli disiplin ve istikrar paneli.")
