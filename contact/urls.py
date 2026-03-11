from django.urls import path
from .views import contact_view, contact_success, thread_list, thread_detail, my_threads, my_thread_detail

app_name = "contact"

urlpatterns = [
    path('', contact_view, name='contact'),
    path('success/', contact_success, name='contact_success'),
    path('admin_THREADS/', thread_list, name='contact_messages'),  # tablist
    path('thread/<int:thread_id>/', thread_detail, name='admin_thread_detail'),
    path('my/', my_threads, name='my_threads'),
    path('my/<int:thread_id>/', my_thread_detail, name='my_thread_detail'),
]
