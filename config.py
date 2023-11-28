import pypyodbc as odbc

#AZURE SQL Server bağlantı dizesi
server = 'ceydabasoglu.database.windows.net'
database = 'ceydabasoglu'
username = 'ceydabasoglu'
password = 'ceyda.123'
driver = '{ODBC Driver 18 for SQL Server}'  # İhtiyaca göre değiştirilebilir


# Bağlantı dizesi oluşturma
conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:ceydabasoglu.database.windows.net,1433;Database=ceydabasoglu;Uid=ceydabasoglu;Pwd=ceyda.123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# Bağlantı oluşturma fonksiyonu
def get_connection():
    try:
        conn = odbc.connect(conn_str)
        print('Azure SQL veritabanına bağlanıldı.')
        return conn
    except Exception as e:
        print('Veritabanına bağlanılamadı:', e)
        return None