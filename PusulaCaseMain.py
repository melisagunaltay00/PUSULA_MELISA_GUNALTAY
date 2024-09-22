import pandas as pd
import pyodbc


# MSSQL bağlantı bilgileri
server = 'DESKTOP-BS7RKV3'
database = 'PUSULA'
user = 'sa'
password = '1234'


# MSSQL'e bağlan
#conn = pymssql.connect(server, user, password, database)
#cursor = conn.cursor()

try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-BS7RKV3;DATABASE=PUSULA;UID=sa;PWD=1234;Encrypt=no')
    cursor = conn.cursor()
    print("Connected")

except pymssql.Error as e:
    print("Bağlantı hatası:", e)
    exit;



# Tablo oluşturma sorgusu (Sütun isimleri ve veri tipleri Excel'deki yapıya göre ayarlanmalıdır)
create_table_query = """
IF NOT EXISTS (select * from sys.objects where name ='HastaBilgileri')
BEGIN
CREATE TABLE dbo.HastaBilgileri (
    Kullanici_id INT NULL ,
    Cinsiyet NVARCHAR(15) NULL,
    Dogum_Tarihi DATE NULL,
    Uyruk NVARCHAR(50) NULL,
    Il NVARCHAR(50) NULL,
    Ilac_Adi NVARCHAR(MAX) NULL,
    Ilac_Baslangic_Tarihi DATE NULL,
    Ilac_Bitis_Tarihi DATE NULL,
    Yan_Etki NVARCHAR(100) NULL,
    Yan_Etki_Bildirim_Tarihi DATETIME NULL,
    Alerjilerim NVARCHAR(100) NULL,
    KronikHastaliklarim NVARCHAR(100) NULL,
    Baba_Kronik_Hastaliklari NVARCHAR(MAX) NULL,
    Anne_Kronik_Hastaliklari NVARCHAR(MAX) NULL,
    Kiz_Kardes_Kronik_Hastaliklari NVARCHAR(MAX) NULL,
    Erkek_Kardes_Kronik_Hastaliklari NVARCHAR(MAX) NULL,
    Kan_Grubu NVARCHAR(10) NULL,
    Kilo NVARCHAR(10) NULL,
    Boy NVARCHAR(10) NULL
)
END
else
BEGIN
   TRUNCATE TABLE dbo.HastaBilgileri
END
"""

print(create_table_query)
cursor.execute(create_table_query)
conn.commit() #herhangi bir execute işleminin işlenmesi için commit yapılıyor.

print('Create Table HastaBilgileri okeyyy')
try:
        # Excel dosyasını oku
    filename ='C:\\Users\\BTI\\Desktop\\side_effect_data 1.xlsx'
    df = pd.read_excel(filename)
    df = df.fillna(value='YOK')
    df['Kilo'] = pd.to_numeric(df['Kilo'], errors='coerce')
    df['Boy'] = pd.to_numeric(df['Boy'], errors='coerce')
    # Parametreli SQL sorgusu oluştur
    insert_query = """
    INSERT INTO HastaBilgileri (
        Kullanici_id, Cinsiyet, Dogum_Tarihi, Uyruk, Il,
         Ilac_Adi,Ilac_Baslangic_Tarihi, Ilac_Bitis_Tarihi, Yan_Etki,
        Yan_Etki_Bildirim_Tarihi, Alerjilerim, KronikHastaliklarim,
        Baba_Kronik_Hastaliklari,Anne_Kronik_Hastaliklari,Kiz_Kardes_Kronik_Hastaliklari, Erkek_Kardes_Kronik_Hastaliklari,
        Kan_Grubu,Kilo, Boy
   
    )
    VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    print(insert_query);
    # Verileri iteratif olarak ekle
    for index, row in df.iterrows():
        # Handle missing Kilo and Boy
        kilo_value = row['Kilo'] if pd.notna(row['Kilo']) else None
        boy_value = row['Boy'] if pd.notna(row['Boy']) else None
        #
        #      
        values = (
            row['Kullanici_id'],
            row['Cinsiyet'],
            row['Dogum_Tarihi'].strftime('%Y-%m-%d') if pd.notna(row['Dogum_Tarihi']) else None,
            row['Uyruk'],
            row['Il'],
            row['Ilac_Adi'],
            row['Ilac_Baslangic_Tarihi'].strftime('%Y-%m-%d') if pd.notna(row['Ilac_Baslangic_Tarihi']) else None,
            row['Ilac_Bitis_Tarihi'].strftime('%Y-%m-%d') if pd.notna(row['Ilac_Bitis_Tarihi']) else None,
            row['Yan_Etki'],
            row['Yan_Etki_Bildirim_Tarihi'].strftime('%Y-%m-%d') if pd.notna(row['Yan_Etki_Bildirim_Tarihi']) else None,
            row['Alerjilerim'],
            row['Kronik Hastaliklarim'],
            row['Baba Kronik Hastaliklari'],
            row['Anne Kronik Hastaliklari'],
            row['Kiz Kardes Kronik Hastaliklari'],
            row['Erkek Kardes Kronik Hastaliklari'],
            row['Kan Grubu'],
            kilo_value,  # Use converted value
            boy_value    # Use converted value
        )
        cursor.execute(insert_query, values)
            # Değişiklikleri kaydet
        conn.commit()

        #row['Kiz Kardes Kronik Hastaliklari']



except pyodbc.Error as e:
    print("Veritabanı hatası:", e)
finally:
    if conn:
        cursor.close()
        conn.close()
#conn.commit()

