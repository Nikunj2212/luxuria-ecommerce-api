from django.shortcuts import render, redirect
from .models import ContactThread, ContactMessage
from django.shortcuts import get_object_or_404, redirect


def contact_view(request):

    # AUTHENTICATED USER
    if request.user.is_authenticated and not request.user.is_staff:

        if request.method == 'POST':
            message = request.POST.get("message")

            # ALWAYS CREATE NEW THREAD
            thread = ContactThread.objects.create(
                user=request.user,
                subject="Support Query",
                status='open'
            )

            ContactMessage.objects.create(
                thread=thread,
                sender='user',
                message=message
            )

            return redirect('accounts:ticket_detail', thread_id=thread.id)

        return render(request, 'pages/contact.html')

    # GUEST USER FLOW
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        thread = ContactThread.objects.create(
            user=None,
            guest_name=name,
            guest_email=email,
            subject="Guest Support Query",
            status='open'
        )

        ContactMessage.objects.create(
            thread=thread,
            sender='user',
            message=message
        )

        return redirect('contact_success')

    return render(request, 'pages/contact.html')

def thread_list(request):
    threads = ContactThread.objects.filter(messages__isnull=False).distinct().order_by('-created_at')
    return render(request, 'contact/admin_threads.html', {'threads': threads})


def thread_detail(request, thread_id):
    thread = get_object_or_404(ContactThread, id=thread_id)
    msgs = thread.messages.all().order_by('created_at')

    if request.method == 'POST' and thread.status == 'open':
        reply = request.POST.get('reply')
        if reply and reply.strip() != "":
            ContactMessage.objects.create(
                thread=thread,
                sender='admin',
                message=reply
            )
        return redirect('dashboard:dashboard_support_detail', thread_id=thread_id)

    return render(request, 'contact/admin_thread_detail.html', {
        'thread': thread,
        'messages': msgs,
    })

# USER

def my_threads(request):
    threads = ContactThread.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'contact/my_threads.html', {'threads': threads})



def my_thread_detail(request, thread_id):
    thread = ContactThread.objects.get(id=thread_id, user=request.user)
    msgs = thread.messages.all().order_by('created_at')

    if request.method == 'POST':
        reply = request.POST.get('reply')
        ContactMessage.objects.create(
            thread=thread,
            sender='user',
            message=reply
        )
        return redirect('my_thread_detail', thread_id=thread_id)

    return render(request, 'contact/my_thread_detail.html', {
        'thread': thread,
        'messages': msgs
    })
    


def contact_success(request):
    return render(request, 'contact/contact_success.html')


def close_thread(request, thread_id):
    thread = get_object_or_404(ContactThread, id=thread_id)
    thread.status = 'closed'
    thread.save()
    return redirect('dashboard:dashboard_support')