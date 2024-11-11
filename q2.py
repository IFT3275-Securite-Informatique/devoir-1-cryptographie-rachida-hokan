# Hokan Gillot (20242295)
# Rachida Toumi (20171874)

from asyncio import wait
import time
from crypt import *
import random
from collections import Counter
import requests
from bs4 import BeautifulSoup

symboles = ['b', 'j', '\r', 'J', '”', ')', 'Â', 'É', 'ê', '5', 't', '9', 'Y', '%', 'N', 'B', 'V', '\ufeff', 'Ê', '?', '’', 
            'i', ':', 's', 'C', 'â', 'ï', 'W', 'y', 'p', 'D', '—', '«', 'º', 'A', '3', 'n', '0', 'q', '4', 'e', 'T', 'È', 
            '$', 'U', 'v', '»', 'l', 'P', 'X', 'Z', 'À', 'ç', 'u', '…', 'î', 'L', 'k', 'E', 'R', '2', '_', '8', 'é', 'O',
              'Î', '‘', 'a', 'F', 'H', 'c', '[', '(', "'", 'è', 'I', '/', '!', ' ', '°', 'S', '•', '#', 'x', 'à', 'g', '*',
                'Q', 'w', '1', 'û', '7', 'G', 'm', '™', 'K', 'z', '\n', 'o', 'ù', ',', 'r', ']', '.', 'M', 'Ç', '“', 'h', 
                '-', 'f', 'ë', '6', ';', 'd', 'ô', 'e ', 's ', 't ', 'es', ' d', '\r\n', 'en', 'qu', ' l', 're', ' p', 'de',
                  'le', 'nt', 'on', ' c', ', ', ' e', 'ou', ' q', ' s', 'n ', 'ue', 'an', 'te', ' a', 'ai', 'se', 'it', 'me',
                    'is', 'oi', 'r ', 'er', ' m', 'ce', 'ne', 'et', 'in', 'ns', ' n', 'ur', 'i ', 'a ', 'eu', 'co', 'tr', 
                    'la', 'ar', 'ie', 'ui', 'us', 'ut', 'il', ' t', 'pa', 'au', 'el', 'ti', 'st', 'un', 'em', 'ra', 'e,', 
                    'so', 'or', 'l ', ' f', 'll', 'nd', ' j', 'si', 'ir', 'e\r', 'ss', 'u ', 'po', 'ro', 'ri', 'pr', 's,',
                      'ma', ' v', ' i', 'di', ' r', 'vo', 'pe', 'to', 'ch', '. ', 've', 'nc', 'om', ' o', 'je', 'no', 'rt', 
                      'à ', 'lu', "'e", 'mo', 'ta', 'as', 'at', 'io', 's\r', 'sa', "u'", 'av', 'os', ' à', ' u', "l'", "'a",
                      'rs', 'pl', 'é ', '; ', 'ho', 'té', 'ét', 'fa', 'da', 'li', 'su', 't\r', 'ée', 'ré', 'dé', 'ec', 'nn', 
                      'mm', "'i", 'ca', 'uv', '\n\r', 'id', ' b', 'ni', 'bl']

bigrams = []
for s in symboles:
    if len(s) == 2:
        bigrams.append(s)

print(bigrams)

# la vraie clé et mapping. On ne l'utilise pas, juste pour comparer
K = gen_key(symboles)
real_mapping = {v: k for k, v in K.items()}

# recuperer l'ensemble de textes francais de gutenberg (les urls)
def get_french_books_urls():
    base_url = "https://www.gutenberg.org/browse/languages/fr"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = soup.find_all('a', href=True)
    book_urls = []
    
    for link in links:
        href = link['href']
        if href.startswith('/ebooks/') and href.split('/')[-1].isdigit():
            book_id = href.split('/')[-1]
            book_url = f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8"
            book_urls.append(book_url)
    
    return book_urls


def get_cipher_mapping(C):
  chunks = [C[i:i + 8] for i in range(0, len(C), 8)]

  code_freq = Counter(chunks)
  all_8bit_codes = ["{:08b}".format(i) for i in range(256)]
  complete_code = {code_key: code_freq.get(code_key, 0) for code_key in all_8bit_codes}
  total_code_freq = sum(complete_code.values())
  normalized_code = {k: v / total_code_freq for k, v in complete_code.items()}
  normalized_code_freq = dict(sorted(normalized_code.items(), key=lambda item: item[1], reverse=True))
  return normalized_code_freq


def get_freq_mapping(urls):
  freq_map = Counter()

  def get_text_symbols(text, bichars):
      symbols = []
      i = 0
      while i < len(text):
          if i + 1 < len(text) and text[i:i+2] in bichars:
              symbols.append(text[i:i+2])
              i += 2 
          else:
              symbols.append(text[i])
              i += 1
      return symbols

  bichars = [symbol for symbol in symboles if len(symbol) == 2]
  for url in urls:
      try:
          text = load_text_from_web(url)
          M = text[10000:] # oublier les 10 000 premiers chars
          if not text:
              print(f"Failed to load content from {url}")
              continue
          
          text_symbols = get_text_symbols(M, bichars)
          freq_map.update(text_symbols)

      except Exception as e:
          print(f"Error processing {url}: {e}")

  # garder seulement les symboles qu'on a dans "symboles"
  filtered_freq_map = {symbol: freq for symbol, freq in freq_map.items() if symbol in symboles}
  freq = dict(sorted(filtered_freq_map.items(), key=lambda item: item[1], reverse=True))
  complete_freq = {symbol_key: freq.get(symbol_key, 0) for symbol_key in symboles}
  total_symbol_freq = sum(complete_freq.values())
  normalized_freq = {k: v / total_symbol_freq for k, v in complete_freq.items()}
  normalized_freq = dict(sorted(normalized_freq.items(), key=lambda item: item[1], reverse=True))
  return normalized_freq
  

def load_french_dictionary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [word.strip().lower() for word in file if word.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred while loading the dictionary: {e}")
        return []

def decrypt_with_map(ciphertext, mapping):
    text = []
    for i in range(0, len(ciphertext), 8):
        chunk = ciphertext[i:i+8]
        text.append(mapping.get(chunk))
    return ''.join(text)
    


# fonctions pour utiliser du NLP, trouver les plus proches mots
from difflib import get_close_matches
import re

def find_closest_valid_word(word, dictionary):
    return get_close_matches(word, dictionary, n=1, cutoff=0.7)

def identify_incorrect_words(decoded_text, dictionary):
    words = re.findall(r'\b\w+\b', decoded_text)
    return [word for word in words if word not in dictionary]

def update_mapping_for_word(incorrect_word, correct_word, mapping, ciphertext, chunk_size=8):
    chunks = [ciphertext[i:i + chunk_size] for i in range(0, len(ciphertext), chunk_size)]

    for i, (inc_char, cor_char) in enumerate(zip(incorrect_word, correct_word)):
        if inc_char != cor_char:
            chunk_to_update = chunks[i] 
            mapping[cor_char] = chunk_to_update
            break

    return mapping

def count_valid_words(decoded_text, dictionary): # pour evaluer si on s'ameliore ou pas
    words = decoded_text.strip().split(' ')
    return sum(1 for word in words if word in dictionary)

# max_correction a augmenter si pas de bons resultats (pour corriger plus de mots)
def refine_mapping(curr_text, mapping, dictionary, ciphertext, max_corrections=50):
    corrections = 0
    incorrect_words = identify_incorrect_words(curr_text, dictionary)
    print(f"nombre mots incorrects: {len(incorrect_words)}")

    for word in incorrect_words: # iterer a travers tous les mots incorrects est tres demandant, on doit limiter
        if corrections >= max_corrections:
            break

        closest_word = find_closest_valid_word(word, dictionary)
        print(f"refining '{word}' to '{closest_word}'")
        if closest_word:
            closest_word = closest_word[0]  # Get the first match
            mapping = update_mapping_for_word(word, closest_word, mapping, ciphertext)

            curr_text = decrypt_with_map(ciphertext, mapping)
            corrections += 1

    return mapping, curr_text


def decrypt(C):
    chunks = [C[i:i + 8] for i in range(0, len(C), 8)]

    # version avec seulement 2 exemples 
    #french_book_urls = ["https://www.gutenberg.org/ebooks/13846.txt.utf-8","https://www.gutenberg.org/ebooks/4650.txt.utf-8"]
    all_french_book_urls = get_french_books_urls() # grand ensemble de textes francais
    french_books_urls = ["https://www.gutenberg.org/ebooks/13846.txt.utf-8","https://www.gutenberg.org/ebooks/4650.txt.utf-8"] # prendre ces 2 là pour les tests, à enlever pour les autres tests`
    french_books_urls.append(all_french_book_urls[:20]) # prendre 20 autres, on limite le nombre pour que ça prenne moins de temps. Mais prendre tous les urls si on veut des frequences fiables
    freq_mapping = get_freq_mapping(french_books_urls)
    cipher_mapping = get_cipher_mapping(C)
    
    mapping = dict(zip(cipher_mapping.keys(), freq_mapping.keys()))
    print(mapping)
    inv_mapping = {value: key for key, value in mapping.items()}


    # Analyse manuelle fonctionne seulement jusqu'à un certain point, on veut automatiser le processus`
    #--------------------------------------------------------------------------------------------
    processed_chunks = ['e ' if chunk==inv_mapping.get('e ') else chunk for chunk in chunks]
    m2 = ''.join(processed_chunks)
    m2_list = m2.split(' ')
    # Filter for sequences ending with 'e' (i.e., 8-bit + 'e')
    filtered_sequences = [m[:-1] for m in m2_list if len(m) == 8 + 1 and m[-1] == 'e']
    sequence_counts = Counter(filtered_sequences)
    most_common_sequence = sequence_counts.most_common(10)
    print(most_common_sequence[0][0]) # a tres forte proba, c'est qu
    for i in range(len(chunks)):
        # On peut etre assez sur que 'e ' est le symbol le plus common pour la majorité des textes
        if inv_mapping.get('e ') == chunks[i]:
            chunks[i] = 'e '
        # En partant de 'e ', on peut deduire d'autres symboles (par frequence)
        elif most_common_sequence[0][0] == chunks[i]:
            chunks[i] = 'qu'
    m = ''.join(chunks)
    # mis a jour du mapping
    replace1 = inv_mapping.get('qu') 
    replace2 = mapping.get(most_common_sequence[0][0])
    inv_mapping['qu'] = most_common_sequence[0][0]
    inv_mapping[replace2] = replace1
    mapping = {v: k for k, v in inv_mapping.items()}
    print(mapping)
    #--------------------------------------------------------------------------------------------

    # En utilisant un dictionnaire de mots francais, on va chercher a trouver le meilleur mapping possible (on a deja trouve pour 'e ' et 'qu')
    # meilleur = qui correspond avec le plus de mots francais 
    dictionnaire = load_french_dictionary('liste.de.mots.francais.frgut.txt')
    initial_map = {'e ' : inv_mapping.get('e '), 'qu': inv_mapping.get('qu')}



    curr_text = decrypt_with_map(C, mapping)

    refined_mapping, refined_text = refine_mapping(curr_text, mapping, dictionnaire, C, max_corrections=50)

    print("nouveau mapping:", refined_mapping)
    return refined_text
    


'''

url1 = "https://www.gutenberg.org/ebooks/13846.txt.utf-8"
corpus1 = load_text_from_web(url1)
url2 = "https://www.gutenberg.org/ebooks/4650.txt.utf-8"
corpus2 = load_text_from_web(url2)
corpus = corpus1 + corpus2
caracteres = list(set(list(corpus)))
nb_caracteres = len(caracteres)
nb_bicaracteres = 256 - nb_caracteres
bicaracteres = [item for item, _ in Counter(cut_string_into_pairs(corpus)).most_common(nb_bicaracteres)]
symboles = ['b', 'j', '\r', 'J', '”', ')', 'Â', 'É', 'ê', '5', 't', '9', 'Y', '%', 'N', 'B', 'V', '\ufeff', 'Ê', '?', '’', 'i', ':', 's', 'C', 'â', 'ï', 'W', 'y', 'p', 'D', '—', '«', 'º', 'A', '3', 'n', '0', 'q', '4', 'e', 'T', 'È', '$', 'U', 'v', '»', 'l', 'P', 'X', 'Z', 'À', 'ç', 'u', '…', 'î', 'L', 'k', 'E', 'R', '2', '_', '8', 'é', 'O', 'Î', '‘', 'a', 'F', 'H', 'c', '[', '(', "'", 'è', 'I', '/', '!', ' ', '°', 'S', '•', '#', 'x', 'à', 'g', '*', 'Q', 'w', '1', 'û', '7', 'G', 'm', '™', 'K', 'z', '\n', 'o', 'ù', ',', 'r', ']', '.', 'M', 'Ç', '“', 'h', '-', 'f', 'ë', '6', ';', 'd', 'ô', 'e ', 's ', 't ', 'es', ' d', '\r\n', 'en', 'qu', ' l', 're', ' p', 'de', 'le', 'nt', 'on', ' c', ', ', ' e', 'ou', ' q', ' s', 'n ', 'ue', 'an', 'te', ' a', 'ai', 'se', 'it', 'me', 'is', 'oi', 'r ', 'er', ' m', 'ce', 'ne', 'et', 'in', 'ns', ' n', 'ur', 'i ', 'a ', 'eu', 'co', 'tr', 'la', 'ar', 'ie', 'ui', 'us', 'ut', 'il', ' t', 'pa', 'au', 'el', 'ti', 'st', 'un', 'em', 'ra', 'e,', 'so', 'or', 'l ', ' f', 'll', 'nd', ' j', 'si', 'ir', 'e\r', 'ss', 'u ', 'po', 'ro', 'ri', 'pr', 's,', 'ma', ' v', ' i', 'di', ' r', 'vo', 'pe', 'to', 'ch', '. ', 've', 'nc', 'om', ' o', 'je', 'no', 'rt', 'à ', 'lu', "'e", 'mo', 'ta', 'as', 'at', 'io', 's\r', 'sa', "u'", 'av', 'os', ' à', ' u', "l'", "'a", 'rs', 'pl', 'é ', '; ', 'ho', 'té', 'ét', 'fa', 'da', 'li', 'su', 't\r', 'ée', 'ré', 'dé', 'ec', 'nn', 'mm', "'i", 'ca', 'uv', '\n\r', 'id', ' b', 'ni', 'bl']
nb_symboles = len(symboles)
dictionnaire = gen_key(symboles)
random.seed(time.time())
a = random.randint(3400, 7200)
b = random.randint(96000, 125000)
l = a+b
c = random.randint(0, len(corpus)-l)
M = corpus[c:c+l]
K = gen_key(symboles)
C = chiffrer(M, K, dictionnaire)
original_message = M  # Remplacer par le texte original utilisé pour le chiffrement
cryptogram = C  # Remplacer par le cryptogramme chiffré
#----------------------------------------------------------\

decrypt(C)
'''

# decrypt en connaissant la clé
'''
def decrypt(C):
    # The key mapping K is given
    symboles = ['b', 'j', '\r', 'J', '”', ')', 'Â', 'É', 'ê', '5', 't', '9', 'Y', '%', 'N', 'B', 'V', '\ufeff', 'Ê', '?', '’', 'i', ':', 's', 'C', 'â', 'ï', 'W', 'y', 'p', 'D', '—', '«', 'º', 'A', '3', 'n', '0', 'q', '4', 'e', 'T', 'È', '$', 'U', 'v', '»', 'l', 'P', 'X', 'Z', 'À', 'ç', 'u', '…', 'î', 'L', 'k', 'E', 'R', '2', '_', '8', 'é', 'O', 'Î', '‘', 'a', 'F', 'H', 'c', '[', '(', "'", 'è', 'I', '/', '!', ' ', '°', 'S', '•', '#', 'x', 'à', 'g', '*', 'Q', 'w', '1', 'û', '7', 'G', 'm', '™', 'K', 'z', '\n', 'o', 'ù', ',', 'r', ']', '.', 'M', 'Ç', '“', 'h', '-', 'f', 'ë', '6', ';', 'd', 'ô', 'e ', 's ', 't ', 'es', ' d', '\r\n', 'en', 'qu', ' l', 're', ' p', 'de', 'le', 'nt', 'on', ' c', ', ', ' e', 'ou', ' q', ' s', 'n ', 'ue', 'an', 'te', ' a', 'ai', 'se', 'it', 'me', 'is', 'oi', 'r ', 'er', ' m', 'ce', 'ne', 'et', 'in', 'ns', ' n', 'ur', 'i ', 'a ', 'eu', 'co', 'tr', 'la', 'ar', 'ie', 'ui', 'us', 'ut', 'il', ' t', 'pa', 'au', 'el', 'ti', 'st', 'un', 'em', 'ra', 'e,', 'so', 'or', 'l ', ' f', 'll', 'nd', ' j', 'si', 'ir', 'e\r', 'ss', 'u ', 'po', 'ro', 'ri', 'pr', 's,', 'ma', ' v', ' i', 'di', ' r', 'vo', 'pe', 'to', 'ch', '. ', 've', 'nc', 'om', ' o', 'je', 'no', 'rt', 'à ', 'lu', "'e", 'mo', 'ta', 'as', 'at', 'io', 's\r', 'sa', "u'", 'av', 'os', ' à', ' u', "l'", "'a", 'rs', 'pl', 'é ', '; ', 'ho', 'té', 'ét', 'fa', 'da', 'li', 'su', 't\r', 'ée', 'ré', 'dé', 'ec', 'nn', 'mm', "'i", 'ca', 'uv', '\n\r', 'id', ' b', 'ni', 'bl']
    K = gen_key(symboles)
    # Invert the key mapping to get binary code to symbol mapping
    K_inv = {v: k for k, v in K.items()}
    print(K_inv)
    # Split the ciphertext into 8-bit chunks
    chunk_size = 8
    chunks = [C[i:i + chunk_size] for i in range(0, len(C), chunk_size)]
    code_freq = Counter(chunks)
    print(code_freq)

    # Map chunks back to symbols
    symbols = [K_inv.get(chunk, '?') for chunk in chunks]

    # Concatenate symbols to get the plaintext
    M = ''.join(symbols)
    return M
'''
