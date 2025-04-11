from Client import Client

ip = input("|Entrez l'adresse du serveur\t$>")
port = int(input("|Entrez un port valide\t\t$>"))
username = input("|Entrez votre nom d'utilisateur\t$>")

client = Client(ip, port, username)
client.init_routine()