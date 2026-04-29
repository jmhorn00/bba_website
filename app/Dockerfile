FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-placeholder-not-for-production \
    DATABASE_URL=sqlite:////tmp/build.db \
    STRIPE_PUBLISHABLE_KEY=pk_test_placeholder \
    STRIPE_SECRET_KEY=sk_test_placeholder \
    STRIPE_WEBHOOK_SECRET=whsec_placeholder \
    RESEND_API_KEY=re_placeholder \
    CONTACT_EMAIL=build@example.com

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm netcat-traditional curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build Tailwind CSS into static files
RUN python manage.py tailwind install --no-input && \
    python manage.py tailwind build --no-input

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
