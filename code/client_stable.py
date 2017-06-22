import socket,os,sys,getopt,ctypes,struct,argparse, select
from threading import Thread, Event
import time
from socerr import socerr

class MyThread(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event

	def run(self):
		i=0
		while not self.stopped.wait(3):
			global CLIENT_NEW_SEQ_NUMBER
			global s
			global paquet
			global adress    		
			#print "tentative numero : "+str(i)
			s.sendto(paquet,adress)
			i=i+1
			# Timout => now you should retransmit

s = socerr(socket.AF_INET, socket.SOCK_DGRAM,0)
client_port_number = 0
s.bind(("localhost", client_port_number))
default_server_port_number = 1212
default_server_ip_adress = "localhost"



#INITIALISATION DES VARIABLES -----------------------------------------------------------------------------------
global USERNAME_ENTERED_BY_USER, CLIENT_NEW_SEQ_NUMBER, CLIENT_LAST_SEQUENCE_TREATED, paquet, adress
global synchro_serveur
global stopFlagPrivateInvitation, stopFlagConnetion, stopFlagGetPublicListeClients,stopFlagDeconnexion,stopFlagChat
global CHAT_MODE,ACCEPT_INVITATION

global GLOBAL_SERVER_SEQUENCE_NUMBER
GLOBAL_SERVER_SEQUENCE_NUMBER=-1

CHAT_MODE="Pu"
USERNAME_ENTERED_BY_USER=""
CLIENT_NEW_SEQ_NUMBER=0
CLIENT_LAST_SEQUENCE_TREATED=None
synchro_serveur=[-1,-1]
ACCEPT_INVITATION="nothing"
def incrementSynchroServeur():
	global synchro_serveur
	if( synchro_serveur[1] > 127):
		synchro_serveur[1] = 0
	else:
		synchro_serveur[1] += 1

#gestion du numero de sequence
def incrementSeq():
	global CLIENT_NEW_SEQ_NUMBER
	if( CLIENT_NEW_SEQ_NUMBER > 127):
		CLIENT_NEW_SEQ_NUMBER = 0
	else:
		CLIENT_NEW_SEQ_NUMBER += 1

#cette fonction permet d'extraire tous les champs d'un paquet recu
def resoudre_paquet(paquet_temporaire):
	#recuperer les donnees--------------        
	#recuperer ACK et CLIENT_NEW_SEQ_NUMBER 
	premier=struct.unpack('>B', paquet_temporaire[0])
	if int(premier[0])<128:
		ACK=0
		SEQ_NUM_RECEIVED_FROM_THE_SERVER=int(premier[0])
	elif int(premier[0])>=128:
		ACK=1
		SEQ_NUM_RECEIVED_FROM_THE_SERVER=int(premier[0])-128	
	else:
		print"error"
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
	name_variable=NICKNAME_SRC[0]
	compteur=0
	USERNAME_SRC=""
	# le caractere '*' je l'ai choisi comme caractere d'echappement pour le cas ou le client
	# entre un USERNAME_SRC de longueur inferieure a 10.Vu que les caracteres autorises sont [a-z][A-Z][0-9]
	while compteur < 10 and name_variable[compteur]!='*':
		USERNAME_SRC=USERNAME_SRC+name_variable[compteur]
		compteur=compteur+1			
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

	#la ligne en dessous est a decommenter pour le debogage
	#debug_resoudre_paquet(ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA)

	return (ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA)

#cette fonction permet d'afficher les champs calcules par la fonction resoudre_paquet, elles sert pour le debogage
def debug_resoudre_paquet(ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA):
		print"\n----------------RECIEVED PACKET-----------------\n"
		print "Premier element en binaire (ACK) : " + str(ACK)
		print "Premier element en binaire (CLIENT_NEW_SEQ_NUMBER) : " + str(SEQ_NUM_RECEIVED_FROM_THE_SERVER)
		print "Premier element en binaire (FLAG) : " + str(FLAG)
		print "Premier element en binaire (CODE) : " + str(CODE)
		print "Voici le type_msg : " + TYPE_MSG[0]
		print "nickname_source : "+ USERNAME_SRC              
		print "TAILLE_DATA : "+ str(TAILLE_DATA)
		print "DATA (methode 1): "+ DATA
		print"\n---------END OF THE RECEIVED PACKET------------"

#creation d'un paquet
def message(ACK,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA):
	global CLIENT_NEW_SEQ_NUMBER
	global paquet
	global adress
	# put data into the paquet
	paquet = ctypes.create_string_buffer(281)
	
	if ACK==0:
		FIRST_B=CLIENT_NEW_SEQ_NUMBER
	elif ACK==1:
		FIRST_B=CLIENT_NEW_SEQ_NUMBER+128
	if FLAG==0:
		SECOND_B=CODE
	elif FLAG==1:
		SECOND_B=CODE+128
	TD=TAILLE_DATA=len(DATA)  
	#j'ai mis 256 comme maximum du nombre de cacarteres a mettre en DATA

	for reste in range(len(DATA),256):
		DATA=DATA+'*'      
	struct.pack_into('>BBs10sH256s', paquet, 0,  FIRST_B, SECOND_B, TYPE_MSG, NICKNAME_SRC,TAILLE_DATA,DATA)
	adress=(default_server_ip_adress,default_server_port_number)
	if TYPE_MSG[0] =='G':
		s.sendto(paquet,adress)
		print "sending the esponse to the server"
	if TYPE_MSG[0] =='C' and ACK==1:
		s.sendto(paquet,adress)
		print " sending acknowledgement client-> server"
	elif TYPE_MSG[0] =='I':
		print "sent IIII"
		s.sendto(paquet,adress)

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

def reponse_message_serveur(ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA):
	global USERNAME_ENTERED_BY_USER
	paquet = ctypes.create_string_buffer(281)
	if ACK==0:
		FIRST_B=SEQ_NUM_RECEIVED_FROM_THE_SERVER
	elif ACK==1:
		FIRST_B=SEQ_NUM_RECEIVED_FROM_THE_SERVER+128
	if FLAG==0:
		SECOND_B=CODE
	elif FLAG==1:
		SECOND_B=CODE+128
	TD=TAILLE_DATA=len(DATA)  
	#j'ai mis 256 comme maximum du nombre de cacarteres a mettre en DATA

	for reste in range(len(DATA),256):
		DATA=DATA+'*'      
	struct.pack_into('>BBs10sH256s', paquet, 0,  FIRST_B, SECOND_B,"C", USERNAME_ENTERED_BY_USER,TAILLE_DATA,DATA)
	adress=(default_server_ip_adress,default_server_port_number)
	s.sendto(paquet,adress)

#permet l'affichage de la liste des clients connectee a la messagerie publique
def affichage_liste_clients_recue(TAILLE_DATA,DATA):
	print "---------------------- Client list--------------------------"
	new_liste=[]
	liste_recue=DATA.split("&")
	for element in liste_recue[1:]:
		new_liste.append(str(element).split(":"))
	for client in new_liste[0:]:
		print client[0]+" statut : "+client[1]
	print "-------------------------------------------------------------"

#pour faire le traitement suite a une reception d'un paquet selon le champ TYPE_MSG inclus dedans
def traitement_paquet(ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,TAILLE_DATA,DATA,tuple_adresse):
	global CLIENT_LAST_SEQUENCE_TREATED
	global CLIENT_NEW_SEQ_NUMBER
	global stopFlagConnetion
	global stopFlagChat
	global stopFlagGetPublicListeClients
	global stopFlagDeconnexion
	global synchro_serveur
	global ACCEPT_INVITATION
	global GLOBAL_SERVER_SEQUENCE_NUMBER
	global CLIENT_LAST_SEQUENCE_TREATED
	global USERNAME_ENTERED_BY_USER
	print "type message recu : "+str(TYPE_MSG[0])
	print "ack = "+str(ACK)


	if CLIENT_LAST_SEQUENCE_TREATED==None and SEQ_NUM_RECEIVED_FROM_THE_SERVER==0 and ACK==1 :

		if TYPE_MSG[0]=='A':
			print "-----------------------------------------------------------"
			print "                Connexion validee"
			print "-----------------------------------------------------------"
			print ""
			print "-----------------------------------------------------------------------------" 
			print ""
			print "Pour deconnecter tapez : DISCONNECT "
			print "Pour Obtenir voir liste des clients public  : GET_PUBLIC_USERS_LIST"
			print "Faire demande d'invitation a une messagerie privee : PRIVATE_CHAT_INVITATION"
			print ""
			print "-----------------------------------------------------------------------------" 

			stopFlagConnetion.set()
			CLIENT_LAST_SEQUENCE_TREATED=0

		elif TYPE_MSG[0]=='B' and FLAG==1 and CODE==1:
			stopFlagConnetion.set()
			CLIENT_NEW_SEQ_NUMBER=0
			print "already used username"	
			exit()

		elif TYPE_MSG[0]=='B' and FLAG==1 and CODE==2 :
			stopFlagConnetion.set()
			print "Wrong username syntaxe"
			exit()
	
	elif TYPE_MSG[0]=='B':

		if ACK==1 and FLAG==1 and CODE==1:
			stopFlagConnetion.set()
			CLIENT_NEW_SEQ_NUMBER=0
			print "already used username"	
			exit()

		elif ACK ==0 and FLAG==1 and CODE==2 :
			stopFlagConnetion.set()
			print "Wrong username syntaxe"
			exit()

		elif ACK==0 and FLAG==0 and CODE==2:
			if GLOBAL_SERVER_SEQUENCE_NUMBER==SEQ_NUM_RECEIVED_FROM_THE_SERVER:
				pass
			else:
				GLOBAL_SERVER_SEQUENCE_NUMBER=GLOBAL_SERVER_SEQUENCE_NUMBER+1
				print DATA				

		
			
		elif FLAG==0 and CODE==1:
			stopFlagPrivateInvitation.set()
			print "-------------------------------"

		elif FLAG==0 and CODE==4 :
			print "-------------Switching to private chat denied------------------"

		elif FLAG==0 and CODE==8 :
			print "-------Switching to public chat due to lack of clients------------"

		elif ACK ==0 and FLAG==1 and CODE==2 :
			stopFlagConnetion.set()
			print "Wrong username syntaxe"
			exit()

		elif ACK==0 and FLAG==1 and CODE==4:
			if GLOBAL_SERVER_SEQUENCE_NUMBER==SEQ_NUM_RECEIVED_FROM_THE_SERVER:
				pass
			else:
				GLOBAL_SERVER_SEQUENCE_NUMBER=GLOBAL_SERVER_SEQUENCE_NUMBER+1
				print  NICKNAME_SRC+" : "+DATA	
				print "-----------------Client inexistant--------------------"		
			reponse_message_serveur(1,SEQ_NUM_RECEIVED_FROM_THE_SERVER,0,CODE,'B',USERNAME_ENTERED_BY_USER,DATA)

		elif ACK==0 and FLAG==1 and CODE==8:
			if GLOBAL_SERVER_SEQUENCE_NUMBER==SEQ_NUM_RECEIVED_FROM_THE_SERVER:
				pass
			else:
				GLOBAL_SERVER_SEQUENCE_NUMBER=GLOBAL_SERVER_SEQUENCE_NUMBER+1
				print  NICKNAME_SRC+" : "+DATA	
				print "--------------client :"+NICKNAME_SRC+" deja dans un chat prive---------------"
			reponse_message_serveur(1,SEQ_NUM_RECEIVED_FROM_THE_SERVER,0,CODE,'B',USERNAME_ENTERED_BY_USER,DATA)

	elif TYPE_MSG[0]=='C' :
		if ACK==1 and SEQ_NUM_RECEIVED_FROM_THE_SERVER==(CLIENT_NEW_SEQ_NUMBER-1):
			stopFlagChat.set()
			CLIENT_LAST_SEQUENCE_TREATED=SEQ_NUM_RECEIVED_FROM_THE_SERVER
			print "sent :D "
		else :
			if GLOBAL_SERVER_SEQUENCE_NUMBER==SEQ_NUM_RECEIVED_FROM_THE_SERVER:
				pass
			else:
				GLOBAL_SERVER_SEQUENCE_NUMBER=GLOBAL_SERVER_SEQUENCE_NUMBER+1
				print  NICKNAME_SRC+" : "+DATA	
			reponse_message_serveur(1,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA)
			
	elif TYPE_MSG[0]=='E' :
		print "seq num ancien"
		print str(CLIENT_NEW_SEQ_NUMBER-1)
		print "seq number received"
		print str(SEQ_NUM_RECEIVED_FROM_THE_SERVER)
		if ACK==1 and SEQ_NUM_RECEIVED_FROM_THE_SERVER==(CLIENT_NEW_SEQ_NUMBER-1):
			print" liste recue"
			stopFlagGetPublicListeClients.set()
			affichage_liste_clients_recue(TAILLE_DATA,DATA)
			print" affichage de la liste termine"
			CLIENT_LAST_SEQUENCE_TREATED=SEQ_NUM_RECEIVED_FROM_THE_SERVER
		else:
			print "this case correponsds to an error in the specification"

	elif TYPE_MSG[0]=='F':
		if ACK==1:
			print "demande transmise au serveur, attente de reponse des clients...."
			stopFlagPrivateInvitation.set()
		elif ACK==0:
			print "sequence recue par du serveur : "+str(SEQ_NUM_RECEIVED_FROM_THE_SERVER)
			print "sequence enregitress : "+str(GLOBAL_SERVER_SEQUENCE_NUMBER)
			if GLOBAL_SERVER_SEQUENCE_NUMBER == SEQ_NUM_RECEIVED_FROM_THE_SERVER:
				if ACCEPT_INVITATION=="ACCEPT":
					message(1,0,CODE,'G',USERNAME_ENTERED_BY_USER,DATA)		
				elif ACCEPT_INVITATION=="DENY":
					message(1,1,CODE,'G',USERNAME_ENTERED_BY_USER,DATA)

			else:
				print "gerer invitation privee"
				print "----- THE CLIENT "+NICKNAME_SRC+" is inviting you for a private chat -----"
				print "type 'ACCEPT' to accept  'DENY' to deny the invitation"
				GLOBAL_SERVER_SEQUENCE_NUMBER=SEQ_NUM_RECEIVED_FROM_THE_SERVER
				acceptance_choice=raw_input()
				while acceptance_choice!="ACCEPT" and acceptance_choice!="DENY":
					acceptance_choice=raw_input()
			
				ACCEPT_INVITATION=acceptance_choice
				if ACCEPT_INVITATION=="ACCEPT":
					message(1,0,CODE,'G',USERNAME_ENTERED_BY_USER,DATA)		
				elif ACCEPT_INVITATION=="DENY":
					message(1,1,CODE,'G',USERNAME_ENTERED_BY_USER,DATA)
				print "sent message sent to the server"
		else:
			print "something bizarre is happening"

	elif TYPE_MSG[0]=='I':
		if ACK==1:
			stopFlagDeconnexion.set()
			print " -----------------Disconnection succeeded-----------------------"
			exit()
	
	elif ACK==1:
		if SEQ_NUM_RECEIVED_FROM_THE_SERVER<=CLIENT_LAST_SEQUENCE_TREATED:
			print "entered in SEQ_NUM_RECEIVED_FROM_THE_SERVER<=CLIENT_LAST_SEQUENCE_TREATED ligne 306"
			return
		else:
			print "what is going on here"
			return
	else :
		"""
		stopFlagConnetion.set()
		stopFlagChat.set()
		stopFlagGetPublicListeClients.set()
		"""
		print "message bizarre received"

		"""
		if type_msg=='B':
		if type_msg=='C':
		if type_msg=='D':
		if type_msg=='G':
		if type_msg=='H':
		"""
	
#Connexion-A----------------------------------------------------------------------------------------------------
def connexion(NICKNAME_SRC):
	global stopFlagConnetion 
	print "trying to connect ..."
	ACK=0
	FLAG=0
	CODE=0
	TYPE_MSG='A'
	DATA=''
	TAILLE_DATA=len(DATA)
	message(ACK,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA) 
	stopFlagConnetion = Event()
	thread = MyThread(stopFlagConnetion)
	thread.start()
	incrementSeq()

#ici c'est le chat normal 
def chat(discussion):
	global stopFlagChat 
	ACK=0
	FLAG=0
	CODE=0
	TYPE_MSG='C'
	DATA=discussion
	TAILLE_DATA=len(DATA)
	message(ACK,FLAG,CODE,TYPE_MSG,USERNAME_ENTERED_BY_USER,DATA)
	stopFlagChat = Event()
	thread = MyThread(stopFlagChat)
	thread.start()
	incrementSeq()
	incrementSynchroServeur()

#pour avoir la liste des clients connectees
def get_public_liste_clients(NICKNAME_SRC):
	global stopFlagGetPublicListeClients
	ACK=0
	CLIENT_NEW_SEQ_NUMBER=0 #on va gerer tout les numeros de sequences apres 
	FLAG=0
	CODE=0
	TYPE_MSG='E'
	DATA=''
	TAILLE_DATA=len(DATA)
	message(ACK,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA)   
	stopFlagGetPublicListeClients = Event()
	thread = MyThread(stopFlagGetPublicListeClients)
	thread.start()
	print "thread started"
	incrementSeq()

def invitation_messagerie_privee(NICKNAME_SRC):
	global stopFlagPrivateInvitation
	mode = raw_input("entrer 'DEC' pour decentralized mode : \nentrer 'CEN' pour centralized mode : ")
	if(mode=='CEN'):
		FLAG=0
	elif(mode=='DEC'):
		FLAG=1
	else : 
		print "wrong choice =>> starting system destruction X""D  "
		exit()

	chaine_liste_client_a_inviter=""
	inviter_un_autre=True
	while inviter_un_autre:
		nickname = raw_input("entrer le suivant si non taper 'END' pour finir : \n")
		if nickname=="END":
			break
		if (len(nickname)<=10 and len(nickname)>0):
			chaine_liste_client_a_inviter=chaine_liste_client_a_inviter+nickname+"&"
		else:
			print "longueur non valide veuillez entrez un username contenant entre 1 et 10 caracteres"
	chaine_liste_client_a_inviter=chaine_liste_client_a_inviter[0:-1]
	print "liste faite : "+ chaine_liste_client_a_inviter

	ACK=0
	CODE=0
	TYPE_MSG='F'
	DATA=chaine_liste_client_a_inviter
	TAILLE_DATA=len(DATA)
	message(ACK,FLAG,CODE,TYPE_MSG,NICKNAME_SRC,DATA)   
	stopFlagPrivateInvitation = Event()
	thread = MyThread(stopFlagPrivateInvitation)
	thread.start()
	print "thread started"
	incrementSeq()
#DECONNEXION-I----------------------------------------------------------------------------------------------------
def deconnexion():
	global stopFlagDeconnexion	
	ACK=0
	FLAG=0
	CODE=0
	TYPE_MSG='I'
	DATA=''
	TAILLE_DATA=len(DATA)
	message(ACK,FLAG,CODE,TYPE_MSG,USERNAME_ENTERED_BY_USER,DATA)   
	stopFlagDeconnexion = Event()
	thread = MyThread(stopFlagDeconnexion)
	thread.start()
	print "thread started"
	incrementSeq()

USERNAME_ENTERED_BY_USER = raw_input("Veuillez entrez votre username de session : ")

connexion(USERNAME_ENTERED_BY_USER)

input=[s,sys.stdin]

while True:
	readable, writable, exceptional = select.select(input, [], [])
	for r in readable:
		if r == s:
			paquet_recu, tuple_adresse = s.recvfrom(1024)
			ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA=resoudre_paquet(paquet_recu)

			traitement_paquet(ACK,SEQ_NUM_RECEIVED_FROM_THE_SERVER,FLAG,CODE,TYPE_MSG,USERNAME_SRC,TAILLE_DATA,DATA,tuple_adresse)

		elif r==sys.stdin :

			#ici si l'input de l'utilisateur est DISCONNECT sera entree on va appeler la fonction deconnexion
			#si non on prend le texte et on l'envoie comme un message de discussion 
			choix_utilisateur = raw_input()
			if choix_utilisateur=="DISCONNECT":
				deconnexion()
			elif choix_utilisateur=="GET_PUBLIC_USERS_LIST":
				get_public_liste_clients(USERNAME_ENTERED_BY_USER)
			elif choix_utilisateur=="PRIVATE_CHAT_INVITATION":
				invitation_messagerie_privee(USERNAME_ENTERED_BY_USER)
			else :
				chat(choix_utilisateur)
				print "trying to send..."

print ("---------------------- fin client ------------------------------")

