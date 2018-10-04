import xml.sax
import processing
import time
from collections import defaultdict


class AContentHandler(xml.sax.ContentHandler):
    final_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    page_threshold = 10000
    term_dict = {}
    title_id_dict = {}
    idflag = 0
    page_count = 0
    file_count = 0
    present_tag = ""
    title = ""
    id = ""
    text = ""

    def __init__(self):
        xml.sax.ContentHandler.__init__(self)

    def startElement(self, name, attrs):
        self.present_tag = name
        if name == "page":
            self.idflag = 1
            self.text = ""  # the text string is to be made empty every time a new page is encountered
            self.title = ""  # the title string is also to be made empty as otherwise, it was appending null string

    def characters(self, content):
        if self.present_tag == "title":
            self.title += content
        elif self.present_tag == "id" and self.idflag == 1:
            self.id = content
        elif self.present_tag == "text":
            self.text += content  # we just append in the text string and not others bcoz it breaks after reading the first '\n' character

    def endElement(self, name):
        if self.present_tag == "id" and self.idflag == 1:
            self.idflag = 0  # reset the flag for id as 0 so that the id of new page can be recognized
        elif self.present_tag == "text":
            self.title_id_dict[self.id] = self.title
            # keep on appending term-ids in final_dict till we read 1000 pages
            if(self.page_count <= self.page_threshold):
                self.page_count = self.page_count + 1
                processing.page_info(self.title, self.id, self.text, self.final_dict, self.term_dict)

            # as soon as we read page threshold(or 1000th page in this case), write the present final_dict to the file
            # and increment the file_count and also set the page_count again to 0
            else:
                write_to_file(self.final_dict, self.file_count)
                print('File', self.file_count, ' Done')
                self.final_dict.clear()
                self.file_count = self.file_count + 1
                self.page_count = 0
                print(self.file_count)


    def write_final_dict_to_file(self):
        """
        for the last few pages which are less than 10000 and are left to be written onto the file because the
        page_count has not yet reached 1000, write them to the file based on the condition when we encounter the
        last tag of the corpus, i.e, mediawiki tag.
        :return: NONE
        """
        write_to_file(self.final_dict, self.file_count)

    def write_term_dict_to_file(self):
        """
        this function maps the unique words in the whole corpus to term-ids and writes this info to a file
        :param term_dict:
        :return:
        """
        with open('/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/TermDict/term_map.txt', 'w') as term_id_file:
            for term, term_id in self.term_dict.items():
                term_id_file.write(term + ':' + str(term_id) + '\n')
                term_id_file.flush()

    def write_title_id_map_to_file(self):
        """
        this function maps the id of a page to its title and writes this info to a file
        :return:
        """
        with open('/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/Title_id_map/title_map.txt', 'w', encoding='utf-8') as title_file:
            for id, title in self.title_id_dict.items():
                title_file.write(id + ':' + title.strip() + '\n')
                title_file.flush()


def main(sourceFileName):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = AContentHandler()
    parser.setContentHandler(Handler)
    parser.parse(sourceFileName)
    Handler.write_final_dict_to_file()
    Handler.write_term_dict_to_file()
    Handler.write_title_id_map_to_file()



def write_to_file(final_dict, file_count):
    """
    this function takes the final_dict which contains inverted index for every 10000 pages and dumps that final_dict
    into a separate file based on the value of file_name which is a string which gives us the particular file no. onto
    which the contents of final_dict are to be written. Also, the dictionary is written in sorted order which means that
    terms with the minimum term-id are written first and so on.
    :param final_dict: the inverted index dictionary for every 1000 pages
    :param file_count: the particular file index onto which contents are to be written
    :return: NONE
    """
    root_path = '/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/IndexFiles/'
    file_name = root_path + 'file' + str(file_count) + '.txt'
    with open(file_name, 'w') as file:
        for word, page_map in sorted(final_dict.items()):
            file.write(str(word) + ':')
            for page_id, freq_map in page_map.items():
                counts = 0
                file.write(str(page_id))
                for category, freq in freq_map.items():
                    counts = counts + freq
                    file.write(str(category) + str(freq))
                file.write(',' + str(counts))
                file.write('|')
            file.write('\n')
            file.flush()


if __name__ == "__main__":
    start = time.time()
    #main("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase1/temp.xml")
    #main("/Users/rishabhmurarka/Desktop/3rd SEm/20172111_phase1/wiki-search-small.xml")
    main("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase1/wiki-search-small.xml")
    #main("/Volumes/Seagate Backup Plus Drive/wiki-62gb/wiki-search-small.xml")
    print("time ", time.time() - start)