# Wordwall Links Import

Use `wordwall_links_sample.csv` as a template only. Replace placeholder rows with reviewed Wordwall links before importing.

Required CSV columns:

```csv
letter,title,url,notes
```

Allowed URL prefixes:

```text
https://wordwall.net/resource/
https://wordwall.net/play/
```

Import command:

```bash
python manage.py import_external_games data/wordwall_links_sample.csv
```

Imported games are saved as `pending`. Review them in Django Admin and set approved items to:

```text
review_status = approved
is_active = True
```
