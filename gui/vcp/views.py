#+
# Copyright 2010 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################

import json
import utils

from django.shortcuts import render
from django.utils.translation import ugettext as _
from freenasUI.freeadmin.views import JsonResp
from freenasUI.vcp.forms import VcenterConfigurationForm
from freenasUI.vcp import models
from django.http import HttpResponse

from freenasUI.system.models import (
    Settings,
)


def vcp_home(request):
    if request.method == 'POST':
     form = VcenterConfigurationForm(request.POST)
     if form.is_valid():

         if form.install_plugin():
            form.save()
            obj = models.VcenterConfiguration.objects.latest('id')
            obj.vc_version = utils.get_plugin_version()
            obj.save()
            return JsonResp(request,message = _('vCenter plugin installed successfully.'),)
         else:
            return JsonResp(request, error = True, message = _(form.vcp_status))
    else:
        try:
          obj = models.VcenterConfiguration.objects.latest('id')
          form = VcenterConfigurationForm(instance=obj)
          form.fields['vc_ip'].widget.attrs['readonly'] = True
          form.fields['vc_username'].widget.attrs['readonly'] = True
          form.fields['vc_password'].widget.attrs['readonly'] = True
          form.fields['vc_port'].widget.attrs['readonly'] = True
          form.fields['vc_management_ip'].widget.attrs['readonly'] = True
          form.is_update_needed()
        except :
           form = VcenterConfigurationForm()
           form.is_update_needed()
    return render(request, "vcp/index.html", {'form': form })


def vcp_upgrade(request):
      form = VcenterConfigurationForm()
      if form.upgrade_plugin():
        return JsonResp(request, message = _('vCenter plugin upgraded successfully.'),)
      else :
          return JsonResp(request, error = True, message=_(form.vcp_status))



def vcp_uninstall(request):
      form = VcenterConfigurationForm()
      if form.uninstall_plugin():
         return JsonResp(request,message = _('vCenter plugin uninstalled successfully.'), )
      else :
         return JsonResp(request, error = True, message = _(form.vcp_status))
