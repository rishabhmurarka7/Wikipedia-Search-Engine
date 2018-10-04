import os
from contextlib import ExitStack
import heapq

#root_path1 = "/Volumes/Seagate Backup Plus Drive/wiki-62gb/Phase_2/IndexFiles/"
root_path1 = "/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/"
root_path = "/Users/rishabhmurarka/Desktop/3rd SEm/IRE/Phase_2/"

index_files_path = 'IndexFiles'
file_list = []
for f in os.listdir(root_path1 + index_files_path):
        if not f.startswith('.'):
            file_list.append(root_path1 + index_files_path + '/' + f)

li = []
with ExitStack() as stack:
    files = [stack.enter_context(open(file)) for file in file_list]
    #cur_lines = [file.readline() for file in files]
    for file in files:
        temp = file.readline().split(':')
        li.append([int(temp[0]), temp[1][:-1], file])

    # in the heap structure, every element is a list of three elements where the first element is the term-id
    # and the second element is the posting list corresponding to that term-id
    # and the third element is the file pointer
    heapq.heapify(li)
    prev_minimum = -1
    file_count = 0
    term_count = 0
    f = open(root_path + 'Secondary_index_files/' + str(file_count) + '.txt', 'w')
    x=0
    while li:
        x = x+1 #this variable helps to omit the newline character in the starting of every file
        min_heap_element = heapq.heappop(li)
        new_file_line = min_heap_element[2].readline()

        # this condition checks if we have reached the end of the file and if so, then don't push anything to heapq
        # new_file_pointer is the next line of the min_heap_element file
        if new_file_line:
            temp = new_file_line.split(':')
            heapq.heappush(li, [int(temp[0]), temp[1][:-1], min_heap_element[2]])
        new_minimum = int(min_heap_element[0])
        if new_minimum == prev_minimum:
            f.write(min_heap_element[1])
        else:
            #if a new term-id is encountered,
            #if x > 1:
                # append a newline character after every time a new term-id is encountered except for the first case
                #f.write('\n')
            if (term_count != 0):
                f.write('\n')
            f.write(str(min_heap_element[0]) + ':' + min_heap_element[1])
            prev_minimum = new_minimum
            term_count = term_count + 1
        if term_count == 100000:
            f.close()
            file_count = file_count + 1
            f = open(root_path + 'Secondary_index_files/' + str(file_count) + '.txt', 'w')
            term_count = 0
    f.close()

print("Big 15gb out.txt file created")

#this function is now redundant as secondary index files are now created in the upper part of code only after modification in the code
def create_secondary_index_files():
    """
    This function creates the secondary index files for the big 20gb inverted_index file(out.txt) on the threshold value
    after encountering every 1 lakh terms from the sorted out.txt file and then creating a new offset file for
    the next 1 lakh words and so on till all the terms are not covered.
    :return:
    """
    file_count = 0
    term_count = 0
    with open(root_path + 'out.txt', 'r') as output_file:
        line = output_file.readline()
        f = open(root_path + 'Secondary_index_files/' + str(file_count) + '.txt', 'w')
        while line:
            if term_count != 100000:
                term_count = term_count + 1
            else:
                f.close()
                file_count = file_count + 1
                f =  open(root_path + 'Secondary_index_files/'  + str(file_count) + '.txt', 'w')
                term_count = 1

            f.write(line)
            line = output_file.readline()
        f.close()

def create_offset_files_for_secondary_index_files():
    """
    this function will create one offset file per each of the secondary level index files. This function reads the secondary
    index files and creates an offset file for each of the secondary index file and returns the
    file number into which we have to look upon in order to search for the given term.
    :return: line returns the file no. which we have to open to find the postings list for a particular term id
    """

    file_list = []
    for f in os.listdir(root_path + 'Secondary_index_files'):
        if not f.startswith('.'):
            file_list.append(f)

    for file in file_list:
        with open(root_path + 'Secondary_index_files/' + file , 'r') as index_file:
            with open(root_path + 'Offset_files/' + 'offset' + str(file), 'w') as offset_file:
                pos = index_file.tell()
                line = index_file.readline()
                while line:
                    term = line.split(':')
                    offset_file.write(term[0] + ':' + str(pos) + '\n')
                    pos = index_file.tell()
                    line = index_file.readline()


def write_sorted_termids_to_file():
    """
    this function will sort the term-termids and write them to file
    :return:
    """
    with open("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase_2/TermDict/term_map.txt") as fin:
        content = sorted(fin)

    with open("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase_2/TermDict/term_map.txt", "w") as fout:
        fout.writelines(content)


def create_primary_term_files():
    """
    this function will take the term-termid file where the mapping of all the terms and their term-ids are stored
    in ascending order and then create small files of 2-2 MB and tore them in a separate folder named as :
    "Secondary_term_files".
    :return:
    """
    file_count = 0
    with open(root_path + 'TermDict/' + 'term_map.txt', 'r') as output_file:
        line = output_file.readline()
        f = open(root_path + 'Secondary_term_files/' + str(file_count) + '.txt', 'w')
        file_name = root_path + 'Secondary_term_files/' + str(file_count) + '.txt'
        while line:
            if os.stat(file_name).st_size < 2000000:
                pass
            else:
                f.close()
                file_count = file_count + 1
                file_name = root_path + 'Secondary_term_files/' + str(file_count) + '.txt'
                f = open(root_path + 'Secondary_term_files/' + str(file_count) + '.txt', 'w')

            f.write(line)
            f.flush()
            line = output_file.readline()
        f.close()

def create_secondary_term_files():
    """
    this function will read all the files in the folder "Secondary_term_files" and create a secondary index for all
    those files and store the first term of each file and its corresponding file name(the file whose first
    term is picked) in a separate file called "term_offset.txt"
    :return:
    """
    file_list = []
    for f in os.listdir(root_path + 'Secondary_term_files'):
        if not f.startswith('.'):
            file_list.append(f)

    with open(root_path + 'term_offset.txt', 'w') as offset_file:
        for file in file_list:
            term_file = open(root_path + 'Secondary_term_files/' + file, 'r')
            file_name = root_path + 'Secondary_term_files/' + file
            line = term_file.readline()
            term = line.split(':')[0]
            offset_file.write(term + ':' + file_name + '\n')
            term_file.close()

def write_sorted_termids_to_file():
    """
    this fucntion will simply sort the file "term_offset.txt".
    Since the command os.listdir does not take the files stored in a folder sequentially but rather in a random order,
    hence we will sort the file term_offset.txt
    :return:
    """
    with open("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase_2/term_offset.txt") as fin:
        content = sorted(fin)

    with open("/Users/rishabhmurarka/PycharmProjects/Wiki/Phase_2/term_offset.txt", "w") as fout:
        fout.writelines(content)





#create_primary_term_files()
#create_secondary_term_files()
#write_sorted_termids_to_file()
#create_secondary_index_files()
create_offset_files_for_secondary_index_files()
#write_sorted_termids_to_file()