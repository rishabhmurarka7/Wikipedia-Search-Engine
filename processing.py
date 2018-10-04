import re
from nltk.corpus import stopwords
from Stemmer import Stemmer

stop_words = set(stopwords.words('english'))
words_to_exclude = ['infobox', 'category', 'redirect', 'large', 'help', 'look','camelcase', 'r',
                    '``','==', 'pp-move-indef', 'reflist', '/ref', "''",'reflistcolwidth=30em', 'include','write',
                        '/', '/small', '&lt', '&gt', '&amp', '&nbsp', 'nowiki', 'cite', 'colwidth', 'infobox',
                        'source', 'hiero', 'div', 'font', 'span', 'strong', 'strike', 'blockquote','new','author',
                        'tt', 'var', 'sup', 'sub', 'big', 'small', 'center', 'h1', 'h2', 'h3', 'em', 'page',
                    'links', 'external', 'references']

ps = Stemmer('porter')


def page_info(title, id, text, final_dict, term_dict):

    title_list = preprocessing(title, term_dict) #titlelist will contain the titles for every page in list format one at a time
    merge_dict(id, title_list, "t", final_dict)
    divideText(text, id, final_dict, term_dict)


def divideText(textbody, id , final_dict, term_dict):
    """
    this function just deals with the text and breaking it into 4 categories ; namely
    References, External Links, Category and Infobox
    :param textbody: the whole text for a given page
    :param id: the id for a given page
    :return: NONE
    """
    references = ""
    external_links = ""
    category = ""
    infobox = ""

    # the text body contains images in File format or some extra content like additional info in the form of
    # tables or {{cite which is of no use(except for in references) and can be removed from the text without losing any useful information
    regex_to_remove_all = re.compile(r"\[\[[Ff]?ile(.*?)\]\]|{\|(.*?)\|}|{{[Vv]?[Cc]ite(.*?)}}|\<(.*?)\>|={3,}",
                                     flags=re.DOTALL)
    textbody = re.sub(regex_to_remove_all, ' ', textbody)

    # in the m.group(0) , it is matching the whole regex and giving it as output whereas in m.group(1)
    # it is giving only the part that is matching inside the brackets
    # for separating the references data from the text data
    m = re.search('== ?References ?==(.*)==', textbody, flags=re.DOTALL)
    if m:
        references = references + m.group(1)
        temp = textbody.split(m.group(1))
        textbody = " ".join(temp)
        references_list = preprocessing(references, term_dict)
        merge_dict(id, references_list, "r", final_dict)


    # for separating the External Links data from the text data
    # also, all the part after the external links can be omitted as there is nothing after the external links
    # that contributes towards the body of the text
    m = re.search('== ?External links ?==(.+?)\[\[Category', textbody, flags = re.DOTALL)
    if m:
        external_links = external_links + m.group(1)
        temp = textbody.split(m.group(1))
        textbody = " ".join(temp)
        external_list = preprocessing(external_links, term_dict)
        merge_dict(id, external_list, "e", final_dict)

    # for separating the Category data from the text data
    m = re.findall('\[\[Category:(.*)\]\]', textbody, flags=re.DOTALL)
    if len(m) > 0:
        for i in m:
            category = category + i
            category_list = preprocessing(category, term_dict)
            merge_dict(id, category_list, "c", final_dict)
        textbody = re.sub('\[\[Category(.+?)\]\]', ' ', textbody, flags=re.DOTALL)

    # for separating the Infobox data from the text data
    m = re.findall('{{Infobox(.+?)}}', textbody, flags= re.DOTALL)
    if len(m) > 0:
        for i in m:
            infobox = infobox + i
            infobox_list = preprocessing(infobox, term_dict)
            merge_dict(id, infobox_list, "i", final_dict)
        textbody = re.sub('{{Infobox(.+?)}}', ' ', textbody, flags=re.DOTALL)

    textbody_list = preprocessing(textbody, term_dict)
    merge_dict(id, textbody_list, "b", final_dict)


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

def preprocessing(unprocessed_data, term_dict):
    """
    for pre-processing the words present in a document(which includes tokenization, stop words
    removal, stemming and converting to lower case)
    :param unprocessed_data: the string on which processing is to be performed
    :return: a list of tokenized words for the given string
    """

    filtered_sentence = []
    punc_list = str.maketrans(' ', ' ', '!"\'()*+,;<>[\\]^`{|}~#?:&_%')
    tokens = unprocessed_data.lower().translate(punc_list).split()
    for w in tokens:
        if w not in stop_words and w not in words_to_exclude and isASCII(w) and len(w) > 2:
            if ps.stemWord(w) not in term_dict:
                term_dict[ps.stemWord(w)] = len(term_dict)

            #if i write filtered_sentence.append(ps.stemWord(w)), then I will have word:posting_list instead of
            #word_id:posting_list in the index files
            filtered_sentence.append(term_dict[ps.stemWord(w)])

    return filtered_sentence


def merge_dict(id, intermediate_list, st, final_dict):
    """
    this merge_dict will be a dictionary of dictionary of dictionary where key will be a word and value will be a dictionary
    and in the second dictionary, key will be the id and value will again be a dictionary where key represents the
    category or field to which that particular word belongs to and value refers to the count of that word of in that
    particular category or field.
    :param id: the id of the current page
    :param intermediate_list: the list of tokenized words which are to be inserted into the dict
    :param st: the catergory to which that particular word belongs
    :return: NONE
    """

    for k in intermediate_list:
        final_dict[k][id][st] += 1