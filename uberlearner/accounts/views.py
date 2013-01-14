from allauth.account import signals
from allauth.account.forms import ResetPasswordKeyForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, HttpResponseRedirect, Http404
import allauth.account
import allauth.account.views
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.http import base36_to_int
from django.utils.translation import ugettext
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from accounts.forms import UserProfileForm
from avatar.views import _get_avatars
from avatar.models import Avatar
from avatar.signals import avatar_updated

def login(request, **kwargs):
    """
    This view is an envelope for the default login view of allauth.account.
    In case the user is already authenticated, this view redirects the user
    to the user-profile page. If not, the regular actions are taken to log
    the user into the system.
    """
    if request.user.is_authenticated():
        return kwargs.get('logged_in_view')(request, **kwargs)
    else:
        return allauth.account.views.login(request, **kwargs)

def signup(request, **kwargs):
    """
    This view is an envelope for the default signup view of the allauth.account.
    In case the user is already authenticated, this view redirects the user
    to the user-profile page. If not, the regular actions are taken to log
    the user into the system.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_user_profile'))
    else:
        return allauth.account.views.signup(request, **kwargs)

def user_profile_with_username(request, username='', user=None):
    if not user:
        user = get_object_or_404(User, username=username)
    return render_to_response('allauth/account/view_profile.html',
                              {'profile_owner': user, 'main_js_module': 'uberlearner/js/main/base'},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request):
    return HttpResponseRedirect(reverse('account_user_profile_with_username', 
                                kwargs={'username': request.user.username}))

@login_required
def edit_user_profile_with_username(request, username=''):
    if request.user and request.user.username != username:
        raise PermissionDenied("You can't edit another user's profile")
    user = get_object_or_404(User, username=username)
    avatar, avatars = _get_avatars(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            if 'avatar' in request.FILES:
                avatar = Avatar(user=user, primary=True)
                image_file = request.FILES['avatar']
                avatar.avatar.save(image_file.name, image_file)
                avatar.save()
                avatar_updated.send(sender=Avatar, user=user, avatar=avatar)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.summary = form.cleaned_data['summary']
            user.profile.save()
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Your profile has been successfully updated')
            return user_profile_with_username(request, '', user)
        else:
            messages.add_message(request, messages.ERROR, 'Your profile could not be updated')
    else:
        form = UserProfileForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'summary': user.profile.summary,
            'avatar': avatar
        }, user=user)

    return render(request, 'allauth/account/edit_profile.html', {
        'form': form,
        'main_js_module': 'uberlearner/js/accounts/profile-edit'
    }) 

def edit_user_profile(request):
    return HttpResponseRedirect(
        reverse('account_edit_user_profile_with_username',
            kwargs={'username': request.user.username})
    )

class ConfirmEmailView(allauth.account.views.ConfirmEmailView):
    """
    This view class over-rides the one provided by django-allauth. The reason for the over-ride is to be
    able to use a different template file name than the one that is hard-coded into django-allauth.
    """
    email_confirm_template = None
    email_confirmed_template = None

    def __init__(self, email_confirm_template='account/email_confirm.html',
                 email_confirmed_template='account/email_confirmed.html', **kwargs):
        self.email_confirm_template = email_confirm_template
        self.email_confirmed_template = email_confirmed_template
        super(ConfirmEmailView, self).__init__(**kwargs)

    def get_template_names(self):
        if self.request.method == "GET":
            return [self.email_confirm_template]
        elif self.request.method == "POST":
            return [self.email_confirmed_template]

def password_reset_from_key(request, uidb36, key, **kwargs):
    """
    This view replaces the view provided by allauth for the actual password reset. Since this view was
    not a class, it could not be extended.
    TODO: convert this view to a class-based view and send the changes upstream.
    """
    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", "account/password_reset_from_key.html")
    token_generator = kwargs.get("token_generator", default_token_generator)

    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)

    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)
            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                messages.add_message(request, messages.SUCCESS,
                    ugettext(u"Password successfully changed.")
                )
                signals.password_reset.send(sender=request.user.__class__,
                    request=request, user=request.user)
                password_reset_key_form = None
                return redirect('account_login')
        else:
            password_reset_key_form = form_class()
        ctx = { "form": password_reset_key_form, }
    else:
        ctx = { "token_fail": True, }

    return render_to_response(template_name, RequestContext(request, ctx))