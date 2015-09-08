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
import socket
import struct

from subprocess import Popen, PIPE

from django.shortcuts import render
from django.utils.translation import ugettext as _

from freenasUI.freeadmin.apppool import appPool
from freenasUI.freeadmin.views import JsonResp
from freenasUI.middleware.notifier import notifier
from freenasUI.middleware.connector import connection as dispatcher
from freenasUI.network import models
from freenasUI.network.forms import HostnameForm, IPMIForm


def hostname(request):
    general = dispatcher.call_sync('system.general.get_config')
    form = HostnameForm(initial={'hostname': general['hostname']}, data=request.POST)

    if form.is_valid():
        form.save()

    return JsonResp(
        request,
        form=form,
    )


def ipmi(request):

    if request.method == "POST":
        form = IPMIForm(request.POST)
        if form.is_valid():
            rv = notifier().ipmi_set_lan(
                form.cleaned_data,
                channel=int(form.cleaned_data.get('channel')),
            )
            if rv == 0:
                return JsonResp(request, message=_("IPMI successfully edited"))
            else:
                return JsonResp(request, error=True, message=_("IPMI failed"))
    else:
        try:
            ipmi = notifier().ipmi_get_lan()

            #TODO: There might be a better way to convert netmask to CIDR
            mask = ipmi.get("SubnetMask")
            num, cidr = struct.unpack('>I', socket.inet_aton(mask))[0], 0
            while num > 0:
                num = num << 1 & 0xffffffff
                cidr += 1
            initial = {
                'dhcp': False
                if ipmi.get("IpAddressSource") == "Static Address"
                else True,
                'ipv4address': ipmi.get("IpAddress"),
                'ipv4gw': ipmi.get("DefaultGatewayIp"),
                'ipv4netmaskbit': str(cidr),
                'vlanid': ipmi.get("8021qVlanId")
                if ipmi.get("8021qVlanId") != 'Disabled'
                else '',
            }
        except Exception:
            initial = {}
        form = IPMIForm(initial=initial)
    return render(request, 'network/ipmi.html', {
        'form': form,
    })


def network(request):

    tabs = appPool.hook_app_tabs('network', request)
    tabs = sorted(tabs, key=lambda y: y['order'] if 'order' in y else 0)
    return render(request, 'network/index.html', {
        'focus_form': request.GET.get('tab', 'network'),
        'hook_tabs': tabs,
    })
