<%!
import time
serial_time = int(time.time())
import socket

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True

def space(string):
    lenght = 20 - len(string)
    return ' ' * lenght
%>; File auto generated
;
; BIND data file for zone "${general['domain']}"
;
$TTL    604800
$ORIGIN ${general['domain']}.
@       IN      SOA     ${general['dns']}.${general['domain']}. root.${general['dns']}.${general['domain']}. (
                     ${serial_time}                 ; Serial
                         604800                 ; Refresh
                          86400                 ; Retry
                        2419200                 ; Expire
                         604800 )               ; Negative Cache TTL
;
@       IN      NS     ${general['dns']}.${general['domain']}.

%for host in sorted(hosts):
    %for int in hosts[host]['network']['interfaces']:
<%
wide_space=space(int['name'])
if is_valid_ipv4_address(int['ip']):
    record='A    '
elif is_valid_ipv6_address(int['ip']):
    record='AAAA ' 
%>${int['name']}${wide_space}   IN ${record}   ${int['ip']}
        %for alias in int['aliases']:
<% wide_space=space(alias) %>${alias}${wide_space}   IN CNAME   ${int['name']}
        % endfor
    % endfor
% endfor
