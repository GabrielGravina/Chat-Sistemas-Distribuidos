from Tkinter import *
from ttk import *
import socket
import thread

class ChatClient(Frame):
  
  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.ServerSOCKET = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.allClients = {}
    self.counter = 0
  
  def initUI(self):
    self.root.title("Trabalho final Sistemas Distribuidos")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    self.FrameSizeX  = 680
    self.FrameSizeY  = 625
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 0
    padY = 0
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    IP_field = Frame(parentFrame)
    serverLabel = Label(IP_field, text="Definir ")
    self.input_content = StringVar()
    self.input_content.set("Servidor01")
    nameField = Entry(IP_field, width=10, textvariable=self.input_content)
    
    self.IP_content = StringVar()
    self.IP_content.set("")
    serverIPField = Entry(IP_field, width=15, textvariable=self.IP_content)
    
    self.Server_PORT_content = StringVar()
    self.Server_PORT_content.set("3000")
    serverPortField = Entry(IP_field, width=5, textvariable=self.Server_PORT_content)
    serverSetButton = Button(IP_field, text="Definir ", width=10, command=self.handleSetServer)
    
    ClientField = Label(IP_field, text="Adicionar amigo: ")
    self.clientIPVar = StringVar()
    self.clientIPVar.set("")
    clientIPField = Entry(IP_field, width=15, textvariable=self.clientIPVar)
    
    self.clientPortVar = StringVar()
    self.clientPortVar.set("3000")
    clientPortField = Entry(IP_field, width=5, textvariable=self.clientPortVar)
    clientSetButton = Button(IP_field, text="Adicionar", width=10, command=self.handleAddClient)
    
    serverLabel.grid(row=0, column=0)
    nameField.grid(row=0, column=1)
    serverIPField.grid(row=0, column=2)
    serverPortField.grid(row=0, column=3)
    serverSetButton.grid(row=0, column=4, padx=5)
    ClientField.grid(row=0, column=5)
    clientIPField.grid(row=0, column=6)
    clientPortField.grid(row=0, column=7)
    clientSetButton.grid(row=0, column=8, padx=5)
    
    readGroupChat = Frame(parentFrame)
    self.receivedChats = Text(readGroupChat, bg="grey", width=60, height=30, state=DISABLED)
    self.receivers = Listbox(readGroupChat, bg="grey", width=30, height=30)
    self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
    self.receivers.grid(row=0, column=1, sticky=E+N+S)

    writeGroupChat = Frame(parentFrame)
    self.chatVar = StringVar()
    self.chatField = Entry(writeGroupChat, width=78, textvariable=self.chatVar)
    sendChatButton = Button(writeGroupChat, text="Enviar mensagem", width=30, command=self.handleSendChat)
    self.chatField.grid(row=0, column=0, sticky=NE)
    sendChatButton.grid(row=0, column=1, padx=5)

    self.statusLabel = Label(parentFrame)

    bottomLabel = Label(parentFrame, text="Grupo: Daniel Terra, Gabriel Gravina, Joao Bosco e Paulo Junior")
    
    IP_field.grid(row=0, column=0)
    readGroupChat.grid(row=1, column=0)
    writeGroupChat.grid(row=2, column=0, pady=5)
    self.statusLabel.grid(row=3, column=0)
    bottomLabel.grid(row=4, column=0, pady=0)
    
  def handleSetServer(self):
    if self.ServerSOCKET != None:
        self.ServerSOCKET.close()
        self.ServerSOCKET = None
        self.serverStatus = 0
    serverAddress = (self.IP_content.get().replace(' ',''), int(self.Server_PORT_content.get().replace(' ','')))
    try:
        self.ServerSOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSOCKET.bind(serverAddress)
        self.ServerSOCKET.listen(5)
        self.setStatus("Escutando na porta %s:%s" % serverAddress)
        thread.start_new_thread(self.listenClients,())
        self.serverStatus = 1
        self.name = self.input_content.get().replace(' ','')
        if self.name == '':
            self.name = "%s:%s" % serverAddress
    except:
        self.setStatus("Erro ao adicionar servidor")
    
  def listenClients(self):
    while 1:
      clientSOCKET, clientAddress = self.ServerSOCKET.accept()
      self.setStatus("Cliente conectado de %s:%s" % clientAddress)
      self.addClient(clientSOCKET, clientAddress)
      thread.start_new_thread(self.handleClientMessages, (clientSOCKET, clientAddress))
    self.ServerSOCKET.close()
  
  def handleAddClient(self):
    if self.serverStatus == 0:
      self.setStatus("Defina o endereco do servidor primeiro")
      return
    clientAddress = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        clientSOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSOCKET.connect(clientAddress)
        self.setStatus("Conectado ao cliente em %s:%s" % clientAddress)
        self.addClient(clientSOCKET, clientAddress)
        thread.start_new_thread(self.handleClientMessages, (clientSOCKET, clientAddress))
    except:
        self.setStatus("Erro ao conectar com o cliente")

  def handleClientMessages(self, clientSOCKET, clientAddress):
    while 1:
      try:
        data = clientSOCKET.recv(self.buffsize)
        if not data:
            break
        self.addChat("%s:%s" % clientAddress, data)
      except:
          break

    self.removeClient(clientSOCKET, clientAddress)
    clientSOCKET.close()
    self.setStatus("Cliente desconectado de %s:%s" % clientAddress)
  
  def handleSendChat(self):
    if self.serverStatus == 0:
      self.setStatus("Defina o endereco do servidor primeiro")
      return
    message = self.chatVar.get()
    if message == '':
        return
    self.addChat("eu", message)
    for client in self.allClients.keys():
      client.send(message)
  
  def addChat(self, client, message):
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",client+": "+message+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientSOCKET, clientAddress):
    self.allClients[clientSOCKET]=self.counter
    self.counter += 1
    self.receivers.insert(self.counter,"%s:%s" % clientAddress)
  
  def removeClient(self, clientSOCKET, clientAddress):
      print self.allClients
      self.receivers.delete(self.allClients[clientSOCKET])
      del self.allClients[clientSOCKET]
      print self.allClients
  
  def setStatus(self, message):
    self.statusLabel.config(text=message)
    print message
      
def main():  
  root = Tk()
  app = ChatClient(root)
  root.mainloop()  

if __name__ == '__main__':
  main()  