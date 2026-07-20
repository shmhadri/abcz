# Staging Deployment and Load Test Checklist

هذا المستند يجهز مرحلة Staging فقط. لا يتم عمل `push` أو `deploy` أو اختبار ضغط على الإنتاج من هذا المستند.

## الهدف

تجهيز بيئة اختبار منفصلة على Render لقياس السعة الحقيقية قبل أي قرار بزيادة `workers` أو إضافة Celery أو الادعاء بتحمل 3000 مستخدم.

## قواعد السلامة

- لا تستخدم قاعدة بيانات الإنتاج.
- لا تنسخ بيانات الطلاب الحقيقية.
- لا تفعل الدفع الحقيقي أو البريد أو الرسائل.
- لا تشغل Locust على `https://abcz-epbz.onrender.com`.
- لا ترفع `WEB_CONCURRENCY` أو `GUNICORN_THREADS` قبل ظهور قياسات من Staging.
- لا تفعل Celery في هذه المرحلة.

## موارد Render المطلوبة

| المورد | الاسم المقترح | ملاحظات |
| --- | --- | --- |
| Web Service | `abcz-staging` | مستقل عن الإنتاج |
| PostgreSQL | `abcz-staging-db` | بيانات اختبار فقط |
| Redis / Key Value | `abcz-staging-redis` | كاش Staging فقط |
| النطاق | `abcz-staging.onrender.com` | يضاف إلى إعدادات الحماية |

## الفرع

يفضل إنشاء فرع Staging بعد مراجعة العمل محليًا:

```powershell
git switch -c staging
git status
```

إذا كان فرع `staging` موجودًا مسبقًا:

```powershell
git switch staging
git status
```

لا تنفذ:

```powershell
git push
```

إلا بعد مراجعة نهائية للمتغيرات والملفات المرحلية.

عند اعتماد القائمة لاحقًا فقط، يكون أمر رفع فرع Staging:

```powershell
git push -u origin staging
```

تأكد قبل ذلك أن خدمة الإنتاج لا تراقب فرع `staging`.

## توليد أسرار Staging

ولد `SECRET_KEY` جديدًا لبيئة Staging فقط:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

لا تحفظ الناتج داخل Git أو `.env.example`.

## متغيرات بيئة Staging

```text
ENVIRONMENT=staging
DEBUG=False
SECRET_KEY=<STAGING_SECRET_KEY>
ALLOWED_HOSTS=abcz-staging.onrender.com
CSRF_TRUSTED_ORIGINS=https://abcz-staging.onrender.com

DATABASE_URL=<STAGING_POSTGRES_INTERNAL_URL>
DB_CONN_MAX_AGE=60

REDIS_URL=<STAGING_REDIS_INTERNAL_URL>
CACHE_KEY_PREFIX=abcz-staging
SUBSCRIPTION_CACHE_TIMEOUT=300
STATIC_CONTENT_CACHE_TIMEOUT=3600
PUBLIC_PAGE_CACHE_TIMEOUT=300

WEB_CONCURRENCY=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=45
GUNICORN_GRACEFUL_TIMEOUT=30
GUNICORN_KEEP_ALIVE=5
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=100

REQUEST_LOG_ENABLED=True
ENABLE_SERVER_TIMING_HEADER=True

MOYASAR_ENABLED=False
MOYASAR_SECRET_KEY=
MOYASAR_PUBLISHABLE_KEY=
MOYASAR_WEBHOOK_SECRET=

EMAIL_ENABLED=False
SMS_ENABLED=False
PUSH_NOTIFICATIONS_ENABLED=False
WHATSAPP_ENABLED=False
```

إذا كانت أسماء متغيرات البريد أو الرسائل مختلفة في المشروع، استخدم نفس الفكرة: تعطيل أي إرسال حقيقي في Staging.

## أوامر Render

Build command:

```bash
bash build.sh
```

Start command:

```bash
sh -c 'gunicorn abcz.wsgi:application --bind 0.0.0.0:${PORT:-8000} --worker-class gthread --workers ${WEB_CONCURRENCY:-2} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-45} --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-30} --keep-alive ${GUNICORN_KEEP_ALIVE:-5} --max-requests ${GUNICORN_MAX_REQUESTS:-1000} --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-100} --access-logfile - --error-logfile -'
```

Health check path:

```text
/health/
```

المتوقع:

- `200` عند سلامة التطبيق وقاعدة البيانات.
- لا يعرض أسرارًا أو مفاتيح.
- أي فشل قاعدة بيانات يظهر كحالة غير صحية بدل خطأ خام.

## فحوص قبل أي Push

```powershell
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --dry-run --noinput
git diff --check
git status
```

## بعد نشر Staging

من Shell الخاص بـ Render Staging فقط:

```bash
python manage.py migrate --noinput
python manage.py check --deploy
python manage.py create_load_test_data --help
python manage.py create_load_test_data --users 100
```

ملاحظة: `--users 100` ينشئ مستخدمين لكل شريحة من شرائح الاختبار، وليس طالبًا واحدًا فقط.

## اختبار وظيفي سريع

افتح Staging يدويًا وتأكد من:

- الصفحة الرئيسية تعمل.
- تسجيل الدخول يعمل.
- صفحة الأسعار تعمل.
- `/sounds/` يعمل.
- `/cvc-reading/` محمي حسب الاشتراك.
- `/english-foundation/` يعمل حسب الاشتراك.
- `/profile/` يعمل للمستخدم المسجل.
- `/api/sounds/progress/` لا يكسر الجلسة أو CSRF.
- Checkout يعرض طرق الدفع بدون تفعيل حقيقي.
- التحويل البنكي يقبل الملفات المسموحة فقط.
- مستوى Silver يفتح المستوى الأول والثاني وأوراق العمل.
- Silver لا يفتح CVC أو المستوى الرابع أو Wordwall أو العصفور الذكي أو الكتاب الكامل.
- `/health/` يرجع حالة سليمة.
- لا توجد أخطاء Console مؤثرة في الصفحات الأساسية.

## إعداد Locust

ثبت Locust محليًا أو على جهاز اختبار منفصل:

```powershell
python -m pip install "locust>=2,<3"
python -m locust --version
```

اضبط الرابط على Staging فقط:

```powershell
$env:LOAD_TEST_BASE_URL="https://abcz-staging.onrender.com"
$env:LOAD_TEST_PASSWORD="LoadTestPass123!"
```

لا تضبط `ALLOW_PRODUCTION_LOAD_TEST=True` لهذه المرحلة.

## تسلسل الضغط

Warm-up:

```powershell
python -m locust `
  -f load_tests/locustfile.py `
  --host "https://abcz-staging.onrender.com" `
  --headless `
  --users 10 `
  --spawn-rate 1 `
  --run-time 2m `
  --csv load_tests/reports/staging_warmup_10
```

25 مستخدمًا:

```powershell
python -m locust `
  -f load_tests/locustfile.py `
  --host "https://abcz-staging.onrender.com" `
  --headless `
  --users 25 `
  --spawn-rate 2 `
  --run-time 5m `
  --csv load_tests/reports/staging_25
```

50 مستخدمًا:

```powershell
python -m locust `
  -f load_tests/locustfile.py `
  --host "https://abcz-staging.onrender.com" `
  --headless `
  --users 50 `
  --spawn-rate 5 `
  --run-time 10m `
  --csv load_tests/reports/staging_50
```

100 مستخدم:

```powershell
python -m locust `
  -f load_tests/locustfile.py `
  --host "https://abcz-staging.onrender.com" `
  --headless `
  --users 100 `
  --spawn-rate 5 `
  --run-time 10m `
  --csv load_tests/reports/staging_100
```

لا تنتقل إلى العدد التالي إلا بعد مراجعة النتائج.

## تحليل النتائج

```powershell
python load_tests/analyze_results.py load_tests/reports/staging_25_stats.csv
python load_tests/analyze_results.py load_tests/reports/staging_50_stats.csv
python load_tests/analyze_results.py load_tests/reports/staging_100_stats.csv
```

سجل من Locust:

- عدد الطلبات.
- RPS.
- Failure rate.
- P50 / P95 / P99.
- Max response time.
- أبطأ endpoint.
- أخطاء 403 / 500 / 502 / 503.
- أخطاء Login أو CSRF أو Sessions.

سجل من Render:

- CPU.
- RAM.
- عدد مرات restart للـworkers.
- أخطاء Web Service.
- PostgreSQL connections: active / idle / limit.
- PostgreSQL locks أو slow queries إن ظهرت.
- Redis memory / clients / evictions / hits / misses عند توفرها.

## معايير النجاح

ينجح المستوى الحالي فقط إذا:

- Failure rate أقل من `1%`.
- لا توجد أخطاء `500/502/503` متكررة.
- `P95` أقل من ثانيتين.
- RAM أقل من `80%`.
- PostgreSQL connections أقل من `80%` من الحد.
- لا توجد إعادة تشغيل غير متوقعة للـworkers.
- لا توجد مشاكل Login أو CSRF أو صلاحيات أو فقدان تقدم.

## معايير الإيقاف

أوقف الاختبار فورًا إذا:

- Failure rate وصل `1%` أو أكثر.
- `P95` تجاوز ثانيتين بشكل مستمر.
- ظهرت أخطاء `500/502/503` متكررة.
- RAM أو PostgreSQL connections تجاوزت `80%`.
- ظهرت Redis evictions مؤثرة.
- حدثت worker restarts.
- ظهرت مشكلة تسجيل دخول أو CSRF أو صلاحيات.

## قالب تقرير الاختبار

| الاختبار | المستخدمون | المدة | الطلبات | RPS | Failure % | P50 | P95 | P99 | Max | القرار |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Warm-up | 10 | 2m |  |  |  |  |  |  |  |  |
| Staging 25 | 25 | 5m |  |  |  |  |  |  |  |  |
| Staging 50 | 50 | 10m |  |  |  |  |  |  |  |  |
| Staging 100 | 100 | 10m |  |  |  |  |  |  |  |  |

| Endpoint | Requests | Failure % | Avg | P95 | P99 | ملاحظة |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
|  |  |  |  |  |  |  |

## قالب القرار

استخدم قرارًا واحدًا فقط بعد كل اختبار:

1. نجاح واضح: ننتقل للعدد التالي.
2. عنق زجاجة في PostgreSQL أو Redis: نعالج الاتصالات والكاش والاستعلامات قبل الزيادة.
3. عنق زجاجة في Web Service: نراجع Gunicorn أو نزيد Web Instances بعد وجود دليل.

لا يوجد قرار اسمه "الموقع يتحمل 3000 مستخدم" بدون اختبار مخصص على بنية مناسبة ومراقبة كاملة.
