# LeadPulse AI - Backend Altyapısı (Gün 1)

Kişiselleştirilmiş B2B Satış ve Outreach Asistanı (LeadPulse AI) için FastAPI, PostgreSQL (Supabase) ve SQLAlchemy/Alembic tabanlı backend mimarisi.

---

## 📁 Proje Dizin Yapısı

```text
backend/
├── alembic/
│   ├── versions/           # Veritabanı revizyon / migration dosyaları
│   │   └── .gitkeep
│   ├── env.py              # Alembic ortam ve model meta-data yapılandırması
│   └── script.py.mako      # Migration şablonu
├── app/
│   ├── models/             # SQLAlchemy ORM Tablo Modelleri
│   │   ├── __init__.py     # Base, Lead, GeneratedMessage dışa aktarımı
│   │   ├── lead.py         # Lead tablosu
│   │   └── message.py      # GeneratedMessage tablosu
│   ├── routers/            # FastAPI Endpoint Yönlendiricileri
│   │   ├── __init__.py
│   │   ├── health.py       # Health check & veritabanı bağlantı testi
│   │   ├── leads.py        # Lead CRUD işlemleri
│   │   └── messages.py     # Üretilen outreach mesajları endpoint'leri
│   ├── schemas/            # Pydantic v2 Veri Doğrulama Şemaları
│   │   ├── __init__.py
│   │   ├── lead.py         # LeadBase, LeadCreate, LeadResponse
│   │   └── message.py      # GeneratedMessageBase, Create, Response
│   ├── __init__.py
│   ├── config.py           # Pydantic Settings & Ortam Değişkenleri
│   ├── database.py         # SQLAlchemy Engine, SessionLocal & get_db Dependency
│   └── main.py             # FastAPI App, CORS ve Route Tanımları
├── .env.example            # Supabase PostgreSQL bağlantı örneği
├── .gitignore              # Python ve ortam dosyaları için ignore kuralı
├── alembic.ini             # Alembic ana yapılandırma dosyası
├── requirements.txt        # Python bağımlılıkları
└── README.md               # Kurulum ve çalıştırma kılavuzu
```

---

## 🚀 Hızlı Başlangıç & Kurulum Adımları

### 1. Sanal Ortam (Virtual Environment) Oluşturma

```powershell
# backend dizinine geçin
cd backend

# Sanal ortamı oluşturun
python -m venv venv

# Windows PowerShell üzerinde sanal ortamı aktif edin:
.\venv\Scripts\Activate.ps1

# (Eğer betik çalıştırma kısıtlaması uyarısı alırsanız: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process)
```

### 2. Bağımlılıkları Yükleme

```powershell
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Tanımlama (.env)

`.env.example` dosyasını `.env` olarak kopyalayın:

```powershell
cp .env.example .env
```

`.env` dosyasını açıp Supabase PostgreSQL bağlantı adresinizi girin:

```env
DATABASE_URL="postgresql://postgres:[SUPABASE_SIFRENIZ]@db.[PROJECT_REF].supabase.co:5432/postgres"
```

> 💡 **Supabase İpucu:** 
> - Doğrudan bağlantı için port `5432` kullanılır (`db.[PROJECT_REF].supabase.co:5432/postgres`).
> - Eğer IPv4 / Havuzlayıcı (Connection Pooler) kullanıyorsanız session mode `5432` veya transaction mode `6543` kullanabilirsiniz.
> - `app/config.py` içinde olası `postgres://` formatı otomatik olarak SQLAlchemy uyumlu `postgresql://` formatına dönüştürülür.

---

## 🗄️ Veritabanı Senkronizasyonu (Alembic Migrations)

Alembic `app/models` ve `app/database.py` üzerindeki `Base.metadata`'yı otomatik algılayacak şekilde yapılandırılmıştır.

### 1. İlk Migration Dosyasını Otomatik Üretme (Auto-generate)

```powershell
alembic revision --autogenerate -m "create leads and generated_messages tables"
```

Bu komut `backend/alembic/versions/` altında yeni bir migration dosyası oluşturur ve `leads` ile `generated_messages` tablolarını, index'leri ve foreign key kısıtlamalarını ekler.

### 2. Migration'ı Supabase / Veritabanına Uygulama

```powershell
alembic upgrade head
```

Artık Supabase veritabanınızda tablolar hazırdır!

### Diğer Faydalı Alembic Komutları:
- **Mevcut versiyon durumunu görme:** `alembic current`
- **Migration geçmişini görme:** `alembic history --verbose`
- **Geri alma (Rollback):** `alembic downgrade -1`

---

## 🌐 FastAPI Sunucusunu Başlatma

Geliştirme sunucusunu hot-reload ile başlatmak için:

```powershell
uvicorn app.main:app --reload --port 8000
```

### 🔗 Erişim Adresleri:
- **Ana Sayfa:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger / OpenAPI Etkileşimli Dokümantasyon:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Dokümantasyon:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Sağlık Kontrolü (Health Check):** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **DB Bağlantı Testi:** [http://127.0.0.1:8000/health/db](http://127.0.0.1:8000/health/db)
