from django.contrib import admin
from django.urls import path
from django.http import HttpResponse  # For a simple home view
from stockdata.views import StockDataView

# Define a simple home view
def home_view(request):
    return HttpResponse("<h1>Welcome to Stock Metrics App!</h1><p>Use /api/stock/<symbol>/ to fetch stock data.</p>")

urlpatterns = [
    # Home route
    path('', home_view, name="home"),  # Root URL route

    # Stock data API route
      path('api/stock/<str:symbol>/', StockDataView.as_view(), name="stock-data"),

    # Admin route
    path('admin/', admin.site.urls),  # Admin panel route
]
