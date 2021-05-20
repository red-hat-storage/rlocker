from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.method == 'GET':
        return render(request, template_name='account/login.html')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.info(request, f"You are logged in as {user.username}")
            return redirect('dashboard_page')
        else:
            messages.error(request, 'The combination of the user name and the password is wrong!')
            return redirect('login_page')

def logout_page(request):
    logout(request)
    messages.info(request, f'You have been logged out!')
    return redirect('dashboard_page')

@login_required(login_url=reverse('login_page'))
def change_password_page(request):
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    if password1 == password2:
        # We could use both password1 or 2 here:
        current_user = request.user
        current_user.set_password(password1)
        current_user.save()
        logout(request)
        messages.success(
            request,
            "Password has been changed! \n"
            "Be sure to use the updated password in your next login! \n"
            "NOTE: Changing your password DOES NOT affect your API token"
        )
        return redirect('login_page')


    else:
        messages.error(
            request,
            "Passwords are not match, or it is not matching our password policies \n"
            "Be sure to: \n"
            " - Contain atleast 8 characters \n"
            " - Your password must include both characters and digits \n"
            " - Your password can't be too similar to your other personal information"
        )
        return redirect('change_password_page')
