# Smart English Journey

An isolated A1/A2 learning path for ABCZ. Existing phonics and foundation URLs are unchanged.

## Enable locally

Set `ENGLISH_PATH_ENABLED=true`, then run:

```powershell
python manage.py migrate
python manage.py runserver
```

Open `/english/`. Personal pages require an authenticated user.

## Routes

- `/english/` — public journey overview
- `/english/dashboard/` — daily quest and skill summary
- `/english/a1/` and `/english/a2/` — mastery-gated level maps
- `/english/unit/<unit>/` — six-stage lesson flow
- `/english/review/` — spaced review queue
- `/english/assessment/` — six-skill diagnostic

Unit content lives in `services/curriculum.py`. Progress and review scheduling live in `services/progress.py`; this keeps the first curriculum release data-driven without duplicating existing ABCZ pages.

## Authored reference unit

`A1.1 Hello!` remains the quality reference, but now runs through the same component-based engine as A1.2-A1.10. Authored units live in `services/units/`; shared components live in `templates/english_path/components/`, with `unit.css` and `unit.js` serving every unit.

The A1.1 quiz is the only route allowed to award A1.1 mastery. Incorrect answers return a targeted explanation and a server-checked similar question, and are also added to the learner's spaced-review queue. Keep `ENGLISH_PATH_ENABLED=false` until the complete registration-to-payment-to-access flow has passed release QA.

## Paid entitlement

`A1.1` is the authenticated free trial. `A1.2` through `A2.10`, both final challenges,
and their review material require the active `english_journey` subscription. Its
server-owned catalog price is 39 SAR for 30 days and it uses the existing ABCZ
`PaymentOrder`/`UserSubscription` checkout and activation flow. Subscription access
and educational progression are checked independently. The plan and its checkout
remain hidden while `ENGLISH_PATH_ENABLED=false`.
