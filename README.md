# Wikipedia-Search-Engine
Constructed an Inverted Index for a Wikipedia dump of around 60gb that would serve for the retrieval of documents related to the search query with an average retrieval time of around 1 sec per query
The link to the dataset can be found here : ftp://10.4.17.131/Datasets/IRE_Monsoon_2017/WikiSearch/

## CODE FILES:

1. **parsing.py** - File containing all functions related to XML parsing.
2. **processing.py** - File containing function which takes as input title, id and content of a wiki page and preprocesses it.
3. **indexing.py** -  File which performs the actual indexing and secondary level and offset files.
4. **search.py** - Main file containing all the code for query processing and retrieval of results

## Execution of Code
### Prerequisits - 
#### Required Directories
1. **IndexFiles** - Initial index gets created here 
2. **Secondary_index_files** - The secondary level indexed files are stored here term_id wise
3. **Offset_files** - Offset files for these secondary_index files are made here
4. **TermDict** - Pickle file containing the term-term_id map is made here
5. **Title_id_map** - File containing page_id-title map is made here

#### Required Files
1. **full_wiki.xml** - The XML file containing the full data of wikipedia

### Execution -  
Run **Search.py** - An infinite loop runs expecting queries that ends with the exit command.

### Types of Queries - 
1. **Field query** - Assuming that fields are small letters(b, i, c, t, r, e) followed by colon and the fields are space separated.
“b:sachin i:2003 c:sports”

2. **Boolean query** - Assuming that the boolean operators are given in capitals (AND, OR, NOT) and remaining words are space separated.
“Sachin AND Dhoni NOT Sehwag” 

3. **Normal query** - Any sequence of words that doesn’t satisfy the above conditions is considered a normal query.
    “Virat Kohli”
    
##Performance -

###For Queries of -

less than 3 words, time to fetch results is < 1s
between 3 and 7 words, time to fetch results is Around 2-3s
