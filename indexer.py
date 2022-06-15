# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 14:35:41 2022

@author: Mostafa
"""

import pdfplumber
import re
import sys

from ignored_words import IRRELEVANT_WORDS 

class CmdArgsParser:
    
    def __init__(self,cmd_string):
        self.parsing_errors = []
        
        #Try parsing the pdf path 
        try:
            self.pdf_file_path = re.search("PDF=.+\.pdf",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No PDF File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.pdf")
        #Try finding the index text file path
        try:
            self.index_file_path = re.search("TXT=.+\.txt",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No text File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.txt")
def get_relevant_words(string):
    all_words = re.findall(r"[a-zA-Z]{2,}",string)
    
    return {word.lower() for word in all_words 
                         if not word.lower() in IRRELEVANT_WORDS}

###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
#                                                       MAIN
###################################################################################################################
###################################################################################################################
################################################################################################################### 
###################################################################################################################
args = CmdArgsParser(' '.join(sys.argv))
if args.parsing_errors:
    for error in args.parsing_errors:
        print("Parse Error! \n"+error)
else:
    #This is a Dictionary<String, Set<Integer>> that will map each relevant word to the set of pages where it appears         
    index = {}
    
    with pdfplumber.open(args.pdf_file_path) as pdf_file:
        for idx,page in enumerate(pdf_file.pages):
            text = page.extract_text()
            words = get_relevant_words(text)
            
            for word in words:
                #If word was encountered before
                if word in index:
                    #Add current page number to the set of page numbers where the word appears
                    index[word].add(idx+1)
                #If this is a new word
                else:
                    #add it to the index with the current page number as the only page (yet) where it appears  
                    index[word] = {idx+1}
    
    with open(args.index_file_path,"w") as index_file:
        for word in sorted(index):
            index_file.write(word)
            index_file.write(":\n")
            
            for page_num in index[word]:
                index_file.write(str(page_num)+",")
                
            index_file.write("\n")