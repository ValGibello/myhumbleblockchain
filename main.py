'''
C'est parti. Je mets tout dans le même fichier, ça ne devrait pas être particulièrement long. 
L'idée est d'aboutir à une blockchain simple, avec preuve de travail, interrogeable par requêtes HTTP (prévoir serveur PIP).abs
'''


import hashlib
import json

from time import time

class Blockchain(object):
    #La classe principale qui va gérer l'ensemble
    def __init__(self):
        self.chain = []
        self.transactions_existantes = []
        self.new_block(previous_hash=1, proof=100)
        #On commence par créer une liste vide qui servira de blockchain

    def nouveau_bloc(self):
        bloc = {
            'index': len(self.chain) + 1,
            'horodatage': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'dernier_hash': self.hash(self.chain[-1]),
        }
        self.transactions_existantes = []
        self.ajout_chaine(bloc)
        return bloc
        #La dedans on met le nécessaire pour créer un bloc

    def nouvelle_transaction(self, expediteur, destinataire, valeur):
        self.transactions_existantes.append({
            'expediteur': expediteur,
            'destinataire': destinataire,
            'valeur': valeur,
        })
        return self.last_block['index'] + 1
        #Pareil mais pour une transaction. Doit renvoyer le numéro du bloc qui la récupère.

    @staticmethod
    def hash(bloc):
        pass
        #Fonction pour hasher un bloc
    
    @property

    def dernier_bloc(self):
        pass
        #Interroge la blockchain pour renvoyer le dernier bloc

    

