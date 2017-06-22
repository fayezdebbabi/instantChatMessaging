import socket,os,select,sys,getopt,ctypes,struct,argparse,re
from socerr import socerr
from threading import Thread, Event
import time

class MyThread(Thread):
	def __init__(self, event, message):
		Thread.__init__(self)
		self.stopped = event
		self.message = message

	def run(self):
		i=0
		while not self.stopped.wait(3.5):
			global SERVER_SEQUENCE_NUMBER
			global s
			global paquet
			global adress
			print "tentative numero : "+str(i)
			i=i+1
			# Timout => now you should retransmit
class MyThreadChat(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event

	def run(self):
		global s
		global Buffeur_Chat
		while not self.stopped.wait(3.5):
			for chat in Buffeur_Chat[1:]:
				for client_a_lequel_on_va_envoyer in chat[3]:
					if client_a_lequel_on_va_envoyer[0]==chat[2]:
						pass
					else :
						tuple_adresse=(client_a_lequel_on_va_envoyer[1],client_a_lequel_on_va_envoyer[2])
						message(0,chat[0],0,0,"C", chat[2],chat[1],tuple_adresse)
class MyThreadPrivateChatInvitation(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event

	def run(self):
		global s

		global Buffeur_Invitation_Messagerie_Privee
		while not self.stopped.wait(3.5):
			for invitation in Buffeur_Invitation_Messagerie_Privee[1:]:
				for client_a_lequel_on_va_envoyer in invitation[2]:
					for client in Liste_clients:
						if client[0]==client_a_lequel_on_va_envoyer:
							tuple_adresse=(client[1],client[2])
							message(0,invitation[0],0,0,'F', invitation[1],"",tuple_adresse)
							print "invitation sent to : "+str(client_a_lequel_on_va_envoyer)
class MyThreadMessagesTypesB(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event

	def run(self):
		global s
		global BuffeurMessagesB
		while not self.stopped.wait(3.5):
			for message in BuffeurMessagesB[1:]:
				for client_a_lequel_on_va_envoyer in message[3]:
					if client_a_lequel_on_va_envoyer==message[2]:
						pass					
					for client in Liste_clients:
						if client[0]==client_a_lequel_on_va_envoyer:
							tuple_adresse=(client[1],client[2])
							message(0,message[0],0,0,'F', message[2],message[1],tuple_adresse)
							print "message sent to : "+str(client_a_lequel_on_va_envoyer)



#dans la lsiste des clients on va mettre toutes les informations liees au clients
#Nicknameclient comme identificateur, adresse  IP , numero de port, Status, Type de chat, Identificateur du chat,
#numero de sequence

#INITIALISATION DES VARIABLES -----------------------------------------------------------------------------------
global Liste_clients,NOMBRE_MAXIMAL_CLIENTS,Buffeur_Chat, SERVER_SEQUENCE_NUMBER, adress, paquet,Buffeur_Invitation_Messagerie_Privee,RUNNING_PRIVATE_ACKWLEGMENET,BuffeurMessagesB
global stopFlagSendPrivateChatInvitation,stopFlagChat, stopFlagMessageBSent,chat_rooms,LAST_SERVER_SEQUENCE_NUMBER_TREATED,STARTED_B_SENDING
SERVER_SEQUENCE_NUMBER=1
LAST_SERVER_SEQUENCE_NUMBER_TREATED=0
NOMBRE_MAXIMAL_CLIENTS=500
STARTED_B_SENDING=False
Liste_clients=[]
Liste_clients.append(["Nickname","adresse IP","Port","Status", "Type chat", "Identifcateur chat","num_seq_traitee", "paquet_a_envoyer"])
Buffeur_Chat=[]
Buffeur_Chat.append(["SERVER_SEQUENCE_NUMBER","DATA", "SENDER_USERNAME","liste_clients_temporelle"])
Buffeur_Invitation_Messagerie_Privee=[]
Buffeur_Invitation_Messagerie_Privee.append(["SERVER_SEQUENCE_NUMBER", "SENDER_USERNAME","liste_clients_temporelle"])
BuffeurMessagesB=[]
BuffeurMessagesB.append(["SERVER_SEQUENCE_NUMBER","SENDER_USERNAME","DATA"])

chat_rooms= {} 
global BUFFEUR_CHAT_STARTED
BUFFEUR_CHAT_STARTED=False
RUNNING_PRIVATE_ACKWLEGMENET=False
s = socerr(socket.AF_INET, socket.SOCK_DGRAM,0)
print "longueur " + str(len(Liste_clients))
default_server_port_number = 1212
s.bind(("localhost", default_server_port_number))
print("++++++++++++ c'est la socket serveur +++++++++++")
print("Port du serveur utilisee : "+str(default_server_port_number))
print ("+++++++++++++++++++++++++++++++++++++++++++++++")
print ("Attente de receptions des clients en UDP ... ")
print ("++++++++++++++++++++++++++++++++++++++++++++++")

def incrementSeq():
	global SERVER_SEQUENCE_NUMBER
	if( SERVER_SEQUENCE_NUMBER > 127):
		SERVER_SEQUENCE_NUMBER = 0
	else:
		SERVER_SEQUENCE_NUMBER += 1

	return SERVER_SEQUENCE_NUMBER
#c'est par tester l'affichage de la liste avec un seul appel de cette fonction
def afficher_liste_clients():
	print "longueur de la liste des clients "+ str(len(Liste_clients))
	for client in Liste_clients[1:]:
		print "username : "+client[0]+" adresse IP : "+ str(client[1])+" port : "+str(client[2])


def send_chat_public_users_acknowledgement(SENDER_USERNAME,liste_clients_temporelle,SEQ_NUM_RECEIVED,DATA,tuple_adresse):
	global Buffeur_Chat
	global Liste_clients
	global SERVER_SEQUENCE_NUMBER
	global stopFlagChat
	compteur=1
	paquet_deja_traitee = False
	#partie acquittement
	while compteur <= (len(Liste_clients)-1):
		if tuple_adresse[0]==Liste_clients[compteur][1] and Liste_clients[compteur][2]==tuple_adresse[1]:
			print "seq num treated : " +str(Liste_clients[compteur][6])
			print "seq num received : " +str(SEQ_NUM_RECEIVED)
			if SEQ_NUM_RECEIVED==Liste_clients[compteur][6]:
				print "paquet already treated by the server"
				message(1,SEQ_NUM_RECEIVED,0,0,'C',SENDER_USERNAME,DATA,(Liste_clients[compteur][1],Liste_clients[compteur][2]))
				paquet_deja_traitee=True
				return paquet_deja_traitee
			else :
				print "entered else acknogement"
				message(1,SEQ_NUM_RECEIVED,0,0,'C',SENDER_USERNAME,DATA,(Liste_clients[compteur][1],Liste_clients[compteur][2]))
				print "public chat added to the buffer"
				chat_a_envoyer=[SERVER_SEQUENCE_NUMBER,DATA, SENDER_USERNAME,liste_clients_temporelle]
				Buffeur_Chat.append(chat_a_envoyer)
				Liste_clients[compteur][6]=Liste_clients[compteur][6]+1 
				#partie transmission
				print str(len(Buffeur_Chat))
				if len(Buffeur_Chat)<=2:
					print "here to start thread"
					stopFlagChat = Event()
					thread = MyThreadChat(stopFlagChat)
					thread.start()
					print "thread started"
				incrementSeq()
				return		
		else:	
			compteur=compteur+1

#pour envoyer des messages de chat dans la messagerie publique
def send_chat_public_users(ACK,SEQ_NUM_RECEIVED,NICKNAME_SRC,DATA,tuple_adresse):
	global Buffeur_Chat
	global Liste_clients
	global SERVER_SEQUENCE_NUMBER
	global stopFlagChat
	SENDER_USERNAME=correct_username(NICKNAME_SRC)
	#ic on met une condiction sur la longueur de la liste si ui on declanche le thread
	liste_clients_temporelle=Liste_clients[1:]
	
	if ACK==0:
		send_chat_public_users_acknowledgement(SENDER_USERNAME,liste_clients_temporelle,SEQ_NUM_RECEIVED,DATA,tuple_adresse)
	else : 
		#print "entereeeeeeed ACCCKKK==11111"
		ACKNOWLEDMENET_SENDER=SENDER_USERNAME
		#print "the one acknowledging is : "+ACKNOWLEDMENET_SENDER
		#print "entereeed send_chat_public_users ACK = 1 "
		paquet_deja_traitee = False
		numero_chat=0
		#print "taille buffeur avant le parcours"+str(len(Buffeur_Chat))
		for chat in Buffeur_Chat[1:]:

			if chat[0]==SEQ_NUM_RECEIVED:
				i=0
				for client_a_supprimer in chat[3]:
					if client_a_supprimer[0]==ACKNOWLEDMENET_SENDER:
						print "found indice egale " +str(i)
						break
					i=i+1
			#	print "sortie de la premiere for"

				a=len(chat[3])
				#print "avant suprression "+str(len(chat[3]))
				if a>1:
					del chat[3][i]	
					#print "chat deleted"
					print str(len(chat[3]))
					if len(chat[3])==1:
					#	print "trying to delete all Chat"
						del Buffeur_Chat[numero_chat]
						stopFlagChat.set()
					#	print "flag remis a zero"
					#	print "maitenant longueur du buffeur est egale a "+str(len(Buffeur_Chat))
						return 
			#	print "nombre des clients dans la transmission a une chat apres suppressions"+str(len(chat[3]))
			numero_chat=numero_chat+1


################################################################################################################################
"""
	liste_temporelle=Liste_clients

	for client in Liste_clients:
		if client[3]=="Pu":
			if (client[1]==tuple_adresse[0] and client[2]==tuple_adresse[1]):
				message(1,SEQ_NUM_RECEIVED,0,0,'C',NICKNAME_SRC,DATA,(client[1],client[2]))
			else:
				message(0,SEQ_NUM_RECEIVED,0,0,'C',NICKNAME_SRC,DATA,(client[1],client[2]))
	print "public chat engaged"
"""


#envoyer la liste des utilisateurs au client
def send_public_users_list(SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC_RECEIVED,tuple_adresse):
	USERNAME=correct_username(NICKNAME_SRC_RECEIVED)
	compteur=1
	paquet_deja_traitee = False
	#partie acquittement
	while compteur <= (len(Liste_clients)-1):
		if tuple_adresse[0]==Liste_clients[compteur][1] and Liste_clients[compteur][2]==tuple_adresse[1]:
			print "seq num treated : " +str(Liste_clients[compteur][6])
			print "seq num received : " +str(SEQ_NUM_RECEIVED)

			if SEQ_NUM_RECEIVED==Liste_clients[compteur][6]:
				chaine_liste_client=""
				if FLAG==0:
					for client in Liste_clients[1:]:
							chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
					DATA=chaine_liste_client
					message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)
				else:
					IdChatTmp=-1
					for client in Liste_clients[1:]:
						if client[0]==USERNAME:
							IdChatTmp=client[5]
							break
					for client in Liste_clients[1:]:
						if Client[5]==IdChatTmp:
							chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
							DATA=chaine_liste_client
							message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)
							break
			else:
				chaine_liste_client=""
				if FLAG==0:
					for client in Liste_clients[1:]:
							chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
					DATA=chaine_liste_client
					message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)
				else:
					IdChatTmp=-1
					for client in Liste_clients[1:]:
						if client[0]==USERNAME:
							IdChatTmp=client[5]
							break
					for client in Liste_clients[1:]:
						if Client[5]==IdChatTmp:
							chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
							DATA=chaine_liste_client
							message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)				
				Liste_clients[compteur][6]=Liste_clients[compteur][6]+1 
				break
		else:	
			compteur=compteur+1





	chaine_liste_client=""
	if FLAG==0:
		for client in Liste_clients[1:]:
				chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
		DATA=chaine_liste_client
		message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)
	else:
		IdChatTmp=-1
		for client in Liste_clients[1:]:
			if client[0]==USERNAME:
				IdChatTmp=client[5]
				break
		for client in Liste_clients[1:]:
			if Client[5]==IdChatTmp:
				chaine_liste_client=chaine_liste_client+"&"+client[0]+": "+client[3]
				DATA=chaine_liste_client
				message(1,SEQ_NUM_RECEIVED,0,0,"E","SERVEUR",DATA,tuple_adresse)

######

				print "paquet already treated by the server"
				message(1,SEQ_NUM_RECEIVED,0,0,'E',SENDER_USERNAME,DATA,(Liste_clients[compteur][1],Liste_clients[compteur][2]))
				paquet_deja_traitee=True
				return paquet_deja_traitee
def envoi_message_typeB(ACK,SERVER_SEQUENCE_NUMBER,FLAG,CODE,NICKNAME,DATA):
	if ACK==0 and FLAG==0 and CODE==2:
		DATA="CLIENT ACCEPTED :"+DATA
		for client in Liste_clients:
			if client[0]==NICKNAME:
				tuple_adresse=(client[1],client[2])
				message(0,SERVER_SEQUENCE_NUMBER,FLAG,CODE,'B',NICKNAME,DATA,tuple_adresse)
				print "Message B sent to : "+str(client[0])
	elif ACK==0 and FLAG==1 and CODE==8:
		for client in Liste_clients:
			if client[0]==NICKNAME:
				tuple_adresse=(client[1],client[2])
				message(0,SERVER_SEQUENCE_NUMBER,FLAG,CODE,'B',NICKNAME,DATA,tuple_adresse)
				print "Message B sent to : "+str(client[0])

"""	
	if STARTED_B_SENDING==False:
		print "here to start thread"
		stopFlagMessageBSent = Event()
		thread = MyThreadMessagesTypesB(stopFlagMessageBSent)
		thread.start()
		print "thread started"
	incrementSeq()		
		print "entered message type B"
		message(ACK,SERVER_SEQUENCE_NUMBER,FLAG,CODE,'B',NICKNAME,DATA,tuple_adresse)	
		print "message type B sent"
"""

#SENDER_USERNAME est celui qui veut inviter a une messagerie privee
#cette fonction permet de filtrer les demandeees et envoyer un message de type B 
def informe_demandee_non_joignable(SEQ_NUM_RECEIVED,SENDER_USERNAME,liste_clients_a_inviter,tuple_adresse):
	print "entered informe joinganble"
	global RUNNING_PRIVATE_ACKWLEGMENET
	global Liste_clients
	global SERVER_SEQUENCE_NUMBER
	seq_local=SERVER_SEQUENCE_NUMBER
	DATA=""
	liste_a_retourner=[]
	exist=False
	for cherchee_pour_l_inviter in liste_clients_a_inviter:
		for client in Liste_clients[1:]:
			if cherchee_pour_l_inviter==client[0]:
				if client[3]=='Pr':
					DATA=DATA+", "+cherchee_pour_l_inviter
					#format envoi_message_typeB(ACK,SERVER_SEQUENCE_NUMBER,FLAG,CODE,NICKNAME,DATA)
					envoi_message_typeB(0,seq_local,1,8,SENDER_USERNAME, cherchee_pour_l_inviter)
					exist=True
					break
				else:
					liste_a_retourner.append(client[0])
					exist=True
					break
				exist=True
		if exist==False:
			envoi_message_typeB(0,seq_local,1,4,SENDER_USERNAME,cherchee_pour_l_inviter)
		exist=False
	print "liste construite : "+str(liste_a_retourner)
	return liste_a_retourner

def acquittement_demande_invitation(SEQ_NUM_RECEIVED,SENDER_USERNAME,liste_clients_a_inviter,tuple_adresse):
	global Buffeur_Invitation_Messagerie_Privee
	global Liste_clients
	global SERVER_SEQUENCE_NUMBER
	global stopFlagChat
	global BUFFEUR_CHAT_STARTED
	global stopFlagSendPrivateChatInvitation
	compteur=1
	paquet_deja_traitee = False
	V_SENDER_USERNAME=correct_username(SENDER_USERNAME)
	#partie acquittement
	while compteur <= (len(Liste_clients)-1):
		if tuple_adresse[0]==Liste_clients[compteur][1] and Liste_clients[compteur][2]==tuple_adresse[1]:
			print "seq num treated : " +str(LAST_SERVER_SEQUENCE_NUMBER_TREATED)
			print "seq num received : " +str(SEQ_NUM_RECEIVED)
			if SEQ_NUM_RECEIVED==LAST_SERVER_SEQUENCE_NUMBER_TREATED:
				print "paquet already treated by the server"
				message(1,SERVER_SEQUENCE_NUMBER,0,0,'F',"SERVER","",(Liste_clients[compteur][1],Liste_clients[compteur][2])) 
				paquet_deja_traitee=True
				chat_rooms[SENDER_USERNAME]=["Libre",0]
				return paquet_deja_traitee
			else :
				print "entered else acknowlegment"
				message(1,SEQ_NUM_RECEIVED,0,0,'F',"SERVER","",(Liste_clients[compteur][1],Liste_clients[compteur][2]))
				liste_filtree=informe_demandee_non_joignable(SERVER_SEQUENCE_NUMBER,V_SENDER_USERNAME,liste_clients_a_inviter,tuple_adresse)
				#SENDER_USERNAME c'est celui qui envoie le message type G  
				invitation_a_ajouter_dans_le_buffeur=[SERVER_SEQUENCE_NUMBER,V_SENDER_USERNAME,liste_filtree]
				Buffeur_Invitation_Messagerie_Privee.append(invitation_a_ajouter_dans_le_buffeur)
				#print "longueeuuuerr : " +str(len(Buffeur_Invitation_Messagerie_Privee))+str(Buffeur_Invitation_Messagerie_Privee)
				#partie transmission
				print str(len(Buffeur_Invitation_Messagerie_Privee))
				if BUFFEUR_CHAT_STARTED==True:
					pass
				else :
					print "here to start thread"
					print "thread stopFlagSendPrivateChatInvitation STARTED"
					stopFlagSendPrivateChatInvitation = Event()
					thread = MyThreadPrivateChatInvitation(stopFlagSendPrivateChatInvitation)
					thread.start()
					BUFFEUR_CHAT_STARTED=True
					print "BUFFEUR STATE CHANGED"
					print "thread started"
				incrementSeq()
				return		
		else:	
			compteur=compteur+1

#envoyer une invitation a des clients specifiques connectes a la messagerie publique
def send_invitation_to_desired_clients(ACK,SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC,DATA,tuple_adresse):
	liste_clients_a_inviter=DATA.split("&")
	USERNAME=correct_username(NICKNAME_SRC)
	#gestion avquittement de la demande
	acquittement_demande_invitation(SEQ_NUM_RECEIVED,NICKNAME_SRC,liste_clients_a_inviter,tuple_adresse)
	
#cette fonction supprime un client de la Liste_clients grace a son Nickname
def remove_client(SEQ_NUM_RECEIVED,NICKNAME_SRC,tuple_adresse):
	"""i=1
	deleted=False
	while i<len(Liste_clients):
		if Liste_clients[i][0]==NICKNAME_SRC:
			del Liste_clients[i]
			deleted=True
		i=i+1
	if deleted:
		"""
	print "maitennant on va envoyer au client le message"
	message(1,SEQ_NUM_RECEIVED,0,0,"I","SERVEUR",DATA,tuple_adresse)
	print"Client : "+ NICKNAME_SRC +" disconnected"

#return True si le sytaxe de username est correcte si non retourne False
def test_correct_username_syntax(user_nickname):
	syntax=False
	correct_user_name=re.match("[a-zA-Z0-9]+", user_nickname)
	#compile(r"[a-zA-Z0-9]+")
	#correct_user_name=z.match(user_nickname)
	if correct_user_name is not None:
		syntax= True
		return syntax
	else :
		return syntax

#return True si le client existe si non retourne False
#la comparaison se fait avec des usernames
def test_exist_client(new_user_nickname):
	compteur=0
	exist_client = False
	while compteur < (len(Liste_clients)-1):     
		if Liste_clients[compteur][0]==new_user_nickname:
			exist_client=True
			return exist_client
		else : 
			compteur=compteur+1
	return exist_client

#return True si le username passe en parametre existe si non retourne False
#la comparaison se fait avec des usernames
def test_used_username_client(new_user_nickname):
	for client in Liste_clients:
		if client[0]==new_user_nickname:
			return True
	return False

#verifier si un utilisateur est connecte ou pas
def already_logged_in(USERNAME,tuple_adresse):
	compteur=1
	connected_client = False
	while compteur < (len(Liste_clients)):
		if Liste_clients[compteur][0]==USERNAME and tuple_adresse[0]==Liste_clients[compteur][1] and Liste_clients[compteur][2]==tuple_adresse[1]:
			print "Already logged in client \'"+USERNAME+"\' tried to connect"
			connected_client=True
			return connected_client
		else : 
			compteur=compteur+1
	return connected_client

#verifier le bon syntaxe du username entree part l'utilisateur
def correct_username(NICKNAME_SRC):
	name_variable=NICKNAME_SRC
	compteur=0
	USERNAME=""
	# entre un USERNAME_SRC de longueur inferieure a 10.Vu que les caracteres autorises sont [a-z][A-Z][0-9]
	while compteur < 10 and name_variable[compteur]!='\x00':
		USERNAME=USERNAME+name_variable[compteur]
		compteur=compteur+1
	print USERNAME
	return USERNAME

#on va ajouter un nouveau client a la liste des clients
def add_new_client_to_list(SEQ_NUM_RECEIVED,NICKNAME_SRC,tuple_adresse):
	USERNAME=correct_username(NICKNAME_SRC)
	if already_logged_in(USERNAME,tuple_adresse):
		status="Pu"   #status publique vu que c'est par defaut
		chat_type="C" #chat centralise vu que c'est par defaut
		chat_identifier=0  #ca c'est le numero de la messagerie par defaut la messagerie publique
		message(1,SEQ_NUM_RECEIVED,0,0,"A","SERVEUR",DATA,tuple_adresse)
		print "client : "+USERNAME+" connected"

	elif test_used_username_client(USERNAME) == True:
		print  "client tried to login with an existing username"
		message(1,SEQ_NUM_RECEIVED,1,1,"B","SERVEUR",DATA,tuple_adresse)

	elif test_correct_username_syntax(USERNAME) == False:
		message(1,SEQ_NUM_RECEIVED,1,2,"B","SERVEUR",DATA,tuple_adresse)
		print "incorrect username syntaxe entered"

	else:
		status="Pu"   #status publique vu que c'est par defaut
		chat_type="C" #chat centralise vu que c'est par defaut
		chat_identifier=0  #ca c'est le numero de la messagerie par defaut la messagerie publique
		num_seq_traitee=SEQ_NUM_RECEIVED
		nouveau_client=[USERNAME,tuple_adresse[0],tuple_adresse[1],status,chat_type,chat_identifier,num_seq_traitee]
		Liste_clients.append(nouveau_client)
		message(1,num_seq_traitee,0,0,"A","SERVEUR",DATA,tuple_adresse)
		print "client : "+USERNAME+" connected"

#pour extraire les champs des paquets recus
def resoudre_paquet(paquet_temporaire):
	#recuperer les donnees--------------        
	#recuperer ACK et SEQ_NUM 
	premier=struct.unpack('>B', paquet_temporaire[0])
	if int(premier[0])<128:
		ACK=0
		SEQ_NUM_RECEIVED=int(premier[0])
	elif int(premier[0])>=128:
		ACK=1
		SEQ_NUM_RECEIVED=int(premier[0])-128		
	else:
		print "error"			
	#recuperer FLAG et CODE
	premier=struct.unpack('>B', paquet_temporaire[1])
	if int(premier[0])<128:
		FLAG=0
		CODE=int(premier[0])
	elif int(premier[0])>=128:
		FLAG=1
		CODE=int(premier[0])-128
	else:
		print "error"			
	# recuperer TYPE_MSG
	TYPE_MSG = struct.unpack('s', paquet_temporaire[2])
	#recuperer le NICKNAME_SRC
	NICKNAME_SRC = struct.unpack_from('10s', paquet_temporaire[3:13])
	#pour mettre la chaine dans nickname dans une variable USERNAME_SRC pour une meilleure utilisation
	USERNAME_SRC=NICKNAME_SRC[0]			
	#recuperer TAILLE_DATA
	dernier = struct.unpack_from('H', paquet_temporaire[13:15])
	TAILLE_DATA=dernier[0]/256			
	# methode 1 pour recuperer data similaire a celle de nickname 
	#recuperer DATA 
	data = struct.unpack_from('256s', paquet_temporaire[15:271])
	data_v=data[0]
	compteur=0
	DATA=""
	while compteur < 256 and data_v[compteur]!='*':
		DATA=DATA+data_v[compteur]
		compteur=compteur+1
	
	#---------------------------------------------------------------------------------------------------------

	#la ligne en dessous est a decommenter pour le debogage permet d'afficher les traitements en details
	#debug_resoudre_paquet(ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA)

	#---------------------------------------------------------------------------------------------------------

	return (ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA)

#cette fonction permet d'afficher les champs calculees par la fonction resoudre_paquet, elles sert pour le debogage
def debug_resoudre_paquet(ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA):
		print"\n----------------RECIEVED PACKET-----------------\n"
		print "Premier element en binaire (ACK) : " + str(ACK)
		print "Premier element en binaire (SEQ_NUM) : " + str(SEQ_NUM_RECEIVED)
		print "Premier element en binaire (FLAG) : " + str(FLAG)
		print "Premier element en binaire (CODE) : " + str(CODE)
		print "Voici le type_msg : " + TYPE_MSG[0]
		print "nickname_source : "+ USERNAME_SRC              
		print "TAILLE_DATA : "+ str(TAILLE_DATA)
		print "DATA (methode 1): "+ DATA
		print"\n---------END OF THE RECEIVED PACKET------------"

def migration_chat_privee(demandeur_de_messagerie_privee,SENDER_USERNAME):
	compteur=0
	while compteur <= (len(Liste_clients)-1):
		if Liste_clients[compteur][0]==demandeur_de_messagerie_privee or Liste_clients[compteur][0]==SENDER_USERNAME:
				Liste_clients[compteur][3]="Pr"
				tuple_adresse=(Liste_clients[compteur][1],Liste_clients[compteur][2])
				message(0,SERVER_SEQUENCE_NUMBER,0,2,'B', "SERVER","SWITCHED TO PRIVATE CHAT",tuple_adresse)
				#message(ACK,SEQ_NUM,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA,tuple_adresse)
				incrementSeq()
				return		
		else:	
			compteur=compteur+1

#NICKNAME_SRC_CHERCHEE_POUR_L_INVITER est celui qu'on cherche a l'inviter
def gestion_envoi_des_demandes_invitations(ACK,SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC_CHERCHEE_POUR_L_INVITER,DATA,tuple_adresse):
	print "entered message type G "
	global Buffeur_Invitation_Messagerie_Privee
	global Liste_clients
	global SERVER_SEQUENCE_NUMBER
	global chat_rooms
	global stopFlagSendPrivateChatInvitation
	global BUFFEUR_CHAT_STARTED
	SENDER_USERNAME=correct_username(NICKNAME_SRC_CHERCHEE_POUR_L_INVITER)
	liste_clients_temporelle=Liste_clients[1:]
	paquet_deja_traitee = False
	tuple_adresse
	demandeur_de_messagerie_privee=""
	#suppression de l'element de la liste du buffeur
	#print "avant le for invita.."
	print str(Buffeur_Invitation_Messagerie_Privee)
	for invitation in Buffeur_Invitation_Messagerie_Privee[1:]:
		print str(invitation)
		if invitation[0]==SEQ_NUM_RECEIVED:
			#print "longueur de invitation [0] "+str(len(invitation[2]))
			if len(invitation[2])>0:	
				demandeur_de_messagerie_privee=invitation[1]
				#print "debuuuttt   invitation 2 : "+str(invitation[2])+" -- length : "+str(len(invitation[2]))
				#print "numero de sequence le meme , invitation trouveee"
				i=0
				for client_a_supprimer in invitation[2]:
					if client_a_supprimer==SENDER_USERNAME:

					#	print "found indice egale " +str(i)
						break
					i=i+1
				a=len(invitation[2])
				#print "maintenant longueur de la liste est egale a : "+str(a)
				del invitation[2][i]	
				#print "invitation deleted"
				#print "invitation 2"+str(invitation[2])+" -- "+str(len(invitation[2]))
				if len(invitation[2])==0:
				#	print "BUFFEUR STATE : "
					print BUFFEUR_CHAT_STARTED
				#	print "trying to delete all Chat"
					stopFlagSendPrivateChatInvitation.set()
					BUFFEUR_CHAT_STARTED=False
					#print "BUFFEUR STATE CHANGED TO : "+str(BUFFEUR_CHAT_STARTED)
					#print "flag remis a zero"
					break
		#	print "nombre des clients dans la transmission a une invitation apres suppressions"+str(len(invitation[3]))
	#le client maitenant elimine dela liste on va faire le traitement

	if FLAG==0:
		envoi_message_typeB(0,SERVER_SEQUENCE_NUMBER,0,2,demandeur_de_messagerie_privee, SENDER_USERNAME)
		print "sending validation"
		migration_chat_privee(demandeur_de_messagerie_privee,SENDER_USERNAME)
		#client accepte
	else:
		#ici on va informer celui qui a initiee la demande de l'invitation,  du refus de celui qui est en train de faire l'acknowlgement
		envoi_message_typeB(0,SERVER_SEQUENCE_NUMBER,0,1,demandeur_de_messagerie_privee, SENDER_USERNAME)
		print "sending denying"
		#client n'accepte pas
		

#pour faire le traitement suite a une reception d'un paquet selon le champ TYPE_MSG inclus dedans
def traitement_paquet(ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,NICKNAME_SRC_RECEIVED,TAILLE_DATA,DATA,tuple_adresse):
	if TYPE_MSG[0]=='A':
		add_new_client_to_list(SEQ_NUM_RECEIVED,NICKNAME_SRC_RECEIVED,tuple_adresse)

	if TYPE_MSG[0]=='C':

		send_chat_public_users(ACK,SEQ_NUM_RECEIVED,NICKNAME_SRC_RECEIVED,DATA,tuple_adresse)
	
	if TYPE_MSG[0]=='E':
		send_public_users_list(SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC_RECEIVED,tuple_adresse)

	if TYPE_MSG[0]=='F':
		if ACK==0:
			send_invitation_to_desired_clients(ACK,SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC_RECEIVED,DATA,tuple_adresse)
		else:
			print "problem X1"
	"""
	if type_msg=='B':
	if type_msg=='D':
	"""
	if TYPE_MSG[0]=='G':
		#starting sending the invitations
		gestion_envoi_des_demandes_invitations(ACK,SEQ_NUM_RECEIVED,FLAG,NICKNAME_SRC_RECEIVED,DATA,tuple_adresse)
	"""
	if type_msg=='H':
	"""
	if TYPE_MSG[0]=='I':
		remove_client(SEQ_NUM_RECEIVED,NICKNAME_SRC_RECEIVED,tuple_adresse)

#creation d'un paquet a envoyer
def message(ACK,SEQ_NUM,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA,tuple_adresse):
	paquet = ctypes.create_string_buffer(281)
	if ACK==0:
		FIRST_B=SEQ_NUM
	elif ACK==1:
		FIRST_B=SEQ_NUM+128
	if FLAG==0:
		SECOND_B=CODE
	elif FLAG==1:
		SECOND_B=CODE+128   			
	TD=TAILLE_DATA=len(DATA)  
	#j'ai mis 256 comme maximum du nombre de cacarteres a mettre en DATA

	for reste in range(len(DATA),256):
		DATA=DATA+'*'      
	struct.pack_into('>BBs10sH256s', paquet, 0,  FIRST_B, SECOND_B, TYPE_MSG, NICKNAME_SRC,TAILLE_DATA,DATA)
	s.sendto(paquet,tuple_adresse)

i = 1
inputs = [s]
ferme_programme = True
while ferme_programme:

	readable, writable, exceptional = select.select(inputs, [], [])
	for element in readable:
		paquet_recu, tuple_adresse = element.recvfrom(1024)
		ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA=resoudre_paquet(paquet_recu)
		traitement_paquet(ACK,SEQ_NUM_RECEIVED,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA,tuple_adresse)

		#afficher_liste_clients() c'est pour les tests


print ("------------------------- fin serveur -----------------")

