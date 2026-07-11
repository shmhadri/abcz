# Controlled Load Testing

هذه الأدوات مخصصة لاختبار التحمل على بيئة محلية أو staging فقط. لا تشغلها على الإنتاج إلا بعد موافقة صريحة وخطة مراقبة وإيقاف.

## Safety

- العنوان الإنتاجي `https://abcz-epbz.onrender.com` محظور افتراضيًا.
- لا تستخدم مستخدمين حقيقيين.
- لا تختبر الدفع الحقيقي أو Webhook حقيقي.
- بيانات الاختبار تحمل prefix آمن وتستخدم بريد `@loadtest.local`.
- التنظيف يحذف فقط المستخدمين الذين يطابقون prefix آمن وبريد load-test.

## Install Locust

```powershell
python -m pip install "locust>=2,<3"
```

## Create Test Data

الأمر التالي ينشئ العدد لكل دور مصادق عليه: Basic وSilver وDiamond وLevel 3 وLevel 4.

```powershell
python manage.py create_load_test_data --users 300 --prefix loadtest_run1_ --password "LoadTestPass123!"
```

لـ 300 مستخدم متزامن تقريبًا مع التوزيع الافتراضي، اجعل `--users` لا يقل عن أكبر عدد متوقع في دور واحد. مثال: 300 إجمالي يعني Silver 90 تقريبًا، لكن `--users 300` يعطي هامشًا جيدًا.

## Run Locust

```powershell
$env:LOAD_TEST_BASE_URL="http://127.0.0.1:8000"
$env:LOAD_TEST_USERNAME_PREFIX="loadtest_run1_"
$env:LOAD_TEST_PASSWORD="LoadTestPass123!"
$env:LOAD_TEST_RUN_ID="local-run1"
locust -f load_tests/locustfile.py --headless -u 50 -r 5 -t 5m --csv load_tests/reports/local-run1
```

## Ramp Plan

ابدأ تدريجيًا ولا تقفز مباشرة إلى 3000 مستخدم:

```powershell
locust -f load_tests/locustfile.py --headless -u 25 -r 5 -t 3m --csv load_tests/reports/smoke-25
locust -f load_tests/locustfile.py --headless -u 100 -r 10 -t 10m --csv load_tests/reports/baseline-100
locust -f load_tests/locustfile.py --headless -u 300 -r 20 -t 15m --csv load_tests/reports/load-300
locust -f load_tests/locustfile.py --headless -u 600 -r 30 -t 20m --csv load_tests/reports/load-600
```

## Scenario Mix

- Visitor: 30%
- Silver: 30%
- Level 3: 15%
- Level 4: 15%
- Diamond: 10%

## Production Guard

الإنتاج محظور افتراضيًا. فتح الحظر يحتاج متغيرًا صريحًا:

```powershell
$env:ALLOW_PRODUCTION_LOAD_TEST="true"
```

لا تستخدم هذا المتغير إلا بعد تجهيز staging أو نافذة اختبار رسمية ومراقبة Render/PostgreSQL وخطة rollback.

## Cleanup

Dry run:

```powershell
python manage.py cleanup_load_test_data --prefix loadtest_run1_
```

حذف فعلي:

```powershell
python manage.py cleanup_load_test_data --prefix loadtest_run1_ --yes
```

## Analyze Results

بعد انتهاء Locust سيخرج ملفات مثل `load_tests/reports/load-300_stats.csv`. لتحويلها إلى ملخص:

```powershell
python load_tests/analyze_results.py load_tests/reports/load-300_stats.csv
```
