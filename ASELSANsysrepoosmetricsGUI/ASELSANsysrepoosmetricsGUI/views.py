import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from ncclient import manager
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import AuthenticationError as AuthenticationError
from ncclient.operations.rpc import RPCError 
from .forms import ConnectForm, ConfigTypeForm
from lxml import etree as ET
from lxml import etree
import os
import copy
import xml.etree.ElementTree as et
# Define a global variable for the manager connection
global_manager = None
def getFilters(folderPath):
    config_methods = []
    for filename in os.listdir(folderPath):
        if filename.endswith(".xml"):
            method_name = os.path.splitext(filename)[0]  # Extract method name without extension
            config_methods.append((method_name, method_name))  # Add tuple for choice field
    return config_methods

global_tree = None
global_varible_num_for_edit = None
global_current = None
global_mark_parent_list = set()
global_mark_parent_temp = set()
global_identifier = 0   
global_leaves = []

def connect(request):

    global global_manager

    if request.method == 'POST':
        form = ConnectForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Establish the connection using ncclient
                global_manager = manager.connect(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    hostkey_verify=False,
                    allow_agent=False,
                    look_for_keys=False,
                    device_params={'name': 'default'}
                )

                # Store necessary data in session
                request.session['netopeer_connection'] = {
                    'host': host,
                    'port': port,
                    'username': username,
                    'password': password
                }

                # Redirect to configuration selection page
                return redirect('dashboard')

            except TimeoutExpiredError:
                error_message = f"Connection to {host}:{port} timed out."
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

            except AuthenticationError:
                error_message = f"Authentication failed for {username} on {host}:{port}."
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

            except Exception as e:
                error_message = f"Error connecting to {host}:{port}: {str(e)}"
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

    else:
        form = ConnectForm()

    return render(request, 'connect.html', {'form': form})

def get_rpc_request(request_name,time):
    rpc_requests = {
        "get-ip": """
            <get-ip xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "get-time": """
            <get-time xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "set-time": """
            <set-time xmlns="ASELSAN-Sysrepo-OS-Metrics">
                <newtime>{time1}</newtime>
            </set-time>
        """.format(time1=time),
        "sync-time": """
            <sync-time xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "freeg": """
            <freeg xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "uptime": """
            <uptime xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "lscpu": """
            <lscpu xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """,
        "top": """
            <top xmlns="ASELSAN-Sysrepo-OS-Metrics"/>
        """
    }
    return rpc_requests.get(request_name, "Invalid request name")

def dashboard(request):
    global global_manager
    # Retrieve connection data from session
    connection_data = request.session.get('netopeer_connection')

    if not connection_data:
        return HttpResponse("Connection data not found in session.", status=400)

    config_methods = [('get-ip', 'Get IP'), ('get-time', 'Get Time'), ('set-time', 'Set Time'), ('sync-time', 'Sync Time'), ('freeg', 'Free G'), ('uptime', 'Uptime'),('lscpu','Ls CPU'),('top','Top')]
    try:
        response = None
        if request.method == 'POST':
            form = ConfigTypeForm(request.POST, choices=config_methods)
            if form.is_valid():
                selected_method = form.cleaned_data['method']
                if selected_method == 'set-time':
                    time_input = request.POST.get('time', None)
                    if not time_input:
                        raise Exception("Time input is required for 'Set Time' method.")
                else:
                    time_input = None
                rpc_req = get_rpc_request(selected_method,time_input)
                #print(selected_method,time_input)
                response = global_manager.dispatch(etree.fromstring(rpc_req))
                print(response)
            else:
                raise Exception("Invalid form data.")
        form = ConfigTypeForm(choices=config_methods)
        return render(request, 'dashboard.html', {'form': form, 'rpc_result': response})
    except Exception as e:
        return render(request, 'dashboard.html', {'form': form,'error_message': str(e)})