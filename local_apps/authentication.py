# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from django.forms.util import ErrorList
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext


class LoginFormIntranet(forms.Form):
    User = forms.CharField(label="Usuario", required=True)
    Password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        user = cleaned_data.get("User")
        passwd = cleaned_data.get("Password")
        
        if user and passwd:
            try:
                usuario = User.objects.get(username=user)
                grupos = usuario.groups.all()
                docente = False
                for grupo in grupos:
                    if grupo.name == "Colaboradores":
                        docente = True
                        break
                if docente:
                    if usuario.check_password(passwd) == False:
                        msg = u'Contraseña incorrecta'
                        self._errors["Password"] = ErrorList([msg])
                        del cleaned_data["Password"]
                else:
                    msg = u'No eres Docente'
                    self._errors["User"] = ErrorList([msg])
                    del cleaned_data["User"]
            except (User.DoesNotExist):
                msg = u'Usuario Incorrecto'
                self._errors["User"] = ErrorList([msg])
                del cleaned_data["User"]
            
        return cleaned_data

@csrf_protect
@never_cache
def login_colaborador(request):
    if request.method == 'POST':
        form = LoginFormIntranet(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['User']
            passwd = form.cleaned_data['Password']
            user = authenticate(username = usuario, password = passwd)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('../profile/')
    else:
        form = LoginFormIntranet()

    return render_to_response("colaboradores/login_colaborador.html", {"form": form }, context_instance = RequestContext(request))

@csrf_protect
def logout_colaborador(request):
    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect('../login/')
    else:
        return HttpResponseRedirect('../login/')

class ChangePasswordForm(forms.Form):
    OldPassword = forms.CharField(widget=forms.PasswordInput, label = "Contraseña Antigua",required = True)
    NewPassword = forms.CharField(widget=forms.PasswordInput, label = "Nueva Contraseña",required = True)
    RepeatPassword = forms.CharField(widget=forms.PasswordInput, label = "Repetir Contraseña",required = True)
    User = forms.CharField(widget = forms.HiddenInput, required = True,label = "")
    
    def clean(self):
        cleaned_data = self.cleaned_data
        oldpasswd = cleaned_data.get("OldPassword")
        newpasswd = cleaned_data.get("NewPassword")
        repeatpasswd = cleaned_data.get("RepeatPassword")
        usuario = cleaned_data.get("User")
        
        if oldpasswd and newpasswd and repeatpasswd and usuario:
            try:
                usuario = User.objects.get(username=usuario)
                if usuario.check_password(oldpasswd) == True:
                    if newpasswd == repeatpasswd:
                        usuario.set_password(newpasswd)
                        usuario.save()
                    else:
                        msg = u'Las contraseñas no coinciden'
                        self._errors["RepeatPassword"] = ErrorList([msg])
                        del cleaned_data["RepeatPassword"]
                else:
                    msg = u'Contraseña Incorrecta'
                    self._errors["OldPassword"] = ErrorList([msg])
                    del cleaned_data["OldPassword"]    
            except User.DoesNotExist:
                msg = u'User Incorrecto, intento de acceso no autorizado'
                self._errors["OldPassword"] = ErrorList([msg])
                del cleaned_data["OldPassword"]
        return cleaned_data

@csrf_protect
def cambiar_passwd(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                return render_to_response("colaboradores/cambiar_passwd_successful.html")
        else:
            form = ChangePasswordForm(initial = {'User': request.user.username})
        return render_to_response("colaboradores/cambiar_passwd.html", {"form": form, "user": request.user }, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect('../login/')