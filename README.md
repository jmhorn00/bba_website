# BBA CPAs Website

Brunner, Blackstone & Associates, PC — full CPA firm website built with Django + Wagtail + Tailwind CSS + HTMX + Stripe.

**Stack:** Django 5 · Wagtail 6 · Tailwind CSS 3 · HTMX · Stripe Checkout · Postgres · Gunicorn · Nginx · Docker Compose

---

## 1. Local Development

### Prerequisites
- Docker and Docker Compose installed
- Node.js (for Tailwind CSS compilation outside Docker)

### First-time setup

```bash
# 1. Clone the repo and enter the project
cd bba_website

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your actual values (see Environment Variables section)

# 3. Start services
docker compose up --build

# 4. In a separate terminal, run migrations and load seed data
docker compose exec app python manage.py load_initial_data

# 5. Create an admin user
docker compose exec app python manage.py createsuperuser
```

The site runs at **http://localhost:8000**
The Wagtail admin is at **http://localhost:8000/cms/**

### Tailwind CSS (development watch mode)

Tailwind is compiled inside Docker during the image build. For live reloading during development:

```bash
# Inside the app container
docker compose exec app python manage.py tailwind start
```

Or on your host machine:
```bash
cd app/theme/static_src
npm install
npm run start
```

---

## 2. Wagtail Admin

1. Go to `http://localhost:8000/cms/`
2. Log in with the superuser credentials you created
3. Use the **Pages** menu in the sidebar to navigate the page tree
4. Click any page to view it; click **Edit** to modify content
5. Click **Publish** to make changes live

The admin shows a welcome panel with common tasks.

---

## 3. Production Deployment

### Build and start

```bash
# 1. Copy env file and configure for production
cp .env.example .env
# Set DEBUG=False, real SECRET_KEY, Stripe live keys, etc.

# 2. Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# 3. Run migrations (happens automatically via entrypoint.sh)
# 4. Load initial content (first deploy only)
docker compose -f docker-compose.prod.yml exec app python manage.py load_initial_data

# 5. Create superuser
docker compose -f docker-compose.prod.yml exec app python manage.py createsuperuser
```

### Static files
Static files are automatically collected by `entrypoint.sh` and served by Nginx.

### SSL / HTTPS
Place your SSL certificates in `nginx/ssl/` and update `nginx/nginx.conf` to add an HTTPS server block.
Point your domain's DNS A record to your server IP, then use Let's Encrypt (certbot) for free certificates.

---

## 4. Environment Variables

| Variable | Description |
|---|---|
| `DEBUG` | Set `True` for development, `False` for production |
| `SECRET_KEY` | Django secret key — generate a long random string |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames |
| `DATABASE_URL` | Postgres connection string |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Postgres credentials |
| `RESEND_API_KEY` | Get from [resend.com/api-keys](https://resend.com/api-keys) |
| `CONTACT_EMAIL` | Where contact form submissions are sent |
| `STRIPE_PUBLISHABLE_KEY` | From Stripe Dashboard → Developers → API Keys |
| `STRIPE_SECRET_KEY` | From Stripe Dashboard (keep secret!) |
| `STRIPE_WEBHOOK_SECRET` | From Stripe Dashboard → Webhooks (after creating endpoint) |
| `WAGTAIL_SITE_NAME` | Displayed in the Wagtail admin header |
| `WAGTAILADMIN_BASE_URL` | Full URL of the site, used for Wagtail admin links |
| `CACHE_TIMEOUT` | Seconds to cache the newsletter RSS feed (default 3600) |

---

## 5. Editing Content (No Developer Needed)

### Homepage hero
1. CMS → Pages → Home → Edit
2. Update **Hero Headline**, **Hero Subheadline**, stats, CTA text
3. Publish

### Services
1. CMS → Pages → Home → Services → Edit
2. In the **Services** StreamField, add/remove/reorder service cards
3. Each card has: icon (emoji), title, description, link text

### Team members
1. CMS → Pages → Home → Edit
2. Scroll to **Team Members** section
3. Add member with initials, name, title, bio, and optional photo

### Newsletter articles (manual)
1. CMS → Pages → Home → Newsletters → Edit
2. In the **Newsletters** StreamField, add articles with title, date, excerpt, URL
3. Alternatively, paste an RSS feed URL in the **Newsletter Feed URL** field

### Job postings
1. CMS → Pages → Home → Careers → Edit
2. In **Open Positions**, add job with title, type, description, requirements
3. Leave **Open Positions** empty to show the "no openings" fallback message

### Links page
1. CMS → Pages → Home → Links → Edit
2. Each **Link Group** has a heading and a list of links
3. Add groups and links as needed

---

## 6. Adding a New Calculator

1. Open `app/calculators/registry.py`
2. Add a new dict to the `CALCULATORS` list:
   ```python
   {
       'slug': 'my-calculator',
       'title': 'My Calculator Title',
       'description': 'Short description shown on the card.',
       'category': 'savings',  # savings | tax | retirement | payroll | investment
   },
   ```
3. Add the input fields to `app/calculators/templates/calculators/partials/_fields.html`:
   ```html
   {% elif slug == 'my-calculator' %}
   <div><label>Input Label</label><input type="number" name="my_field" value="1000"></div>
   ```
4. Add the calculation function to `app/calculators/logic.py`:
   ```python
   def my_calculator(post):
       value = float(post.get('my_field', 0))
       result = value * 2
       return {'Result': fmt(result)}
   ```
5. Register it in the dispatch table at the bottom of `logic.py`:
   ```python
   CALC_FUNCTIONS = {
       ...
       'my-calculator': my_calculator,
   }
   ```

---

## 7. ShareFile Setup

When the ShareFile URL changes (e.g. a new client portal subdomain):

1. CMS → Pages → Home → Resource Center → Edit
2. Update **ShareFile URL** and **ShareFile Signup URL** fields
3. Publish

The footer and navbar ShareFile links are hardcoded in the templates:
- `app/website/templates/website/partials/_navbar.html`
- `app/website/templates/website/partials/_footer.html`

Search for `sharefile.com` and update those URLs if needed.

---

## 8. Newsletter Feed

To connect a live RSS feed (e.g. Thomson Reuters Checkpoint):

1. CMS → Pages → Home → Newsletters → Edit
2. Paste the RSS feed URL into **Newsletter Feed URL**
3. Publish — the feed is cached for 1 hour (configurable via `CACHE_TIMEOUT` env var)
4. If the feed URL is blank, manually-entered **Newsletter** items are displayed instead

---

## 9. Stripe Setup

### Test mode (development)
1. Create a free account at [stripe.com](https://stripe.com)
2. Dashboard → Developers → API Keys → copy test keys
3. Add to `.env`: `STRIPE_PUBLISHABLE_KEY=pk_test_...` and `STRIPE_SECRET_KEY=sk_test_...`
4. Test card: `4242 4242 4242 4242`, any future expiry, any CVC

### Webhook (required for async payment confirmation)
1. Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://yourdomain.com/pay/webhook/`
3. Events: select `checkout.session.completed`
4. Copy the **Signing Secret** → add to `.env` as `STRIPE_WEBHOOK_SECRET=whsec_...`

### Switching to live mode
1. Dashboard → toggle to **Live mode** (top-left)
2. Copy live API keys (pk_live_... and sk_live_...)
3. Update `.env` with live keys
4. Create a new live webhook endpoint and update `STRIPE_WEBHOOK_SECRET`

---

## 10. Viewing Payment History

1. Log into the Wagtail CMS admin at `/cms/`
2. In the left sidebar, click **Snippets**
3. Click **Payment History**
4. View all payment records with status, client details, and invoice numbers
5. Use the search box and status filter to find specific records

Payments can be filtered by status: Pending, Complete, Failed, Refunded.

---

## Project Structure

```
bba_website/
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
├── .env.example                # Environment variable template
├── nginx/                      # Nginx config + Dockerfile
└── app/
    ├── Dockerfile
    ├── entrypoint.sh           # Runs migrations + collectstatic on start
    ├── requirements.txt
    ├── manage.py
    ├── config/
    │   ├── settings/
    │   │   ├── base.py         # Shared settings
    │   │   ├── development.py
    │   │   └── production.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── home/                   # Wagtail home app (required)
    ├── website/                # Main CMS app — all page models
    │   ├── models.py           # 9 Wagtail page types
    │   ├── blocks.py           # All StreamField blocks
    │   ├── wagtail_hooks.py    # Admin customization
    │   ├── management/commands/load_initial_data.py
    │   └── templates/website/
    ├── contact/                # HTMX contact form
    ├── payments/               # Stripe Checkout payment flow
    ├── calculators/            # 19 financial calculators
    │   ├── registry.py         # Calculator catalog
    │   ├── logic.py            # Server-side calculation functions
    │   └── views.py
    └── theme/                  # django-tailwind CSS pipeline
        └── static_src/
            ├── tailwind.config.js
            └── src/styles.css
```
