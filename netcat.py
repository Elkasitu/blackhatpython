import sys
import socket
import getopt
import threading
import subprocess


# define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "BHP Net Tool"
    print
    print "Usage: netcat.py -t target_host -p port"
    print "-l --listen                  - listen on [host]:[port] for
                                          incoming connections"
    print "-e --execute=file_to_run     - execute the given file upon
                                          receiving a connection"
    print "-c --command                 - initialize a command shell"
    print "-u --upload=destination      - upon receiving connection upload a
                                          file and write to [destination]"
    print
    print
    print "Examples: "
    print "netcat.py -t 192.168.0.1 -p 5555 -l -c"
    print "netcat.py -t 192.168.0.1 -p 5555 -l -u=~/target.sh"
    print "netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
            
        #connect to our target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)
        while True:
            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                    
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # send it off
            client.send(buffer)

    except:
            
        print "[*] Exception! Exiting."

        # tear down the connection
        client.close()

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
        ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()


    for opt, arg in opts:
        if opt in ("-h", "--help"): usage()
        elif opt in ("-l", "--listen"): listen = True
        elif opt in ("-e", "--execute"): execute = arg
        elif opt in ("-c", "--command"): command = True
        elif opt in ("-u", "--upload"): upload_destination = arg
        elif opt in ("-t", "--target"): target = arg
        elif opt in ("-p", "--port"): port = int(arg)
        else: assert False, "Unhandled Option"

    # listening or not?
    if not listen and len(target) and port > 0:

        # read in the buffer from the command line
        # this will block, so send CTRL-D if not sending input to stdin
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)

    # we are going to listen and potentially upload things, execute commands
    # and drop a shell back depending on our command line options above
    if listen:
        server_loop()


main()

