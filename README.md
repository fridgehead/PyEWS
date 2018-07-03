PyEWS
=====

Commandline client for exchange web services, to be used in conjunction with NTLMRelayX and the "proxyEWS" feature

NTLMRelayX will relay hashes to a target EWS server and keep the connection open with heartbeats. This tool can then connect to the proxy port and interact with the mailbox

Usage
-----

set emailaddress=target@domain.com
connect 127.0.0.1:PORT

tree -> show dir tree
cd -> change to dir
ls -> show contents of dir
export -> dump contents of folder to folder specified in "export" var

