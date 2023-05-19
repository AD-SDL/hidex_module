import socket
import json            
 
# next create a socket object
s = socket.socket()        
#print ("Socket successfully created")
 
# reserve a port on your computer in our
# case it is 12345 but it can be anything
port = 2000               
 
# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
#s.bind(("146.137.240.22", port))        
#print ("socket binded to %s" %(port))


#module: Module = kwargs["step_module"]
sock = socket.socket()  
#sock.bind(("146.137.240.22", port))
msg = {
    "action_handle": "open",
    "action_vars": {},
}
sock.connect(("146.137.240.22", port))
sock.send(str(msg).encode())
tcp_response = sock.recv(1024).decode()
tcp_response = eval(tcp_response)
print(tcp_response)
# action_response = tcp_response.get('action_response')
# action_msg = tcp_response.get('action_msg')
# action_log = tcp_response.get('action_log')
sock.close()
#TODO: assert all of the above. deal with edge cases?
#return action_response, action_msg, action_log 
# put the socket into listening mode
# s.listen(5)    
# print ("socket is listening")           
 
# # a forever loop until we interrupt it or
# # an error occurs
# while True:
 
# Establish connection with client.
  # c, addr = s.connect()    
  # print ('Got connection from', addr )
  # while True:
  #   command = str(input())
  #   # send a thank you message to the client. encoding to send byte type.
  #   if command == "run_assay":
  #       print("runasdfl;kjasfdl")
  #       c.send(json.dumps({"action_handle": command, "action_vars": {"assay_name":"A260/A280"}}).encode())
  #   else:        
  #       c.send(json.dumps({"action_handle": command, "action_vars": {}
  #   }).encode())
  #   if command == "state":
  #       test = c.recv(1024)
  #       print(test)
  #   if command == "run_assay":
  #       test = c.recv(1024)
  #       while not(str(test) == "Idle"):
  #           print(test)
  #           test = c.recv(1024)
  #       print(test)
  #       print("done")
  # # Close the connection with the client
  # c.close()
   
  # # Breaking once connection closed
  # break