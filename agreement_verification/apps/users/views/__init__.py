"""
User authentication views including registration.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from ..forms import UserRegistrationForm


@csrf_exempt
def register_view(request):
    """
    User registration view.
    Handles user registration with form validation.
    Redirects to login page on successful registration.
    """
    if request.user.is_authenticated:
        return redirect('/app/')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(
                    request,
                    f'Account created successfully for {user.get_full_name()}! '
                    f'Please log in with your credentials.'
                )
                return redirect('/app/login/?registered=1')
            except Exception as e:
                messages.error(
                    request,
                    f'An error occurred while creating your account. Please try again.'
                )
                form.add_error(None, str(e))
        else:
            # Form has errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{form.fields[field].label if field in form.fields else field}: {error}")

            if error_messages:
                messages.error(
                    request,
                    'Please fix the following errors:<br>' + '<br>'.join(error_messages[:3])
                )
    else:
        form = UserRegistrationForm()

        # Check if user was just redirected from successful registration
        if request.GET.get('registered') == '1':
            messages.success(
                request,
                'Registration successful! Please log in with your email and password.'
            )

    return render(request, 'users/register.html', {'form': form})