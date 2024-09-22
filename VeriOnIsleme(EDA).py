import pandas as pd
import pyodbc
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split


# Veritabanı bağlantısı
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-BS7RKV3;DATABASE=PUSULA;UID=sa;PWD=1234;Encrypt=no')
    cursor = conn.cursor()
    print("Connected")

except pymssql.Error as e:
    print("Bağlantı hatası:", e)
    exit;
query = "SELECT [Kullanici_id], [Cinsiyet], [Dogum_Tarihi], [Uyruk], [Il], [Ilac_Adi], [Ilac_Baslangic_Tarihi], [Ilac_Bitis_Tarihi], [Yan_Etki], [Yan_Etki_Bildirim_Tarihi], [Alerjilerim], REPLACE([KronikHastaliklarim],' ','') 'KronikHastaliklarim', [Baba_Kronik_Hastaliklari], [Anne_Kronik_Hastaliklari], [Kiz_Kardes_Kronik_Hastaliklari], [Erkek_Kardes_Kronik_Hastaliklari], replace([Kan_Grubu],' ','') 'Kan_Grubu', [Kilo], [Boy] FROM [PUSULA].[dbo].[HastaBilgileri]"


# Veriyi yükleme
df = pd.read_sql(query, conn)

# Veriyi gözlemleme (EDA)
print(df.info())  # Veride eksik değerlerin olup olmadığını anlamak için
print(df.describe())  # Sayısal verilerin dağılımı

# 1. Eksik Değerlerin Ele Alınması
# Sayısal kolonlar için ortalama ile doldurma
num_imputer = SimpleImputer(strategy='mean')
df['Kilo'] = num_imputer.fit_transform(df[['Kilo']])
df['Boy'] = num_imputer.fit_transform(df[['Boy']])

# Kategorik kolonlar için en sık değer ile doldurma
cat_imputer = SimpleImputer(strategy='most_frequent')

#Imputer dönüşümünün sonucu numpy array'dir, bu yüzden bunu pandas serisine çevireceğiz
df['Kan_Grubu'] = cat_imputer.fit_transform(df[['Kan_Grubu']]).ravel()

# Alternatif olarak KNNImputer kullanılabilir (komşuluk tabanlı eksik değer doldurma)
# knn_imputer = KNNImputer(n_neighbors=5)
# df[['Kilo', 'Boy']] = knn_imputer.fit_transform(df[['Kilo', 'Boy']])

# 2. Kategorik Değişkenlerin Kodlanması
# Label Encoding (Sıralı kategorik değişkenler için uygundur)
label_encoder = LabelEncoder()
df['Cinsiyet'] = label_encoder.fit_transform(df['Cinsiyet'])

# One-Hot Encoding (Sırasız kategorik değişkenler için uygundur)
onehot_encoder = OneHotEncoder(sparse_output=False)
kan_grubu_encoded = onehot_encoder.fit_transform(df[['Kan_Grubu']])

# Yeni sütunları DataFrame'e ekleyelim
kan_grubu_df = pd.DataFrame(kan_grubu_encoded, columns=onehot_encoder.get_feature_names_out(['Kan_Grubu']))
df = pd.concat([df, kan_grubu_df], axis=1)

# 3. Sayısal Verilerin Normalizasyonu veya Standartlaştırılması
# Standard Scaler (Z-Skoru ile ölçeklendirme)
scaler = StandardScaler()
df[['Kilo', 'Boy']] = scaler.fit_transform(df[['Kilo', 'Boy']])

# Alternatif: MinMaxScaler (0-1 arası ölçeklendirme)
# minmax_scaler = MinMaxScaler()
# df[['Kilo', 'Boy']] = minmax_scaler.fit_transform(df[['Kilo', 'Boy']])

# 4. Aykırı Değerlerin Ele Alınması
# Aykırı değerleri belirlemek için Z-Skoru, IQR (Interquartile Range) gibi yöntemler kullanılabilir
# Aykırı değerlerin gözlemlenmesi ve gerekirse çıkarılması yapılabilir

# Train-test split (Veriyi eğitim ve test setlerine ayırma)
X = df.drop(columns=['KronikHastaliklarim'])  # Özellikler
y = df['KronikHastaliklarim']  # Hedef değişken

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Veri ön işleme tamamlandı ve eğitim/test setlerine ayrıldı.")
