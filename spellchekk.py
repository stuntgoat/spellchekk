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


def make_word_lists():
    """
    creates a dict of 2 lists of the words,
    an upper case list and a lower case list
    """
    
    tmp_list = {'lower': [],
          'normal': []}
    for word in _words.readlines():
        tmp_list['lower'].append(word.lower().strip())
        tmp_list['normal'].append(word.strip())
    return tmp_list


word_list = make_word_lists()                  


def check(_word):
    """
    Checks to see if a word is in the corpus of words; if it
    is, return False, since there is no need to parse it as a
    misspelling
    """

    if _word.lower() in word_list['lower']:
        return word_list['normal'][word_list['lower'].index(_word.lower())]
    else: 
        return False


class Inspector(object):
    """
    Checks duplicate letters in a word.
    
    Returns a list of dicts that are the letter that is repeated as the dict key and the index of 
    that letter-group in the word as the dict value.

    Also provides a seeder method for passing a list to the Matrixer class.
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
        returns a list of the following items:
        - an empty list, if re.finditer contains an empty iterator object or
        - a list containing the re.MatchObject
        """
        re_list = self.re_gt_2()
        _l = []
        for x in re_list:
            _l.append(re.finditer(x, self.word))
        
        return [list(i) for i in _l]    

    def _start(self, re_matchobject_list):
        """
        append a dict of the compiled re from self.re_gt_2 and the index 
        of the occurence of the re in self.word
        """

        if len(re_matchobject_list) > 0:
            for i in re_matchobject_list:
                self.resultlist_dicts.append({i.group(): i.start()})
        return None
        
    def call_start(self, _list):
        """
        call self._start on each unique letter in self.word
        """
        for i in _list:
            self._start(i)
        return None

    def inspect(self):
        """
        returns a list of dicts containing the letter that is duplicated as key and the index
        as value
        """
        self.call_start(self.letters_gt_2())
        self.sorted = sorted(self.resultlist_dicts, key=lambda x: x[x.keys()[0]], reverse=True)
 
        return self.sorted

    def seeder(self):
        """
        returns a list to seed the Matrixer class
        """
        return [len(i.keys()[0]) for i in self.resultlist_dicts]


class Matrixer(object):
    def __init__(self, initial_list):
        
        # print initial_list
        self.list = initial_list
        self.length = len(initial_list)
        self.matrix = []

    def rangeit(self, num):
        return [[x] for x in range(1, num + 1)]
    
    def add_lists(self, one, two):
        """
        creates a matrix between the ranges of each integer in the given array
        """
        tmp_array = []
        while len(one) > 0:
            last = one.pop()
            for elem in two:
                for i in range(1, last + 1):
                    _next = [i] + elem
                    tmp_array.append(_next)
                    # if the _next list is the same length
                    # as the original list, this is a final iteration,
                    # so append it to self.matrix
                    if len(_next) == self.length:
                        self.matrix.append(_next)

            self.add_lists(one, tmp_array)
                    
        return None

    def solve(self):
        
        if len(self.list) == 1:
            # return a list of lists containing an integer within
            # range of the single integer
            return self.rangeit(self.list[0])
        elif len(self.list) == 0:
            return [[]]
        else:
            
            last = self.list.pop()
            last_as_list = self.rangeit(last)
            self.add_lists(self.list, last_as_list)
            return self.matrix




class Candidater(object):
    """
    Returns a list of all permutations of a word based on a list of dicts returned from 
    Inspector and a matrix_list of permutations of quantities of repeated characters.
    """

    def __init__(self, inspection, matrix_list, word):
        self.inspection = inspection
        self.matrix = matrix_list
        self.word = word
        self.candidates = []

    def replacer(self, matrix_item):
        """
        using an array of integers, starting from the end of the word,
        replace the duplicated letter group in the word with a new
        quantity of letters taken from the matrix_item array.

        """
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
        """
        calls replacer on each array in the matrix. 
        """
        for matrix_item in self.matrix:
            self.word_element = self.word[:]    
            self.replacer(matrix_item)

        return self.candidates


class Voweller(object):
    """
    Like Inspector but specific to Vowels. Checks the existence of all unique vowels
    in word_candidate. Returns a list of dicts; the dict key is the vowel and the
    dict value is the index in which it occurs in the word.
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
        # return [re.compile("%s{1,}" % x) for x in self.the_vowels()]
        # previous line did not return beat from buuut
        return [re.compile("%s" % x) for x in self.the_vowels()]
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
        
    def call_start(self, _list):
        for i in _list:
            self._start(i)
        return None
    
    def inspect(self):
        self.call_start(self.vowel_list())
        self.sorted = sorted(self.resultlist, key=lambda d: d[d.keys()[0]], reverse=True)
        return self.sorted

    def seeder(self):
        """
        returns a list of the integer 5 for each unique vowel
        """
        return [5 for i in self.resultlist]
        

class VowelCandidater(object):
    """
    compares every permutation of vowel combination with each vowel 
    in a word.

    accepts a list of dictionaries that are the vowel and
    the index in the word in which it occurs, a matrix of permutations,
    and the word that it is testing.

    returns permuations of the word based on the matrix_list and inspection dictionary
    """

    def __init__(self, inspection_dict, matrix_list, word):
        self.inspection = inspection_dict
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

    M = Matrixer(matrix_seed)
    matrix = M.solve()
    
    C = Candidater(inspection, matrix, _word)
    candidates = C.check_candidate()
    
    if matrix == [[]]:
        
        V = Voweller(_word)
        vowel_inspection =  V.inspect()
        VM = Matrixer(V.seeder())
        vowel_matrix = VM.solve()
        
        VC = VowelCandidater(vowel_inspection, vowel_matrix, _word)
        candidates = VC.check_candidate()

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
            
            VC = VowelCandidater(vowel_inspection, vowel_matrix, candidate)
            candidates = VC.check_candidate()
            for word_candidate in candidates:
                if check(word_candidate) and check(word_candidate) not in actual_words:
                    actual_words.append(check(word_candidate))
        return actual_words


def select_random(_list):
    """
    return a random item from the list passed in
    as an argument.
    """
    selector = random.randint(0, len(_list) - 1)
    return _list[selector]

def prompt():
    """
    prompt for a word and run spell_checker function on the word,
    if the word is not immediately found in the word corpus
    """
    _input = raw_input('> ')
    if check(_input) == False:
        these_words = spell_checker(_input.lower())
        # print these_words
        if these_words == []:
            return 'NO SUGGESTION'
        
        elif len(these_words) == 1:
            return these_words[0]
        else:
            return select_random(these_words)
    else:
        # user entered a word from the corpus;
        # return the word from the corpus.
        return check(_input)


while True:
    print prompt()
