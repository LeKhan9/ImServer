from socket import *
from random import *

'''
Mohammad Khan, March 2016
____________________________________________________________________________
This is an implementation of a web server that serves html and image files in
a non-persistent, non-parallel fashion. The webpage contains a form using the
post method. The authentication is cross-listed with a database of names and
passwords. An authenticated user will see a random image pop up on the screen,
and the size of that image can be toggled between large and small. Permissions
for specific files are strictly controlled, and errors are handled.
_____________________________________________________________________________
'''

# quick access to different files in our server to check for permissions
files = ['test', 'com315access', 'diagram', 'quokka', 'dog', 'cat', 'turtle', 'parrot', 'gazelle', 'elephant']

# cross-lists current user with database
def authenticate(username, password, fileReader):
    users = fileReader.split('\n')

    # created one key for both username and pass,
    # and checks if it exists in users list
    key = username + ':' + password
    try:
        value_index = users.index(key)
        return True
    except:
        return False
    
def main():
    
    serverPort = 80
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(22)
    print('The server is ready to receive!')

    # constantly looping and looking for connection
    try:
        while 1:
            connectionSocket, addr = serverSocket.accept()
            sentence = connectionSocket.recv(1024)

            # Converts the incoming raw data into a string
            # and find the file name from the GET or POST methods
            # in order to serve or manipulate the file
            sentence = str(sentence.decode('ascii'))

            # If there does exist a file name, then split
            # otherwise ignore (handles IooB error)
            if(sentence.find(' ')!= -1):
                fileName = sentence.split()[1][1:]
            else:
                fileName = ''
                
            #print(fileName)-- for debugging

            # types of files/keys we want to parse out
            website = "html"
            photo = "png"
            icon = "ico"
            name = "id="
            password = "pwd="
            pyFile = "py"

            # if the file to serve is an html 
            if(website in fileName):
                try:
                    fileOpen = open(fileName,'r')
                    fileOpen = fileOpen.read().encode('ascii')
                except IOError:
                    error = "<h1><b>Error 404: file does not exist</b></h1>"
                    error = error.encode('ascii')
                    connectionSocket.send(error)

                # if there does exist an input to the form
                if(name in sentence and password in sentence):

                    # split at 'id=', and then the first '&' of input form,
                    # hence the username is the first index
                    words = sentence.split("id=")
                    user = words[1].split("&")

                    #userName
                    theName = user[0]

                    # since the input form switches the size from second
                    # term in the input form string to third depending on
                    # the size, this accomodates the parsing of either
                    if(user[1].split("=")[0] == "size"):
                        theSize = user[1].split("=")[1]
                        thePass = user[2].split("=")[1]
                    else:
                        theSize = user[2].split("=")[1]
                        thePass = user[1].split("=")[1]
                
                    try:
                        fileOpen = open('class_data.txt','r')
                        fileOpen = fileOpen.read()
                    except IOError:
                        error = "<h1><b>Error 404: file does not exist</b></h1>"
                        error = error.encode('ascii')
                        connectionSocket.send(error)
                        
                    # if user authentication is genuine
                    if(authenticate(theName, thePass, fileOpen) == True):

                        # obtain a random image from files list
                        imageFile = files[randint(3,9)]+ ".png"

                        # open html file in order to manipulate it and insert image
                        try:
                            fileOpen = open('com315access.html', 'r')
                            fileOpen = str(fileOpen.read())
                        except IOError:
                            error = "<h1><b>Error 404: file does not exist</b></h1>"
                            error = error.encode('ascii')
                            connectionSocket.send(error)
                            
                        words = fileOpen.split("<hr> <hr>")

                        # html code before and after horizontal lines
                        beforeLines = words[0]
                        afterLines = words[1]

                        # toggling size values
                        if(theSize == "small"):
                            x, y = "220", "220"
                        else:
                            x, y = "380", "380"

                        # html code for image tag
                        imageString = '<img src=' + imageFile + ' width="'+ x +'" height ="' + y + '">'

                        # greet client
                        userString = '<h1><b>Welcome ' + theName + '! </b></h1>'

                        # concatenates all the previous tags/html code and encodes into ascii to send to client
                        authString = beforeLines + userString + '<hr> <hr>' + imageString + afterLines
                        authString = authString.encode('ascii')
                    
                        connectionSocket.send(authString)
                        
                    # if user is not authenticated, just serve normal file, no image    
                    else:
                        
                        # open html file in order to manipulate it and insert image
                        try:
                            fileOpen = open('com315access.html', 'r')
                            fileOpen = str(fileOpen.read())
                        except IOError:
                            error = "<h1><b>Error 404: file does not exist</b></h1>"
                            error = error.encode('ascii')
                            connectionSocket.send(error)
                            
                        words = fileOpen.split("<hr> <hr>")

                        # html code before and after lines
                        beforeLines = words[0]
                        afterLines = words[1]

                        # greet client to try again
                        userString = "<h1><b>Login attempt failed. Try again!</b></h1>"
                        
                        # concatenates all the previous tags/html code and encodes into ascii to send to client
                        unAuthString = beforeLines + userString + '<hr> <hr>' + afterLines
                        unAuthString = unAuthString.encode('ascii')
                    
                        connectionSocket.send(unAuthString)
                        
                # if non-input form html file, serve html file
                else:
                    connectionSocket.send(fileOpen)

            # displays favicon on tab - the substring 'check' triggers the file
            elif (icon in fileName):
                fileName = fileName.encode('ascii')
                connectionSocket.send(fileName)

            # gets image byte file, reads and serves it 
            elif(photo in fileName):
                try:
                    fileOpen = open(fileName, 'rb')
                    fileOpen = fileOpen.read()
                    connectionSocket.send(fileOpen)
                except IOError:
                    error = "<h1><b>Error 404: file does not exist</b></h1>"
                    error = error.encode('ascii')
                    connectionSocket.send(error)

            # if file was not any of the above types
            else:
                # if client attempts to access user database, send a 'no!'
                if(fileName == "class_data.txt"):
                    error = "<h1><b>Error 403: Unauthorized Access</b></h1>"
                    error = error.encode('ascii')
                    connectionSocket.send(error)
                    
                # if client tries to access source code, deny it
                elif(pyFile in fileName):
                    error = "<h1><b>Error 403: Unauthorized Access</b></h1>"
                    error = error.encode('ascii')
                    connectionSocket.send(error)
                    
                # if file isn't even in database, then 404 error    
                else:
                    try:
                        value_index = files.index(fileName)
                    except:
                        error = "<h1><b>Error 404: file does not exist</b></h1>"
                        error = error.encode('ascii')
                        connectionSocket.send(error)
            
            connectionSocket.close()
    except ConnectionAbortedError:
        connectionSocket, addr = serverSocket.accept()
        sentence = connectionSocket.recv(1024)
        error = '<h1><b>Connection Aborted Error: peer unexpectedly quit connection attempt</b></h1>'
        error = error.encode('ascii')
        connection.send(error)
        connectionSocket.close()
main()
