import datetime
import json
import os
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Grit Tracker", page_icon="⚡", layout="centered"
)

# --- DOSYA YÖNETİMİ ---
VERI_DOSYASI = "veri.csv"
HEDEF_DOSYASI = "hedefler_ayar.json"

HAFTALIK_VERI_DOSYASI = "veri_haftalik.csv"
HAFTALIK_HEDEF_DOSYASI = "haftalik_hedefler_ayar.json"

# Varsayılan Günlük Hedefler
DEFAULT_GOALS = {
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

# Varsayılan Haftalık Hedefler
DEFAULT_HAFTALIK_GOALS = {
    "Haftalık Spor": {
        "emoji": "🔥",
        "renk": "#1E3A8A",
        "tip": "Miktar (Sayısal)",
        "hedef_deger": 4.0,
        "birim": "gün",
    },
    "Kod / Proje": {
        "emoji": "🚀",
        "renk": "#581C87",
        "tip": "Onay (Tik)",
        "hedef_deger": 1.0,
    },
}


def hedefleri_yukle(dosya, varsayilan):
  if os.path.exists(dosya):
    try:
      with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return varsayilan
  return varsayilan


def hedefleri_kaydet(dosya, hedefler):
  with open(dosya, "w", encoding="utf-8") as f:
    json.dump(hedefler, f, ensure_ascii=False, indent=4)


def verileri_yukle(dosya, ek_kolonlar):
  if os.path.exists(dosya):
    try:
      df = pd.read_csv(dosya)
      if "Tarih" not in df.columns:
        cols = ["Tarih"] + ek_kolonlar
        return pd.DataFrame(columns=cols)
      return df
    except:
      cols = ["Tarih"] + ek_kolonlar
      return pd.DataFrame(columns=cols)
  else:
    cols = ["Tarih"] + ek_kolonlar
    return pd.DataFrame(columns=cols)


def verileri_kaydet(dosya, df):
  df.to_csv(dosya, index=False)


bugun = datetime.date.today()
str_bugun = str(bugun)

yil, hafta_num, _ = bugun.isocalendar()
str_hafta = f"{yil}-W{hafta_num:02d}"

# Session State Başlatma
if "custom_goals" not in st.session_state:
  st.session_state["custom_goals"] = hedefleri_yukle(
      HEDEF_DOSYASI, DEFAULT_GOALS
  )

if "custom_haftalik_goals" not in st.session_state:
  st.session_state["custom_haftalik_goals"] = hedefleri_yukle(
      HAFTALIK_HEDEF_DOSYASI, DEFAULT_HAFTALIK_GOALS
  )

# Günlük DataFrame yükleme ve eksik kolonları tamamlama
df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
df["Tarih"] = df["Tarih"].astype(str)

for h_adi in st.session_state["custom_goals"].keys():
  if h_adi not in df.columns:
    df[h_adi] = 0.0

if df[df["Tarih"] == str_bugun].empty:
  yeni_satir = {"Tarih": str_bugun, "Uyku": 7}
  for h in st.session_state["custom_goals"].keys():
    yeni_satir[h] = 0.0
  df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
  verileri_kaydet(VERI_DOSYASI, df)

st.session_state["data"] = df

# Haftalık DataFrame yükleme
df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
df_h["Tarih"] = df_h["Tarih"].astype(str)

for h_adi in st.session_state["custom_haftalik_goals"].keys():
  if h_adi not in df_h.columns:
    df_h[h_adi] = 0.0

if df_h[df_h["Tarih"] == str_hafta].empty:
  yeni_satir_h = {"Tarih": str_hafta}
  for h in st.session_state["custom_haftalik_goals"].keys():
    yeni_satir_h[h] = 0.0
  df_h = pd.concat([df_h, pd.DataFrame([yeni_satir_h])], ignore_index=True)
  verileri_kaydet(HAFTALIK_VERI_DOSYASI, df_h)

st.session_state["haftalik_data"] = df_h


def veri_guncelle(kolon, deger):
  current_df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  current_df["Tarih"] = current_df["Tarih"].astype(str)
  if current_df[current_df["Tarih"] == str_bugun].empty:
    yeni_satir = {"Tarih": str_bugun, "Uyku": 7}
    for h in st.session_state["custom_goals"].keys():
      yeni_satir[h] = 0.0
    current_df = pd.concat(
        [current_df, pd.DataFrame([yeni_satir])], ignore_index=True
    )
  current_df.loc[current_df["Tarih"] == str_bugun, kolon] = deger
  verileri_kaydet(VERI_DOSYASI, current_df)
  st.session_state["data"] = current_df


def haftalik_veri_guncelle(kolon, deger):
  current_df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
  current_df_h["Tarih"] = current_df_h["Tarih"].astype(str)
  if current_df_h[current_df_h["Tarih"] == str_hafta].empty:
    yeni_satir_h = {"Tarih": str_hafta}
    for h in st.session_state["custom_haftalik_goals"].keys():
      yeni_satir_h[h] = 0.0
    current_df_h = pd.concat(
        [current_df_h, pd.DataFrame([yeni_satir_h])], ignore_index=True
    )
  current_df_h.loc[current_df_h["Tarih"] == str_hafta, kolon] = deger
  verileri_kaydet(HAFTALIK_VERI_DOSYASI, current_df_h)
  st.session_state["haftalik_data"] = current_df_h


# --- BUTON TIKLAMA (QUERY PARAMS) YÖNETİMİ ---
if "action_toggle" in st.query_params:
  h_adi = st.query_params["action_toggle"]
  current_df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  if h_adi in current_df.columns:
    mev = current_df.loc[current_df["Tarih"] == str_bugun, h_adi].values[0]
    yeni = 0.0 if mev > 0 else 1.0
    veri_guncelle(h_adi, yeni)
  st.query_params.clear()
  st.rerun()

if "action_inc" in st.query_params:
  h_adi = st.query_params["action_inc"]
  current_df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  if h_adi in current_df.columns:
    mev = current_df.loc[current_df["Tarih"] == str_bugun, h_adi].values[0]
    hedef_sinir = st.session_state["custom_goals"][h_adi].get(
        "hedef_deger", 1.0
    )
    artis = 0.5 if h_adi == "Su Tüketimi" else 1.0
    yeni_deger = mev + artis
    if yeni_deger <= hedef_sinir:
      veri_guncelle(h_adi, yeni_deger)
  st.query_params.clear()
  st.rerun()

if "action_toggle_w" in st.query_params:
  h_adi = st.query_params["action_toggle_w"]
  current_df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
  if h_adi in current_df_h.columns:
    mev = current_df_h.loc[
        current_df_h["Tarih"] == str_hafta, h_adi
    ].values[0]
    yeni = 0.0 if mev > 0 else 1.0
    haftalik_veri_guncelle(h_adi, yeni)
  st.query_params.clear()
  st.rerun()

if "action_inc_w" in st.query_params:
  h_adi = st.query_params["action_inc_w"]
  current_df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
  if h_adi in current_df_h.columns:
    mev = current_df_h.loc[
        current_df_h["Tarih"] == str_hafta, h_adi
    ].values[0]
    hedef_sinir = st.session_state["custom_haftalik_goals"][h_adi].get(
        "hedef_deger", 1.0
    )
    yeni_deger = mev + 1.0
    if yeni_deger <= hedef_sinir:
      haftalik_veri_guncelle(h_adi, yeni_deger)
  st.query_params.clear()
  st.rerun()

# --- ÜST MENÜ / SEKMELER ---
(
    tab_gunluk,
    tab_gunluk_gecmis,
    tab_haftalik_hedefler,
    tab_hedef_yonetimi,
    tab_haftalik_gecmis,
    tab_aylik,
    tab_yillik,
) = st.tabs(
    [
        "📅 Bugün",
        "📊 Günlük Geçmiş",
        "📆 Haftalık Hedefler",
        "⚙️ Hedef Yönetimi",
        "📈 Haftalık Geçmiş",
        "📉 Aylık",
        "🏆 Yıllık",
    ]
)


# ==========================================
# 1. SEKME: BUGÜN
# ==========================================
@st.fragment
def gunluk_hedefler_bileseni():
  st.header("Günlük Hedefler")
  st.caption(f"Tarih: {bugun.strftime('%d.%m.%Y')}")

  current_df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  current_df["Tarih"] = current_df["Tarih"].astype(str)

  if current_df[current_df["Tarih"] == str_bugun].empty:
    yeni_satir = {"Tarih": str_bugun, "Uyku": 7}
    for h in st.session_state["custom_goals"].keys():
      yeni_satir[h] = 0.0
    current_df = pd.concat(
        [current_df, pd.DataFrame([yeni_satir])], ignore_index=True
    )

  aktif_satir = current_df[current_df["Tarih"] == str_bugun].iloc[0]

  for hedef_adi, detay in st.session_state["custom_goals"].items():
    emoji = detay.get("emoji", "🎯")
    renk = detay.get("renk", "#37474F")
    tip = detay.get("tip", "Onay (Tik)")
    hedef_deger = detay.get("hedef_deger", 1.0)
    birim_etiketi = detay.get("birim", "")

    mevcut_deger = (
        aktif_satir[hedef_adi] if hedef_adi in aktif_satir else 0.0
    )
    if pd.isna(mevcut_deger):
      mevcut_deger = 0.0

    tamamlandi = mevcut_deger >= hedef_deger

    if tip == "Onay (Tik)":
      durum_metni = "Her gün, Tamamlandı" if tamamlandi else "Her gün, 0/1"
      buton_sembol = "✓" if tamamlandi else "+"
      param_adi = "action_toggle"
    else:
      durum_metni = (
          f"Her gün, {mevcut_deger:g}/{hedef_deger:g} {birim_etiketi}"
      )
      if tamamlandi:
        buton_sembol = "✓"
        param_adi = ""  # Hedef doldu, işlem yapılmasın
      else:
        buton_sembol = "+"
        param_adi = "action_inc"

    su_cubugu_html = ""
    if hedef_adi == "Su Tüketimi" or (
        tip == "Miktar (Sayısal)" and birim_etiketi in ["L", "lt", "litre"]
    ):
      yuzde = (
          min(int((mevcut_deger / hedef_deger) * 100), 100)
          if hedef_deger > 0
          else 0
      )
      su_cubugu_html = f'<div style="background-color: rgba(255, 255, 255, 0.3); border-radius: 6px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden;"><div style="height: 100%; background: linear-gradient(90deg, #ffffff 0%, #e0f7fa 100%); border-radius: 6px; width: {yuzde}%;"></div></div>'

    # Buton HTML yapısı (Eğer hedef tamamlandıysa tıklama engellenir)
    if tamamlandi and tip == "Miktar (Sayısal)":
      buton_html = (
          '<div style="width: 42px; height: 42px; border-radius: 50%;'
          " background-color: rgba(46, 125, 50, 0.6); border: 2px solid"
          ' rgba(255, 255, 255, 0.8); display: flex; align-items: center;'
          " justify-content: center; color: white; font-weight: bold;"
          ' font-size: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">✓</div>'
      )
    else:
      buton_html = (
          f'<a href="?{param_adi}={hedef_adi}" target="_self"'
          ' style="width: 42px; height: 42px; border-radius: 50%;'
          ' background-color: rgba(255, 255, 255, 0.25); border: 2px solid'
          ' rgba(255, 255, 255, 0.6); display: flex; align-items: center;'
          ' justify-content: center; color: white; text-decoration: none;'
          ' font-weight: bold; font-size: 18px; box-shadow: 0 2px 6px'
          f' rgba(0,0,0,0.15);">{buton_sembol}</a>'
      )

    html_kodu = (
        f'<div style="background-color: {renk}; padding: 14px 18px;'
        " border-radius: 20px; color: white; margin-bottom: 12px; box-shadow: 0"
        " 4px 12px rgba(0, 0, 0, 0.2); display: flex; align-items: center;"
        ' justify-content: space-between;">'
        '<div style="display: flex; align-items: center; gap: 14px;'
        ' flex-grow: 1; overflow: hidden;">'
        f'<span style="font-size: 28px; flex-shrink: 0;">{emoji}</span>'
        '<div style="display: flex; flex-direction: column; width: 100%;">'
        f'<div style="font-size: 16px; font-weight: 600; color: white;'
        f' line-height: 1.2;">{hedef_adi}</div>'
        f'<div style="font-size: 12px; opacity: 0.85; color: white;'
        f' margin-top: 3px;">{durum_metni}</div>'
        f"{su_cubugu_html}"
        "</div>"
        "</div>"
        f'<div style="margin-left: 14px; flex-shrink: 0;">{buton_html}</div>'
        "</div>"
    )

    st.markdown(html_kodu, unsafe_allow_html=True)

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


with tab_gunluk:
  gunluk_hedefler_bileseni()


# ==========================================
# 2. SEKME: GÜNLÜK GEÇMİŞ (YENİ İSTATİSTİK)
# ==========================================
with tab_gunluk_gecmis:
  st.header("Geçmiş Günlük Kayıtlar")
  st.caption(
      "Tüm günlere ait girdiğin verileri ve istatistikleri buradan"
      " inceleyebilirsin."
  )
  df_gecmis = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  if not df_gecmis.empty:
    st.dataframe(df_gecmis.sort_values(by="Tarih", ascending=False), use_container_width=True)
  else:
    st.info("Henüz kayıtlı günlük veri bulunmuyor.")


# ==========================================
# 3. SEKME: HAFTALIK HEDEFLER
# ==========================================
with tab_haftalik_hedefler:
  st.header("Haftalık Hedefler")
  st.caption(f"Bu Hafta: {str_hafta}")

  current_df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
  current_df_h["Tarih"] = current_df_h["Tarih"].astype(str)

  if current_df_h[current_df_h["Tarih"] == str_hafta].empty:
    yeni_satir_h = {"Tarih": str_hafta}
    for h in st.session_state["custom_haftalik_goals"].keys():
      yeni_satir_h[h] = 0.0
    current_df_h = pd.concat(
        [current_df_h, pd.DataFrame([yeni_satir_h])], ignore_index=True
    )

  aktif_hafta_satir = current_df_h[current_df_h["Tarih"] == str_hafta].iloc[0]

  for hedef_adi, detay in st.session_state["custom_haftalik_goals"].items():
    emoji = detay.get("emoji", "🎯")
    renk = detay.get("renk", "#1E3A8A")
    tip = detay.get("tip", "Onay (Tik)")
    hedef_deger = detay.get("hedef_deger", 1.0)
    birim_etiketi = detay.get("birim", "")

    mevcut_deger = (
        aktif_hafta_satir[hedef_adi]
        if hedef_adi in aktif_hafta_satir
        else 0.0
    )
    if pd.isna(mevcut_deger):
      mevcut_deger = 0.0

    tamamlandi = mevcut_deger >= hedef_deger

    if tip == "Onay (Tik)":
      durum_metni = "Bu hafta, Tamamlandı" if tamamlandi else "Bu hafta, 0/1"
      buton_sembol = "✓" if tamamlandi else "+"
      param_adi = "action_toggle_w"
    else:
      durum_metni = (
          f"Bu hafta, {mevcut_deger:g}/{hedef_deger:g} {birim_etiketi}"
      )
      if tamamlandi:
        buton_sembol = "✓"
        param_adi = ""
      else:
        buton_sembol = "+"
        param_adi = "action_inc_w"

    prog_bar_html = ""
    if tip == "Miktar (Sayısal)" and hedef_deger > 0:
      yuzde = min(int((mevcut_deger / hedef_deger) * 100), 100)
      prog_bar_html = f'<div style="background-color: rgba(255, 255, 255, 0.3); border-radius: 6px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden;"><div style="height: 100%; background: linear-gradient(90deg, #ffffff 0%, #e0f7fa 100%); border-radius: 6px; width: {yuzde}%;"></div></div>'

    if tamamlandi and tip == "Miktar (Sayısal)":
      buton_html_w = (
          '<div style="width: 42px; height: 42px; border-radius: 50%;'
          " background-color: rgba(30, 58, 138, 0.6); border: 2px solid"
          ' rgba(255, 255, 255, 0.8); display: flex; align-items: center;'
          " justify-content: center; color: white; font-weight: bold;"
          ' font-size: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">✓</div>'
      )
    else:
      buton_html_w = (
          f'<a href="?{param_adi}={hedef_adi}" target="_self"'
          ' style="width: 42px; height: 42px; border-radius: 50%;'
          ' background-color: rgba(255, 255, 255, 0.25); border: 2px solid'
          ' rgba(255, 255, 255, 0.6); display: flex; align-items: center;'
          ' justify-content: center; color: white; text-decoration: none;'
          ' font-weight: bold; font-size: 18px; box-shadow: 0 2px 6px'
          f' rgba(0,0,0,0.15);">{buton_sembol}</a>'
      )

    html_kodu_w = (
        f'<div style="background-color: {renk}; padding: 14px 18px;'
        " border-radius: 20px; color: white; margin-bottom: 12px; box-shadow: 0"
        " 4px 12px rgba(0, 0, 0, 0.2); display: flex; align-items: center;"
        ' justify-content: space-between;">'
        '<div style="display: flex; align-items: center; gap: 14px;'
        ' flex-grow: 1; overflow: hidden;">'
        f'<span style="font-size: 28px; flex-shrink: 0;">{emoji}</span>'
        '<div style="display: flex; flex-direction: column; width: 100%;">'
        f'<div style="font-size: 16px; font-weight: 600; color: white;'
        f' line-height: 1.2;">{hedef_adi}</div>'
        f'<div style="font-size: 12px; opacity: 0.85; color: white;'
        f' margin-top: 3px;">{durum_metni}</div>'
        f"{prog_bar_html}"
        "</div>"
        "</div>"
        f'<div style="margin-left: 14px; flex-shrink: 0;">{buton_html_w}</div>'
        "</div>"
    )

    st.markdown(html_kodu_w, unsafe_allow_html=True)


# ==========================================
# 4. SEKME: HEDEF YÖNETİMİ
# ==========================================
with tab_hedef_yonetimi:
  st.header("Hedefleri ve Görsel Detayları Düzenle")

  hedef_turu_secimi = st.radio(
      "Yönetilecek Hedef Kategorisi", ["Günlük Hedefler", "Haftalık Hedefler"]
  )

  if hedef_turu_secimi == "Günlük Hedefler":
    st.subheader("Günlük Yeni Hedef Ekle")
    with st.form("yeni_hedef_form"):
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

      hedef_ekle_buton = st.form_submit_button("Günlük Hedef Ekle")

      if hedef_ekle_buton and yeni_ad:
        if yeni_ad not in st.session_state["custom_goals"]:
          st.session_state["custom_goals"][yeni_ad] = {
              "emoji": yeni_emoji,
              "renk": yeni_renk,
              "tip": yeni_tip,
              "hedef_deger": yeni_hedef_deger,
              "birim": yeni_birim,
          }
          hedefleri_kaydet(HEDEF_DOSYASI, st.session_state["custom_goals"])

          current_df = verileri_yukle(VERI_DOSYASI, ["Uyku"])
          if yeni_ad not in current_df.columns:
            current_df[yeni_ad] = 0.0
            verileri_kaydet(VERI_DOSYASI, current_df)

          st.success(
              f"'{yeni_emoji} {yeni_ad}' başarıyla eklendi ve kaydedildi!"
          )
          st.rerun()
        else:
          st.warning("Bu isimde bir günlük hedef zaten var.")

    st.divider()
    st.subheader("Mevcut Günlük Hedefleri Yönet")
    if st.session_state["custom_goals"]:
      silinecek_hedef = st.selectbox(
          "Silinecek günlük hedefi seç:",
          list(st.session_state["custom_goals"].keys()),
          key="del_daily",
      )
      if st.button("Seçili Günlük Hedefi Kalıcı Olarak Sil"):
        if len(st.session_state["custom_goals"]) > 1:
          del st.session_state["custom_goals"][silinecek_hedef]
          hedefleri_kaydet(HEDEF_DOSYASI, st.session_state["custom_goals"])
          st.success(f"'{silinecek_hedef}' kalıcı olarak silindi.")
          st.rerun()
        else:
          st.error("En az bir günlük hedef kalmak zorunda.")

  else:
    st.subheader("Haftalık Yeni Hedef Ekle")
    with st.form("yeni_haftalik_hedef_form"):
      col_wh1, col_wh2 = st.columns(2)
      with col_wh1:
        yeni_w_ad = st.text_input("Haftalık Hedef Adı")
        yeni_w_emoji = st.text_input("Emoji", value="⚡")
      with col_wh2:
        yeni_w_tip = st.selectbox(
            "Hedef Tipi", ["Onay (Tik)", "Miktar (Sayısal)"], key="w_tip"
        )
        yeni_w_renk = st.color_picker("Hedef Rengi", value="#1E3A8A", key="w_col")

      yeni_w_birim = ""
      yeni_w_hedef_deger = 1.0
      if yeni_w_tip == "Miktar (Sayısal)":
        col_wb1, col_wb2 = st.columns(2)
        with col_wb1:
          yeni_w_birim = st.text_input("Birim (Örn: gün, saat)", value="gün")
        with col_wb2:
          yeni_w_hedef_deger = st.number_input(
              "Hedeflenen Miktar", min_value=0.1, value=4.0, key="w_val"
          )

      hedef_w_ekle_buton = st.form_submit_button("Haftalık Hedef Ekle")

      if hedef_w_ekle_buton and yeni_w_ad:
        if yeni_w_ad not in st.session_state["custom_haftalik_goals"]:
          st.session_state["custom_haftalik_goals"][yeni_w_ad] = {
              "emoji": yeni_w_emoji,
              "renk": yeni_w_renk,
              "tip": yeni_w_tip,
              "hedef_deger": yeni_w_hedef_deger,
              "birim": yeni_w_birim,
          }
          hedefleri_kaydet(
              HAFTALIK_HEDEF_DOSYASI, st.session_state["custom_haftalik_goals"]
          )

          current_df_h = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
          if yeni_w_ad not in current_df_h.columns:
            current_df_h[yeni_w_ad] = 0.0
            verileri_kaydet(HAFTALIK_VERI_DOSYASI, current_df_h)

          st.success(
              f"'{yeni_w_emoji} {yeni_w_ad}' başarıyla eklendi ve"
              " kaydedildi!"
          )
          st.rerun()
        else:
          st.warning("Bu isimde bir haftalık hedef zaten var.")

    st.divider()
    st.subheader("Mevcut Haftalık Hedefleri Yönet")
    if st.session_state["custom_haftalik_goals"]:
      silinecek_w_hedef = st.selectbox(
          "Silinecek haftalık hedefi seç:",
          list(st.session_state["custom_haftalik_goals"].keys()),
          key="del_weekly",
      )
      if st.button("Seçili Haftalık Hedefi Kalıcı Olarak Sil"):
        if len(st.session_state["custom_haftalik_goals"]) > 1:
          del st.session_state["custom_haftalik_goals"][silinecek_w_hedef]
          hedefleri_kaydet(
              HAFTALIK_HEDEF_DOSYASI, st.session_state["custom_haftalik_goals"]
          )
          st.success(f"'{silinecek_w_hedef}' kalıcı olarak silindi.")
          st.rerun()
        else:
          st.error("En az bir haftalık hedef kalmak zorunda.")


# ==========================================
# 5. SEKME: HAFTALIK GEÇMİŞ
# ==========================================
with tab_haftalik_gecmis:
  st.header("Haftalık Geçmiş Tablosu")
  df_w_tab = verileri_yukle(HAFTALIK_VERI_DOSYASI, [])
  if not df_w_tab.empty and len(df_w_tab.columns) > 1:
    st.dataframe(df_w_tab, use_container_width=True)
  else:
    st.info("Henüz yeterli haftalık veri girilmedi.")


# ==========================================
# 6. SEKME: AYLIK İSTATİSTİKLER
# ==========================================
with tab_aylik:
  st.header("Aylık Rapor")
  df_m = verileri_yukle(VERI_DOSYASI, ["Uyku"])
  if not df_m.empty and "Uyku" in df_m.columns:
    ortalama_uyku = df_m["Uyku"].mean()
    st.metric("😴 Ortalama Uyku Süresi", f"{ortalama_uyku:.1f} Saat")
  else:
    st.info("Henüz yeterli veri bulunmuyor.")


# ==========================================
# 7. SEKME: YILLIK İSTATİSTİKLER
# ==========================================
with tab_yillik:
  st.header("Yıllık Büyük Resim")
  st.info("Uzun vadeli disiplin ve istikrar paneli.")
