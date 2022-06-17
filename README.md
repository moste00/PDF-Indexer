# PDF-Indexer
A python script to scrape a pdf file and create a word index out of it.

A [word index](https://en.wikipedia.org/wiki/Index_(publishing)#Purpose) is a sorted list of words in a document, where each word is tagged by the all the page numbers it appears in. For example, in a book about cats, an index might look like this 

Cute: 1,2,5,7

Eyes: 3,4,5

Paws: 2,3,4

Whiskers: 5,6,7

The numbers that follow each word is all the page numbers where the word appeared. This helps you find a word quickly.

## How To Use

Use any python installation with the library [pdfplumber](https://github.com/jsvine/pdfplumber) installed. You can do it with 

    pip install pdfplumber
    
as usual.

Invoke the script as follows

    python indexer.py PDF="PATH\TO\PDF\FILE\INCLUDING\EXTENTSION.pdf" IDX="PATH\TO\OUTPUT\FILE\INCLUDING\EXTENSION.txt"

You can also remove the string double quotations if the file paths have no spaces in it. The IDX file can have any 3 letter extension.

## Page Groups

If the PDF file is too large for the resulting index to be useful, you can split it into several sub-indices using page groups. A page group is any set of pages you are interested in. For example, suppose you are indexing a large file representing a collection of lectures and you're only interested in lecture 1, the first 10 pages. 

You can invoke the script like this

    python indexer.py PDF="PATH\TO\PDF\FILE\INCLUDING\EXTENTSION.pdf" IDX="PATH\TO\OUTPUT\FILE\INCLUDING\EXTENSION.txt" #Lecture1=1..10
    
This invocation will, in addition to creating the overall index specified by IDX, also create a sub-index of only the the first 10 pages, in a file named Lecture1.txt. And thus you have only the words of Lecture 1 indexed.

The page group name minus the leading '#' is the path to its output file. If no extension is found the DEFAULT_EXTENSION from config.py will be used.

## Customizing The Output Format
The way format customization works is that the script calls callback functions in config.py before or after key events in the printing process, and the return objects are printed to the output file.

For example, suppose we want to print in the json format. First we need to invoke the script like this

    python indexer.py PDF="PATH\TO\PDF\FILE\INCLUDING\EXTENTSION.pdf" IDX="PATH\TO\OUTPUT\FILE\INCLUDING\EXTENSION.txt" #Lecture1.json=1..10

But that is not enough, the file config.py must also contain the following function defintions 

    def before_writing_begins(total_num_words):
        return "{\n"
    def before_writing_word(num_words_written_so_far):
        if num_words_written_so_far == 0: return '"'
        return ',"'
    def after_writing_word(num_words_written_so_far):
        return '":['
    def before_writing_pagenum(page_numbers_written_so_far, total_page_numbers):
        return ""
    def after_writing_pagenum(page_numbers_written_so_far, total_page_numbers):
        if page_numbers_written_so_far == total_page_numbers: return "]\n"
        return ","
    def after_writing_ends():
        return "}"
        
    The first function is called at the very beginning during printing, before anything has been printed. It returns the starting curly brace in the json file. 
    
    The second function is called everytime any word is printed, before printing. It checks if this is the first word, and if so, only returns a string quotation, and otherwise returns a seperating comma before the string quotation. 
    
    The third function terminates the json string containing the word and starts the json array where the page numbers will be written. 
    
    The fourth function is a no-op because we don't need to do anything beofer writing a page number. 
    
    The fifth function, called after every page number is printed, normally prints the seperating comma in the json array containing the page numbers but when the         array is finished it terminates it and starts a new line. 
    
    The final function is called after the printing process is done and terminates the root json object. 
    
    This is what the output files might look like  
    {
        "word1":[1]
        ,"word2":[2,3]
        ,"word3":[3,4]
    }
    
    Therefore, those 6 callback functions in config.py allow the user to customize the output format in an extremely general way. 
## Efficiency

The script is somewhat a sloth. It takes about a minute to index a pdf file of about 500 pages on an intel core i7 4th gen dual 2.9 GHz core machine with 8GB RAM and an HDD, running a Windows 8.1 instance. 

I think there is no realistic way to improve it as most of the time appears to be spent in the pdfplumber code. But I will try.  
