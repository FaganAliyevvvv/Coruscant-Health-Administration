from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import CompleteOrderForm
from .models import ServiceOrder


@role_required(User.Role.DEPARTMENT)
def order_queue(request):
    pending = ServiceOrder.objects.filter(status=ServiceOrder.Status.PENDING).select_related(
        "patient__user", "doctor__user"
    )
    in_progress = ServiceOrder.objects.filter(
        status=ServiceOrder.Status.IN_PROGRESS, assigned_department=request.user
    ).select_related("patient__user", "doctor__user")
    return render(request, "orders/order_queue.html", {"pending": pending, "in_progress": in_progress})


@role_required(User.Role.DEPARTMENT)
def accept_order(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id, status=ServiceOrder.Status.PENDING)
    order.mark_in_progress(request.user)
    messages.success(request, f"Order #{order.id} accepted and marked in progress.")
    return redirect("orders:order_queue")


@role_required(User.Role.DEPARTMENT)
def complete_order(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id, assigned_department=request.user)
    if request.method == "POST":
        form = CompleteOrderForm(request.POST)
        if form.is_valid():
            order.complete(form.cleaned_data["result_text"])
            messages.success(request, f"Order #{order.id} completed and results uploaded.")
            return redirect("orders:order_queue")
    else:
        form = CompleteOrderForm()
    return render(request, "orders/complete_order.html", {"form": form, "order": order})
