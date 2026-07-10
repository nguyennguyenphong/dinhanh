# Path: accounts/views/login.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from accounts.application.dtos.login import LoginDTO
from accounts.exceptions.exception import AccountDomainError
from accounts.policies.login_policy import LoginPolicy
from accounts.providers.login import LoginProvider
from accounts.views.forms.login_base_form import LoginBaseForm


@sensitive_post_parameters("password")
@csrf_protect
def login(request):
    """
    Handles HTTP GET and POST operations to authenticate user profiles.
    Optimized dynamic redirection ensures the user lands on the requested target
    captured dynamically from POST, GET, or role-based fallbacks.
    """
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = LoginBaseForm(request.POST)
        if form.is_valid():
            dto = LoginDTO(
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
            )
            try:
                user_entity = LoginProvider.authenticate_user().execute(
                    dto, request=request
                )

                User = get_user_model()
                django_user = User.objects.get(pk=user_entity.id)
                django_login(request, django_user)

                # Priority: POST parameter -> GET query string fallback
                redirect_to = request.POST.get("next", request.GET.get("next", ""))

                # Guard against malicious Open Redirect phishing vectors
                if redirect_to:
                    is_safe_target = url_has_allowed_host_and_scheme(
                        url=redirect_to,
                        allowed_hosts={request.get_host()},
                        require_https=request.is_secure(),
                    )
                    if is_safe_target:
                        return redirect(redirect_to)

                if LoginPolicy.is_administrative_user(user_entity):
                    return redirect("dashboard")
                elif LoginPolicy.is_standard_client(user_entity):
                    return redirect("tenant_list")

                return redirect("dashboard")

            except AccountDomainError as e:
                form.add_error(None, str(e))
                messages.error(request, str(e))
    else:
        form = LoginBaseForm()

    context = {"form": form, "next": request.GET.get("next", "")}
    return render(request, "pages/auth/login.html", context)
