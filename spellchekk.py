#!/usr/bin/python

# This solves the problem located, at some point in time, here:
# http://www.justin.tv/problems/spellcheck

# The problem 
# Write a program that reads a large list of English words (e.g. from /usr/share/dict/words on a unix system) into memory, and then reads words from stdin, and prints either the best spelling suggestion, or "NO SUGGESTION" if no suggestion can be found. The program should print ">" as a prompt before reading each word, and should loop until killed.

# For example:

# > sheeeeep
# sheep
# > peepple
# people
# > sheeple
# NO SUGGESTION

# The class of spelling mistakes to be corrected is as follows:

#     * Case (upper/lower) errors: "inSIDE" => "inside"
#     * Repeated letters: "jjoobbb" => "job"
#     * Incorrect vowels: "weke" => "wake"

# Any combination of the above types of error in a single word should be corrected (e.g. "CUNsperrICY" => "conspiracy").

# If there are many possible corrections of an input word, your program can choose one in any way you like. It just has to be an English word that is a spelling correction of the input by the above rules.



import readline
import re
import random

# open a corpus of words for comparing with the spell checker.
_words = open('/usr/share/dict/words', 'rb')


def make_word_list():
    _l = {'lower': [],
          'normal': []}
    for word in _words.readlines():
        _l['lower'].append(word.lower().strip())
        _l['normal'].append(word.strip())
    return _l


word_list = make_word_list()                  


def check(_word):
    """
    Checks to see if a word is in the corpus of words; if it
    is, return False, since there is no need to parse it as a
    misspelling
    """

    if _word.lower() in word_list['lower']:
        return word_list['normal'][word_list['lower'].index(_word.lower())]
    else: return False


class Inspector(object):
    """
    Read a word and parse it before creating a list that represents the number
    of times each uquique letter is repeated
    """

    def __init__(self, _word):
        self.word = _word
        self.matrix_seed = []
        self.resultlist_dicts = []

    def unique_letters(self):
        """return a list of all unique letters in a word"""
        _l = []
        for letter in self.word:
            if letter not in _l:
                _l.append(letter)
        return _l
            
    def re_gt_2(self):
        """return a list of compiled regular expression objects
        for each letter that is repeated twice or more."""

        return [re.compile("%s{2,}" % x) for x in self.unique_letters()]

    def letters_gt_2(self):
        """
        returns a list of re.finditer objects for each letter unique letter
        in self.word
        """
        _list = self.re_gt_2()
        _l = []
        for x in _list:
            _l.append(re.finditer(x, self.word))
        print("this is letters_gt_2: %s" % _l)
        return [list(i) for i in _l]    

    def _start(self, _list):
        if len(_list) > 0:
            for i in _list:
                self.resultlist_dicts.append({i.group(): i.start()})
        return None
        
    def showthis(self, _list):
        for i in _list:
            self._start(i)
        return None

    def inspect(self):
        self.showthis(self.letters_gt_2())
        self.sorted = sorted(self.resultlist_dicts, key=lambda x: x[x.keys()[0]], reverse=True)

        return self.sorted

    def seeder(self):
        """
        returns a list to seed the Matrixer class
        """
        return [len(i.keys()[0]) for i in self.resultlist_dicts]


class Matrixer(object):
    """
    accepts a list of the quantity of all repeated letters in order as they occur
    in a word.
    returns a matrix of all permutations of integers from 1 to n for each item in 
    the list given; n being the integer in the list given.
    """

    def __init__(self, input_list):
        self.matrix = []
        self.list = input_list
    def _iterate(self, _list):
        tuple_map = [(n, m) for n, m in zip(_list, range(len(_list)))]
        for item in tuple_map:
            for x in range(item[0]):
                if item[0] == 1:
                    return None
                new_item = item[0] - 1
                _new_list = self.join_lists(_list, new_item, item[1])
                if _new_list not in self.matrix:
                    self.matrix.append(_new_list)
                    self._iterate(_new_list)
        return None

    def solve(self):

        self.matrix.append(self.list)

        self._iterate(self.list)

        return self.matrix

    def join_lists(self, _list, new_item, index):
        _l = []
        front, middle, back = self.partition_list(_list, index)
        if front == []:
            _l.append(new_item)
            for i in back:
                _l.append(i)
        elif back == []:
            for i in front:
                _l.append(i)
            _l.append(new_item)
        else:
            for i in front:
                _l.append(i)
            _l.append(new_item)
            for i in back:
                _l.append(i)
                
        return _l
    def partition_list(self, _list, index):
        try:
            if index == -1:
                raise IndexError
            else:
                front = _list[:index]
        finally:
            pass
        
        try:
            middle = _list[index]
        finally:
            pass
        try:
            back = _list[index+1:]
        except IndexError:
            back = []
        finally:
            pass
        return (front, middle, back)

class Candidater(object):
    """



    """

    def __init__(self, inspection, matrix_list, word):
        self.inspection = inspection
        self.matrix = matrix_list
        self.word = word
        self.candidates = []

    def replacer(self, matrix_item):
        recipelist_tuples = zip([key for key in self.inspection], matrix_item) 
        minor_candidate = []
        
        for item in recipelist_tuples:
            
            caboose = self.word_element[item[0].values()[0]:]
            back = self.word_element[:item[0].values()[0]]
            caboose = caboose.replace(item[0].keys()[0], item[0].keys()[0][:item[1]])
            minor_candidate.append(caboose)
            self.word_element = back
        try:
            minor_candidate.append(back)
            minor_candidate.reverse()
            self.candidates.append(''.join(minor_candidate))
        except UnboundLocalError:
            pass        

    def check_candidate(self):
        
        for matrix_item in self.matrix:
            self.word_element = self.word[:]    
            self.replacer(matrix_item)

        return self.candidates


class Voweller(object):
    """
    
    """


    def __init__(self, word_candidate):
        self.vowels = ('a', 'e', 'i', 'o', 'u')
        self.resultlist = []
        self.word = word_candidate

    def the_vowels(self):
        _l = []
        for letter in self.word:
            if letter not in _l and letter in self.vowels:
                _l.append(letter)
        return _l
    def re_vowels(self):
        return [re.compile("%s{1,}" % x) for x in self.the_vowels()]

    def vowel_list(self):
        _list = self.re_vowels()
        _l = []
        for x in _list:
            _l.append(re.finditer(x, self.word))
        return [list(i) for i in _l]    

    def _start(self, _list):
        if len(_list) > 0:
            for i in _list:
                self.resultlist.append({i.group(): i.start()})
        return None
        
    def showthis(self, _list):
        for i in _list:
            self._start(i)
        return None
    
    def inspect(self):
        self.showthis(self.vowel_list())
        self.sorted = sorted(self.resultlist, key=lambda d: d[d.keys()[0]], reverse=True)
        return self.sorted

    def seeder(self):
        """
        returns a list of the integer 5 for each unique
        """
        print("This is self.resultlist in Voweller: %s" % self.resultlist)
        return [5 for i in self.resultlist]
        

class VowelCandidater(object):
    """
    compares every permutation of vowel combination with each vowel 
    in a word.

    accepts a list of dictionaries that are the vowel and
    the index in which it occurs, a 
    """

    def __init__(self, inspection, matrix_list, word):
        print("this is the VowelCandidater inspection: %s" % inspection)
        print("this is the VowelCandidater matrix_list: %s" % matrix_list)
        self.inspection = inspection

        self.matrix = matrix_list
        self.word = word
        self.candidates = []
        self.vowels = ('a', 'e', 'i', 'o', 'u')
        
    def replacer(self, matrix_item):
        recipelist_tuples = zip([x for x in self.inspection], matrix_item) 
        minor_candidate = []
        for item in recipelist_tuples:
            
            caboose = self.word_element[item[0].values()[0]:]
            
            back = self.word_element[:item[0].values()[0]]
            caboose = caboose.replace(item[0].keys()[0][0], self.vowels[item[1]-1])
            
            minor_candidate.append(caboose)
            self.word_element = back
        try:
            minor_candidate.append(back)
            minor_candidate.reverse()
            word_candidate = ''.join(minor_candidate)
            self.candidates.append(word_candidate)
        except UnboundLocalError:
            pass
    def check_candidate(self):

        for matrix_item in self.matrix:
            self.word_element = self.word[:]
            self.replacer(matrix_item)
        return self.candidates

    

def spell_checker(_word):
    actual_words = []
    I = Inspector(_word); 
    inspection = I.inspect()

    matrix_seed = I.seeder()
    print matrix_seed
    M = Matrixer(matrix_seed)
    matrix = M.solve()
    
    C = Candidater(inspection, matrix, _word)
    candidates = C.check_candidate()
    
    if matrix == [[]]:
        
        V = Voweller(_word)
        vowel_inspection =  V.inspect()
        VM = Matrixer(V.seeder())
        vowel_matrix = VM.solve()
        
        c = VowelCandidater(vowel_inspection, vowel_matrix, _word)
        candidates = c.check_candidate()

        for word_candidate in candidates:
            if check(word_candidate) and check(word_candidate) not in actual_words:
                actual_words.append(check(word_candidate))
        return actual_words
    
    else:
    
        for candidate in candidates:

            V = Voweller(candidate)
            vowel_inspection =  V.inspect()
            VM = Matrixer(V.seeder())
            vowel_matrix = VM.solve()
            
            c = VowelCandidater(vowel_inspection, vowel_matrix, candidate)
            candidates = c.check_candidate()
            for word_candidate in candidates:
                if check(word_candidate) and check(word_candidate) not in actual_words:
                    actual_words.append(check(word_candidate))
        return actual_words


def select_random(_list):
    selector = random.randint(0, len(_list) - 1)
    return _list[selector]

def prompt():
    _input = raw_input('> ')
    if check(_input) == False:
        these_words = spell_checker(_input.lower())
        print these_words
        if these_words == []:
            return 'NO SUGGESTION'
        
        elif len(these_words) == 1:
            return these_words[0]
        else:
            return select_random(these_words)
    else:
        return check(_input)


while True:
    print prompt()
