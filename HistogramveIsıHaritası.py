import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyodbc

# Veritabanı bağlantısı
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-BS7RKV3;DATABASE=PUSULA;UID=sa;PWD=1234;Encrypt=no')
    cursor = conn.cursor()
    print("Connected")

except pymssql.Error as e:
    print("Bağlantı hatası:", e)
    exit;
query = "SELECT [Kullanici_id], [Cinsiyet], [Dogum_Tarihi], [Uyruk], [Il], [Ilac_Adi], [Ilac_Baslangic_Tarihi], [Ilac_Bitis_Tarihi], [Yan_Etki], [Yan_Etki_Bildirim_Tarihi], [Alerjilerim], REPLACE([KronikHastaliklarim],' ','') 'KronikHastaliklarim', [Baba_Kronik_Hastaliklari], [Anne_Kronik_Hastaliklari], [Kiz_Kardes_Kronik_Hastaliklari], [Erkek_Kardes_Kronik_Hastaliklari], replace([Kan_Grubu],' ','') 'Kan_Grubu', [Kilo], [Boy] FROM [PUSULA].[dbo].[HastaBilgileri]"
df = pd.read_sql(query, conn)

# Bağlantıyı kapatma
conn.close()

# Veri temizleme (gerekirse)
df['KronikHastaliklarim'] = df['KronikHastaliklarim'].str.split(',')  # Kronik hastalıkları listeye çevir
df = df.explode('KronikHastaliklarim')  # Her hastalığı ayrı bir satıra getir

# Kan grubuna göre kronik hastalıkların sıklığını hesapla
plt.figure(figsize=(12, 6))
sns.countplot(data=df, x='KronikHastaliklarim', hue='Kan_Grubu', palette='viridis')
plt.title('Kan Gruplarına Göre Kronik Hastalıkların Dağılımı')
plt.xlabel('Kronik Hastalık')
plt.ylabel('Sıklık')
plt.xticks(rotation=45)
plt.legend(title='Kan Grubu')
plt.show()

# Isı haritası için pivot tablo oluştur
pivot_table = df.pivot_table(index='KronikHastaliklarim', columns='Kan_Grubu', aggfunc='size', fill_value=0)

# Isı haritasını oluştur
plt.figure(figsize=(10, 6))
sns.heatmap(pivot_table, annot=True, cmap='YlGnBu')
plt.title('Kan Grubuna Göre Kronik Hastalıkların Dağılımı')
plt.xlabel('Kan Grubu')
plt.ylabel('Kronik Hastalık')
plt.show()
