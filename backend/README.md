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

---

## 📋 Gün 2: Lead Modülü API Endpoint'leri

Lead modülü `/api/v1/leads` önekiyle sunulur:

| Metot | Endpoint | Durum | Açıklama |
|---|---|---|---|
| `POST` | `/api/v1/leads/` | `201 Created` | Yeni lead kaydı oluşturur |
| `GET` | `/api/v1/leads/` | `200 OK` | Tüm lead'leri listeler (`skip`, `limit`, `status` filtresi) |
| `GET` | `/api/v1/leads/{lead_id}` | `200 OK` | ID'ye göre tekil lead getirir (404 kontrolü) |
| `PUT` | `/api/v1/leads/{lead_id}` | `200 OK` | Lead bilgilerini ve durumunu günceller |
| `DELETE` | `/api/v1/leads/{lead_id}` | `204 No Content` | Lead'i ve ilişkili mesajları siler |

### Örnek İstekler (cURL):

```bash
# 1. Yeni Lead Oluşturma
curl -X POST "http://127.0.0.1:8000/api/v1/leads/" \
     -H "Content-Type: application/json" \
     -d '{"company_name": "Acme Corp", "company_url": "acme.com", "target_audience": "B2B SaaS Founders", "status": "pending"}'

# 2. Lead Listeleme (Sayfalama ve Durum Filtresi)
curl -X GET "http://127.0.0.1:8000/api/v1/leads/?skip=0&limit=50&status=pending"

# 3. Tekil Lead Getirme
curl -X GET "http://127.0.0.1:8000/api/v1/leads/1"

# 4. Lead Güncelleme
curl -X PUT "http://127.0.0.1:8000/api/v1/leads/1" \
     -H "Content-Type: application/json" \
     -d '{"status": "generated"}'

# 5. Lead Silme
curl -X DELETE "http://127.0.0.1:8000/api/v1/leads/1"
```

---

## 🤖 Day 3: AI Outreach Generation Endpoints

AI-powered outreach generation integrates Google Gemini (`gemini-2.5-flash`) via the `google-genai` SDK:

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/api/v1/leads/{lead_id}/generate` | `201 Created` | Generates a personalized outreach message using Gemini AI, saves it to `generated_messages`, and sets lead status to `generated`. |
| `GET` | `/api/v1/leads/{lead_id}/messages` | `200 OK` | Retrieves all message generation history for a specific lead. |

### Example AI Generation Requests (cURL):

```bash
# 1. Generate a Personalized Cold Email for Lead #1
curl -X POST "http://127.0.0.1:8000/api/v1/leads/1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "outreach_channel": "cold_email",
       "sender_name": "Sarah Connor",
       "sender_company": "LeadPulse AI",
       "value_proposition": "We help sales teams 3x their outbound pipeline with automated personalization.",
       "additional_instructions": "Focus on their recent expansion and keep the tone conversational."
     }'

# 2. Generate a LinkedIn InMail for Lead #1
curl -X POST "http://127.0.0.1:8000/api/v1/leads/1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "outreach_channel": "linkedin",
       "sender_name": "Sarah Connor",
       "sender_company": "LeadPulse AI"
     }'

# 3. List All Messages Generated for Lead #1
curl -X GET "http://127.0.0.1:8000/api/v1/leads/1/messages"
```


