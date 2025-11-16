FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PORT=8000 PRODUCT_URL=http://product_service:8001 CUSTOMER_URL=http://customer_service:8003 ORDER_URL=http://order_service:8004 PAYMENT_URL=http://payment_service:8002 SHIPPING_URL=http://shipping_service:8005 JWT_SECRET=patrones-ut4
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]