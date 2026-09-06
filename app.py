import datetime
import os
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Grit Tracker", page_icon="⚡", layout="centered"
)

# --- ÖZEL TASARIM VE İOS TARZI KART / ANİMASYON CSS ---
st.markdown(
    """
    <style>
    /* Genel arka plan ve tipografi iyileştirmeleri */
    .stApp {
        background-color: #0e1117;
    }
    
    /* iOS tarzı yumuşatılmış, büyük ve renkli kart kapsayıcıları */
    .custom-card {
        padding: 18px 22px;
        border-radius: 20px;
        color: white;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
    }
    
    /* Su dolum animasyonu (Soldan sağa dolan sıvı efekti) */
    .water-bar-background {
        background-color: rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        height: 14px;
        width: 100%;
        margin-top: 10px;
        overflow: hidden;
        position: relative;
    }
    
    .water-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        border-radius: 12px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Form elemanlarını kart tasarıma entegre etme */
    div.stForm {
        background: transparent;
        border: none;
        padding: 0;
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

# Başlangıç Hedefleri (Kreatin kaldırıldı, Su hedefi 3L olarak güncellendi)
if "custom_goals" not in st.session_state:
  st.session_state["custom_goals"] = {
      "Su Tüketimi": {
          "emoji": "💧",
          "renk": "#1E88E5",
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

  with st.form("gunluk_form"):
    girilen_veriler = {}

    for hedef_adi, detay in st.session_state["custom_goals"].items():
      emoji = detay["emoji"]
      renk = detay["renk"]
      tip = detay["tip"]
      hedef_deger = detay["hedef_deger"]

      # Her hedef için iOS tarzı renkli ve yumuşatılmış çerçeve kartı
      st.markdown(
          f"""
            <div class="custom-card" style="background-color: {renk};">
                <div style="font-size: 18px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
                    <span>{emoji}</span> <span>{hedef_adi}</span>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      if tip == "Onay (Tik)":
        girilen_veriler[hedef_adi] = st.checkbox(
            f"{hedef_adi} Tamamlandı", value=False, key=f"chk_{hedef_adi}"
        )
      else:
        birim_etiketi = detay.get("birim", "")
        # Su tüketimi özelinde soldan sağa dolan sıvı animasyonlu bar gösterimi
        if hedef_adi == "Su Tüketimi":
          su_degeri = st.number_input(
              f"Miktar ({birim_etiketi})",
              min_value=0.0,
              max_value=10.0,
              step=0.25,
              value=0.0,
              key=f"num_{hedef_adi}",
          )
          girilen_veriler[hedef_adi] = su_degeri

          # Yüzde hesaplama (3 Litre hedefe göre)
          yuzde = min(int((su_degeri / hedef_deger) * 100), 100)
          st.markdown(
              f"""
                <div style="font-size: 13px; margin-top: -5px; margin-bottom: 5px; opacity: 0.9;">
                    Hedef: {hedef_deger} {birim_etiketi} | Alınan: {su_degeri} {birim_etiketi} (%{yuzde})
                </div>
                <div class="water-bar-background">
                    <div class="water-bar-fill" style="width: {yuzde}%;"></div>
                </div>
                """,
              unsafe_allow_html=True,
          )
        else:
          girilen_veriler[hedef_adi] = st.number_input(
              f"Miktar ({birim_etiketi})",
              min_value=0.0,
              step=1.0,
              value=0.0,
              key=f"num_{hedef_adi}",
          )

      st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    st.subheader("😴 Uyku Takibi")
    uyku_suresi = st.slider("Uyku Süresi (Saat)", 0, 12, 7)

    kaydet_buton = st.form_submit_button("Bugünü Kaydet / Güncelle")

    if kaydet_buton:
      yeni_veri = {"Tarih": str(bugun), "Uyku": uyku_suresi}
      yeni_veri.update(girilen_veriler)

      df = st.session_state["data"]

      for col in yeni_veri.keys():
        if col not in df.columns:
          df[col] = 0

      df["Tarih"] = df["Tarih"].astype(str)
      if not df[df["Tarih"] == str(bugun)].empty:
        for col, val in yeni_veri.items():
          df.loc[df["Tarih"] == str(bugun), col] = val
      else:
        df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)

      st.session_state["data"] = df
      verileri_kaydet(df)
      st.success("Veriler başarıyla kaydedildi! 💪")

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
    st.subheader("Kayıtlı Veri Tablosu")
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
