# Hokan Gillot (20242295)
# Rachida Toumi (20171874)

# Voir code dans le rapport pour commentaires

import math
import random as rnd
import numpy as np
import requests
from collections import Counter
# fonctiond données

# convert string to list of integer
def str_to_int_list(x):
  z = [ord(a) for a in x  ]
  for x in z:
    if x > 256:
      print(x)
      return False
  return z

# convert a strint to an integer
def str_to_int(x):
  x = str_to_int_list(x)
  if x == False:
    print("Le text n'est pas compatible!")
    return False

  res = 0
  for a in x:
    res = res * 256 + a
  i = 0
  res = ""
  for a in x:
    ci = "{:08b}".format(a )
    if len(ci)>8:
      print()
      print("long",a)
      print()
    res = res + ci
  res = eval("0b"+res)
  return res

# exponentiation modulaire
def modular_pow(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if (exponent % 2 == 1):
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result

# fonction pour convertir int -> str
def int_to_str(x):
    chars = []
    while x > 0:
        prem_octet = x & 0xFF # prendre le 1er octet de la chaine
        chars.append(chr(prem_octet)) # on ajoute le caractère associé à l'octet
        x = x>>8 # on passe aux prochains 8 bits
    
    return ''.join(reversed(chars)) # on doit inverser la chaine car on a commencé de droite à gauche`

# Q1.1
# Clé publique Question 1.1
N = 143516336909281815529104150147210248002789712761086900059705342103220782674046289232082435789563283739805745579873432846680889870107881916428241419520831648173912486431640350000860973935300056089286158737579357805977019329557985454934146282550582942463631245697702998511180787007029139561933433550242693047924440388550983498690080764882934101834908025314861468726253425554334760146923530403924523372477686668752567287060201407464630943218236132423772636675182977585707596016011556917504759131444160240252733282969534092869685338931241204785750519748505439039801119762049796085719106591562217115679236583
e = 3

# Cryptogramme 1.1
C = 1101510739796100601351050380607502904616643795400781908795311659278941419415375
def racine_e(c, e):
    # on fait une binary search
    low, high = 0, c
    while low < high:
        mid = (low + high) // 2
        if mid**e > c:
            high = mid - 1 # cherche 1ere moitié
        elif mid**e < c:
            low = mid + 1 # chercher 2eme moitié
        else:
            return mid # on trouve une valeur entiere exacte
    return -1


m = racine_e(C, e)
print('m = '+str(m))

if C == modular_pow(m,e,N):
    #print(modular_pow(m,e,N))
    print('message trouvé, correspond au cryptogramme')

text = int_to_str(m)
print("Nom personnage:", text)

#Q1.2 (illustration de la méthode, voir rapport pour code au complet)

# ATTENTION : pour ne pas avoir à soumettre le kaggle dataset qu'on a utilisé, comme placeholder on utilise une liste d'auteurs choisit.
# Ceci est seulement pour ILLUSTRER la méthode (dictionnaire), voir le rapport`pour l'importation et les resultats avec le kaggle dataset.
# En réalité il faut le dataset BooksDatasetCLean.csv de kaggle (https://www.kaggle.com/datasets/elvinrustam/books-dataset?select=BooksDatasetClean.csv ) et faire
'''
import pandas as pd
data = pd.read_csv("BooksDatasetClean.csv")
authors = data["Authors"]
print(authors.head)

def get_one_author(name):
    name = name.replace("By ", "")
    auteurs = name.split(",")[0:2] 
    if len(auteurs) >= 2: # si 2 auteurs ou plus, on garde que le premier
        last, first = auteurs
        first = first.split(" ")[0] + " " + " ".join(first.split(" ")[1:])
        return first+' '+last
    return name 


authors = authors.apply(get_one_author)
'''


authors = ["Guy de Maupassant", "Molière", "Émile Zola", "Albert Camus", "Victor Hugo", "Agatha Christie",
                 "Stefan Zweig", "Antoine de Saint-Exupéry", "Voltaire", "Honoré de Balzac", "William Shakespeare",
                 "George Orwell", "Jules Verne", "Jean-Paul Sartre", "Charles Baudelaire", "Jean Anouilh",
                 "Boris Vian", "Eugène Ionesco", "JR Tolkien", "Gustave Flaubert", "Robert Louis Stevenson",
                 "Romain Gary", "Albert Cohen", "Pierre de Marivaux", "Jean Racine", "Georges Simenon",
                 "Alexandre Dumas", "Franz Kafka", "Jean Giono", "Primo Levi", "Prosper Mérimée", "Jack London",
                 "John Steinbeck", "René Barjavel", "Isaac Asimov", "Marguerite Duras", "Jane Austen", "Marcel Proust",
                 "Françoise Sagan", "La Fontaine", "Pierre Corneille", "Denis Diderot", "Céline", "Alfred de Musset",
                 "Molière", "Arthur Conan Doyle", "Marcel Pagnol", "Dostoïevski", "Oscar Wilde", "Beaumarchais",
                 "Stendhal"]


def attack_dictionnaire(C, e, N, name_list):
    for name in name_list:
        m_guess = str_to_int(name)
        C_guess = modular_pow(m_guess, e, N)
        if C_guess == C:
            return name 
    return 'Auteur pas trouvé'

N_2 = 172219604291138178634924980176652297603347655313304280071646410523864939208855547078498922947475940487766894695848119416017067844129458299713889703424997977808694983717968420001033168722360067307143390485095229367172423195469582545920975539060699530956357494837243598213416944408434967474317474605697904676813343577310719430442085422937057220239881971046349315235043163226355302567726074269720408051461805113819456513196492192727498270702594217800502904761235711809203123842506621973488494670663483187137290546241477681096402483981619592515049062514180404818608764516997842633077157249806627735448350463
e_2 = 173
C_2 = 25782248377669919648522417068734999301629843637773352461224686415010617355125387994732992745416621651531340476546870510355165303752005023118034265203513423674356501046415839977013701924329378846764632894673783199644549307465659236628983151796254371046814548224159604302737470578495440769408253954186605567492864292071545926487199114612586510433943420051864924177673243381681206265372333749354089535394870714730204499162577825526329944896454450322256563485123081116679246715959621569603725379746870623049834475932535184196208270713675357873579469122917915887954980541308199688932248258654715380981800909

m2 = attack_dictionnaire(C_2, e_2, N_2, authors)
print('------------------------------------')
print('C = '+str(modular_pow(str_to_int(m2),e_2, N_2))) # cipher associÃ©
print('m = '+str(str_to_int(m2)))
print(m2)

