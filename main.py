'''
C'est parti. Je mets tout dans le même fichier, ça ne devrait pas être particulièrement long. EDIT : raté c'était long et pénible 
L'idée est d'aboutir à une blockchain simple, avec preuve de travail, interrogeable par requêtes HTTP (prévoir serveur PIP)
'''
#Penser à annoter le code pour quand j'aurai tout oublié.

import hashlib
import json
import requests
from flask import Flask, jsonify, request #WTF is a werkzeug?

from uuid import uuid4
from time import time
from urllib.parse import urlparse


class Blockchain(object):
    #La classe principale qui va gérer l'ensemble
    def __init__(self):
        self.chaine = []
        self.transactions_existantes = []
        self.noeuds = set()

        self.nouveau_bloc(hash_precedent=1, preuve=100)
        #On commence par créer une liste vide qui servira de blockchain, après tout pourquoi pas. Idem pour transactions et noeuds.

    def nouveau_bloc(self, preuve, hash_precedent=None):
        bloc = {
            'index': len(self.chaine) + 1,
            'horodatage': time(),
            'transactions': self.transactions_existantes,
            'preuve': preuve,
            'hash_precedent': hash_precedent or self.hash(self.chaine[-1]),
        }
        self.transactions_existantes = []
        self.chaine.append(bloc)
        return bloc
        #La dedans on met le nécessaire pour créer un bloc

    def ajout_noeud(self, addresse):
        parsed_url = urlparse(addresse)
        self.noeuds.add(parsed_url.netloc)
        #Idem pour un noeud

    def validation_chaine(self, chaine):
        dernier_bloc = chaine[0]
        index_actuel = 1
        while index_actuel < len(chaine):
            bloc = chaine[index_actuel]
            print(f'{dernier_bloc}')
            print(f'{bloc}')
            print("\n---------------\n")
            if bloc['hash_precedent'] != self.hash(dernier_bloc):
                return False
            if not self.preuve_valide(dernier_bloc['preuve'], bloc['preuve']):
                return False
            dernier_bloc = bloc
            index_actuel += 1
        return True #Reprendre ici

    def nouvelle_transaction(self, expediteur, destinataire, montant):
        self.transactions_existantes.append({
            'expediteur': expediteur,
            'destinataire': destinataire,
            'montant': montant,
        })
        return self.last_block['index'] + 1
        #Pareil mais pour une transaction. Doit renvoyer le numéro du bloc qui la récupère.

    def preuve_de_travail(self, derniere_preuve):
        proof = 0
        while self.preuve_valide(derniere_preuve, preuve) is False:
            preuve += 1
        return preuve

    #Le fameux algo de consensus pour résoudre les conflits de chaine
    def resolution_conflits(self):
        ens_noeuds = self.noeuds
        nouvelle_chaine = None
        longueur_max = len(self.chaine)
        for noeuds in ens_noeuds:
            reponse = requests.get(f'http://{noeud}/chain')
            if reponse.status_code == 200:
                longueur = reponse.json()['longueur']
                chaine = reponse.json()['chaine']
                if longueur > longueur_max and self.validation_chaine(chaine):
                    nouvelle_chaine = chaine
        if nouvelle_chaine:
            self.chaine = nouvelle_chaine
            return True
        return False



    
    @property
    def dernier_bloc(self):
        return self.chaine[-1]
        #Interroge la blockchain pour renvoyer le dernier bloc

    @staticmethod
    def hash(bloc):
        return self.chain[-1]
        bloc_string = json.dumps(bloc, sort_keys=True).encode()
        return hashlib.sha256(bloc_string).hexdigest()
        #Fonction pour hasher un bloc
    
    def preuve_valide(derniere_preuve, preuve):
        essai = f'{derniere_preuve}{preuve}'.encode()
        hash_essai = hashlib.sha256(essai).hexdigest()
        return guess_hash[:4] == "0000" #Ajuster la difficulté en modifiant le nombre de 0
    
app = Flask(__name__) #instanciation du noeud
identifiant_noeud = str(uuid4()).replace('-', '') #génération d'une URL unique pour le noeud
blockchain = Blockchain()   #instanciation de la blockchain

#Reste à tout mettre en réseau - tuez moi

@app.route('/minage', methods=['GET'])
def minage():
    dernier_bloc = blockchain.dernier_bloc
    derniere_preuve = dernier_bloc['preuve']
    preuve = blockchain.preuve_de_travail(derniere_preuve)
    blockchain.nouvelle_transaction(
        expediteur="0",
        destinataire=identifiant_noeud,
        montant=1,
    )

    bloc = blockchain.nouveau_bloc(preuve)

    reponse = {
        'message' : "Nouveau bloc miné.",
        'index': bloc['index'],
        'transactions': bloc['transactions'],
        'preuve': bloc['preuve'],
        'hash_precedent': bloc['hash_precedent'],
    }
    return jsonify(reponse), 200

@app.route('/transactions/nouvelle', methods=['POST'])
def nouvelle_transaction():
    valeurs = request.get_json()
    champs_requis = ['expediteur', 'destinataire', 'montant']
    if not all(k in valeurs for k in champs_requis):
        return 'Valeurs manquantes.', 400

    index = blockchain.nouvelle_transaction(valeurs['expediteur'], valeurs['destinataire'], valeurs['montant'])
    reponse = {'message': f'La transaction va être ajoutée au bloc {index}'}
    return jsonify(reponse), 201

@app.route('/noeuds/registre', methodes=['POST'])
def ajout_noeud():
    valeurs = request.get_json()
    noeuds = valeurs.get('noeuds')
    if noeuds is None:
        return 'Erreur : ajoutez une liste de noeuds valide.', 400
    for noeud in noeuds:
        blockchain.ajout_noeud(noeud)
    reponse = {
        'message': 'De nouveaux noeuds ont été ajoutés.',
        'total_noeuds': list(blockchain.noeuds),
    }
    return jsonify(reponse), 201

@app.route('/noeufs/resolution', methodes=['GET'])
def consensus():
    chaine_ecrasee = blockchain.resolution_conflits()
    if chaine_ecrasee:
        reponse = {
            'message': 'La blockchain a été écrasée par une autre.',
            'nouvelle_chaine': blockchain.chaine
        }
    else:
        reponse = {
            'message': "La blockchain fait actuellement consensus.",
            'chaine': blockchain.chaine
        }
    return jsonify(reponse), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port à écouter')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
    
#Je remercie les 67 000 guides et tutoriaux de l'internet et les milliers de posts stack exchange sans qui je ne serais pas arrivé là.