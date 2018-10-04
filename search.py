import re
import time
import math
import operator
from nltk.corpus import stopwords
import os
import pickle
from Stemmer import Stemmer
stop_words = set(stopwords.words('english'))
ps = Stemmer('porter')


root_path = "/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/"


def isASCII(word):
    """
    removing non-ascii charcaters from a string. If the word is a ascii character,
    then only include it into the list or dictionary or even file
    :param word: the string which is to be checked for non-ascii presence
    :return: True if the word is an ascii character ; otherwise false
    """
    try:
        word = word.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True

def preprocessing(unprocessed_data):
    """
    for pre-processing the words present in a query(which includes tokenization, stop words
    removal, stemming and converting to lower case)
    :param unprocessed_data: the string on which processing is to be performed
    :return: a list of tokenized words for the given string
    """

    filtered_sentence = []
    punc_list = str.maketrans(' ', ' ', '!"\'()*+,;<>[\\]^`{|}~#?:&_%')
    tokens = unprocessed_data.lower().translate(punc_list).split()
    for w in tokens:
        if w not in stop_words and isASCII(w) and len(w) > 2:
            filtered_sentence.append(ps.stemWord(w))

    return filtered_sentence

def read_offset_file(term_id , file_no):
    """
    this function will take as input the term-id which in turn will tell the offset file number to be read
    and find the line at which we have to perform the seek operation
    in order to find the postings list for a particular term-id
    :return: line which needs to be searched in the corresponding secondary_index_file for the posting list
    """
    if 'offset' + str(file_no) + '.txt' in os.listdir(root_path + 'Offset_files/'):
        with open(root_path + 'Offset_files/' + 'offset' + str(file_no) + '.txt', 'r') as f:
            '''
            line = f.readline()
            while line:
                temp = line.split(':')
                if term_id == temp[0]:
                    return temp[1]
            '''

            lines = f.readlines()
            for line in lines:
                if str(term_id) == line.split(':')[0]:
                    return line.split(':')[1]
    else:
        return "12f1b1|2887261f1e1|18767752f1b1|"


def read_secondary_index_files(file_no, pos):
    """
    this function will read the secondary index file from the position returned by read_offset_file function
    and return the postings list for a particular term-id
    :return: the posting list for the term-id provided in the argument of this function
    """

    with open(root_path + 'Secondary_index_files/' + str(file_no) + '.txt', 'r') as f:
        f.seek(int(pos), 0)
        line = f.readline()
        temp = line.split(':')
        return temp[1]

def find_tfidf(posting_list):
    """
    this function returns the list of all the [docids, tf-idf] values which contain that particular term
    :param posting_list: this is the posting list for a particular term with details of all the documents which
    contain that particular term
    :return:
    """
    total_documents = 17640866 #570861
    posting_lists_without_frequencies = []
    tf_idf_values = []
    doc_ids = []

    #basically, if the posting list is empty, then just return an empty string
    if len(posting_list) == 0:
        return tf_idf_values

    if '|' not in posting_list:
        posting_list_for_docids = ([posting_list])
    else:
        posting_list_for_docids = posting_list.split('|')[:-1]

    idf_value = math.log(total_documents/len(posting_list_for_docids))
    #if the categories are not to be assigned any weights while finding results to a search query, then follow below code
    '''
    for i in posting_list_for_docids:
        temp = i.split(',')
        posting_lists_without_frequencies.append(temp[0])
        tf_idf_values.append(float(temp[1]) * idf_value)

    for i in posting_lists_without_frequencies:
        doc_ids.append(re.split("[a-z]", i)[0])
    '''

    #the following lines of code in this function gives importance to where a word from the search query appears in
    #document, like if a word appears in the title of the document then, it will be given utmost importance in the search
    # results and so on..
    for i in posting_list_for_docids:
        if 't' in i:
            temp = re.split("[a-z]", i)
            doc_ids.append(temp[0])
            tf_idf_values.append(float(temp[1]) * idf_value * 50)
        elif 'b' in i:
            temp = re.split("[a-z]", i)
            doc_ids.append(temp[0])
            tf_idf_values.append(float(temp[1]) * idf_value * 25)
        elif 'c' in i:
            temp = re.split("[a-z]", i)
            doc_ids.append(temp[0])
            tf_idf_values.append(float(temp[1]) * idf_value * 10)
        elif 'i' in i:
            temp = re.split("[a-z]", i)
            doc_ids.append(temp[0])
            tf_idf_values.append(float(temp[1]) * idf_value * 5)
        else:
            temp = re.split("[a-z]", i)
            doc_ids.append(temp[0])
            tf_idf_values.append(float(temp[1]) * idf_value)



    doc_id_and_frequency_map = dict(zip(doc_ids, tf_idf_values))

    #sorting the doc_id_and_frequency_map on the basis of value of this dict or tf_idf_values
    doc_id_and_frequency_map = sorted(doc_id_and_frequency_map.items(), key=operator.itemgetter(1), reverse = True)
    return doc_id_and_frequency_map

    # doc_id_and_frequency_map = dict(doc_id_and_frequency_map)
    # find_actual_results(doc_id_and_frequency_map)

def find_actual_results(doc_id_and_frequency_list, page_title_map):
    # with open(root_path + 'Title_id_map/' + 'title_map.txt', 'r', encoding='utf-8') as f:
    #     lines = f.readlines()
    #     lines = [line.split(":", 1) for line in lines]
    #     page_title_map = dict(lines)
    results = []
    for i in doc_id_and_frequency_list:
        try:
            results.append(page_title_map[i[0].strip()].strip())
        except KeyError:
            continue
    return results


def find_term_id(processed_query_list, term_and_term_id_map):
    """
    this function just finds the term-id for each of the words in the list passed in its argument
    :param processed_query_list: list of tokens or tokenized words
    :return: list of term-ids corresponding to each of the tokenized word in the argument
    """
    term_id_lists = []
    # with open(root_path + 'TermDict/term_map.txt', 'r') as f:
    #     lines = f.readlines()
    #     lines = [line.split(":", 1) for line in lines]
    #     term_and_term_id_map = dict(lines)

    for i in processed_query_list:
        try:
            term_id_lists.append(term_and_term_id_map[i])
        except KeyError:
            continue
    term_id = [term for term in term_id_lists]
    return term_id

def perform_or_operation(set1, set2):
    """
    performs the OR operation of given two lists
    :param set1:
    :param set2:
    :return:
    """
    union_set = set.union(set1, set2)
    return union_set

def perform_and_operation(set1, set2):
    """
    performs the AND operation of given two lists
    :param set1:
    :param set2:
    :return:
    """
    intersection_set = set.intersection(set1, set2)
    return intersection_set

def perform_not_operation(set1, set2):
    """
    performs the NOT operation of given two lists
    :param set1:
    :param set2:
    :return:
    """
    set_difference = set1.difference(set2)
    return set_difference

def find_posting_list(query, term_and_term_id_map):
    """
    this fuction takes as argument a tokenized word and returns the
    :return:
    """
    processed_query_list = preprocessing(query)
    term_id = find_term_id(processed_query_list, term_and_term_id_map)
    if not term_id:
        print("No documents match the given search query")
    term_id = term_id[0]
    file_no = int(int(term_id) / 100000)
    position = read_offset_file(term_id, file_no)
    posting_list = read_secondary_index_files(file_no, position)
    list_of_lists = find_tfidf(posting_list)

    return list_of_lists


if __name__ == "__main__":

    #loading the id-page map into the memory
    print("Loading Title map")
    with open(root_path + 'Title_id_map/' + 'title_map.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines = [line.split(":", 1) for line in lines] #here, 1 means it will split in the basis of first ':' character
        page_title_map = dict(lines)
    print("Done")
    '''
    # loading the term-termid map into the memory
    with open(root_path + 'TermDict/term_map.txt', 'r') as f:
        lines = f.readlines()
        lines = [line.split(":", 1) for line in lines]
        term_and_term_id_map = dict(lines)
    '''
    print("Loading Term Dict")
    with open(root_path + 'TermDict/' +  'term_mapping.pickle', 'rb') as handle:
        term_and_term_id_map = pickle.load(handle)
    print("Done")
    while True:

        query = input("Enter your query:")
        if ':' in query:
            query_type = "field"
        elif 'AND' in query or 'OR' in query or 'NOT' in  query:
            query_type = "boolean"
        elif query == "exit":
            query_type = "exit"
        else:
            query_type = "normal"

        print("Query type is:" + query_type)

        start = time.time()

        ############### PROCESSING THE NORMAL QUERY########################
        if query_type == "normal":
            #this is a list of list(of length 2 of term_id,tfidf value)
            list_of_lists = []
            ranking_list = []

            #this list will contain the set of docids of all the documents which contain the particular words in the query
            list_of_docids = []

            # this list will contain the dictionary of a tuple(doc_id,tfidf) for all the terms in the query
            list_of_dictionaries = []
            processed_query_list = preprocessing(query)

            #this list contains the term-ids corresponding to each of the tokenized word in the argument
            term_id_lists = find_term_id(processed_query_list, term_and_term_id_map)
            if not term_id_lists or len(term_id_lists) != len(processed_query_list):
                print("No documents match the given search query")
                continue

            for term in term_id_lists:
                file_no = int(int(term) / 100000)
                position = read_offset_file(term, file_no)
                posting_list = read_secondary_index_files(file_no, position)
                # list_of_lists is the list of all the [docids, tf-idf] values which contain that particular term
                list_of_lists = find_tfidf(posting_list)


                list_of_docids.append(set([i[0] for i in list_of_lists]))
                list_of_dictionaries.append(dict(list_of_lists))
            #set.intersection function takes as argument a list of sets
            intersection_set = set.intersection(*list_of_docids)

            for doc_id in list(intersection_set):
                total_tfidf_score = 0
                for dictionary in list_of_dictionaries:
                    total_tfidf_score += dictionary[doc_id]
                ranking_list.append((doc_id, total_tfidf_score))

            ranking_list = sorted(ranking_list, key=operator.itemgetter(1), reverse=True)
            results = find_actual_results(ranking_list[:10], page_title_map)
            for i, v in enumerate(results[:10]):
                print(i + 1, ". ", v)
            print("*********************************************************")

        ############### PROCESSING THE FILED QUERY########################
        elif query_type == "field":
            #this set will contain the final set of document titles which satisfy the given constraints
            results = []
            final_results = []

            list_of_final_dictionary = []
            final_ranking_list = []

            #this list will contain only the categories line 'b', 't' in sequence as they appear in the query
            query_categories = re.findall("([a-z]):", query)

            #this list will give all the words in the query along with the spaces and extra characters which need to be removed
            query_terms = re.split("[a-z]:", query)[1:]

            #this list will give all the words in the query with spaces removed from their ends in sequence
            query_terms = [i.strip()  for i in query_terms]

            for category, terms in list(zip(query_categories, query_terms)):
                new_posting_list = []
                # this is a list of list(of length 2 of term_id,tfidf value)
                list_of_lists = []
                ranking_list = []

                # this list will contain the set of docids of all the documents which contain the particular words in the query
                list_of_docids = []

                # this list will contain the dictionary of a tuple(doc_id,tfidf) for all the terms in the query
                list_of_dictionaries = []

                processed_query_list = preprocessing(terms)
                term_id_lists = find_term_id(processed_query_list, term_and_term_id_map)
                if not term_id_lists or len(term_id_lists) != len(processed_query_list):
                    print("No documents match the given search query")
                    continue
                for term in term_id_lists:
                    file_no = int(int(term) / 100000)
                    position = read_offset_file(term, file_no)
                    posting_list = read_secondary_index_files(file_no, position) #posting_list is of type string
                    posting_list_separated = posting_list.split("|")

                    #this new posting_list will only contain those docids information which contain that particular term
                    # in its docid
                    new_posting_list = [i for i in posting_list_separated if category in i]

                    new_posting_list = "|".join(new_posting_list)
                    list_of_lists = find_tfidf(new_posting_list)

                    list_of_docids.append(set([i[0] for i in list_of_lists]))
                    list_of_dictionaries.append(dict(list_of_lists))
                # set.intersection function takes as argument a list of sets
                intersection_set = set.intersection(*list_of_docids)

                for doc_id in list(intersection_set):
                    total_tfidf_score = 0
                    for dictionary in list_of_dictionaries:
                        total_tfidf_score += dictionary[doc_id]
                    ranking_list.append((doc_id, total_tfidf_score))

                ranking_list = sorted(ranking_list, key=operator.itemgetter(1), reverse=True)
                results.append(set([i[0] for i in ranking_list]))
                list_of_final_dictionary.append(dict(list_of_lists))
                #results.append(set(find_actual_results(ranking_list, page_title_map)))
            final_intersection_set = set.intersection(*results)

            for doc_id in list(final_intersection_set):
                total_tfidf_score = 0
                for dictionary in list_of_final_dictionary:
                    total_tfidf_score += dictionary[doc_id]
                final_ranking_list.append((doc_id, total_tfidf_score))

            final_ranking_list = sorted(final_ranking_list, key=operator.itemgetter(1), reverse=True)
            final_results.append(set(find_actual_results(final_ranking_list[:10], page_title_map)))
            final_intersection = set.intersection(*final_results)
            if not final_intersection:
                print("No documents match the given search query")
                continue
            #print(final_results)
            for i, v in enumerate(list(final_intersection)[:10]):
                print(i + 1, ". ", v)
            print("*********************************************************")

        ############### PROCESSING THE BOOLEAN QUERY########################
        elif query_type == "boolean":
            #list_of_dictionaries = []
            ranking_list = []

            query_operations = re.findall("AND|OR|NOT", query)
            query_terms = re.split("AND|OR|NOT", query)
            query_terms = [i.strip() for i in query_terms]
            # print(query_terms)
            # print(query_operations)

            result = query_terms[0]
            list_of_lists = find_posting_list(result, term_and_term_id_map)
            list_of_docids = set([i[0] for i in list_of_lists])
            list_of_dictionaries = dict(list_of_lists)
            for i in range(1, len(query_terms)):
                #finding the various parameters for the current word in the query
                list_of_lists_2 = find_posting_list(query_terms[i], term_and_term_id_map)
                list_of_docids_2 = set([i[0] for i in list_of_lists_2])
                for j in list_of_lists_2:
                    list_of_dictionaries[j[0]] = j[1]

                if query_operations[i-1] == 'AND':
                    resultant_set = perform_and_operation(list_of_docids, list_of_docids_2)
                elif query_operations[i-1] == 'OR':
                    resultant_set = perform_or_operation(list_of_docids, list_of_docids_2)
                elif query_operations[i-1] == 'NOT':
                    resultant_set = perform_not_operation(list_of_docids, list_of_docids_2)

                list_of_docids = resultant_set

            for doc_id in list(list_of_docids):
                total_tfidf_score = 0
                total_tfidf_score += int(list_of_dictionaries[doc_id])
                ranking_list.append((doc_id, total_tfidf_score))

            ranking_list = sorted(ranking_list, key=operator.itemgetter(1), reverse=True)
            results = find_actual_results(ranking_list[:10], page_title_map)
            for i, v in enumerate(results[:10]):
                print(i+1, ". ", v)
            print("*********************************************************")
        elif query_type == "exit":
            exit(0)

        print("Time to fetch the result of this query", time.time() - start)

