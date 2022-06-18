# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 00:34:03 2022

@author: Mostafa
"""
import re

from config import DEFAULT_EXTENSION

#A Page Group is a name given to a bunch of pages
#It's an interface with a single method 
#contains(page_number : Int) : Bool 
#That returns whether the page number belongs to the page
class PageGroup:
    def __init__(self,name):
        self.name = name
    
class RangePageGroup(PageGroup):
    def __init__(self,name,start_page_number,end_page_number):
        self.start = start_page_number
        self.end = end_page_number
        PageGroup.__init__(self, name)
    
    def contains(self,page_number):
        return page_number >= self.start and page_number <= self.end

class SetPageGroup(PageGroup):
    def __init__(self,name,page_numbers):
        self.page_numbers = page_numbers
        PageGroup.__init__(self, name)
    
    def contains(self,page_number):
        return page_number in self.page_numbers
    
ALPHA_NUMERIC = "[_a-zA-Z0-9]+"
NUMBER = "[0-9]+"
RANGE = NUMBER +"\.\."+ NUMBER
OPTIONAL_EXTENSION =  "(\."+ ALPHA_NUMERIC +")?" 
COMMA_SEPERATED_LIST_OF_NUMBERS = NUMBER +"(,"+ NUMBER +")*"

class CmdArgsParser:
    
    def __init__(self,cmd_string):
        self.parsing_errors = []
        
        #Try parsing the pdf path 
        try:
            self.pdf_file_path = re.search("PDF=.+\.pdf",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No PDF File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.pdf")
        #Try parsing the index file path
        try:
            self.index_file_path = re.search("IDX=[^.]+\."+ALPHA_NUMERIC,cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No Index File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.ext")
        
        self.groups = []
        #Try parsing ranged page groups
        ranged_groups = re.finditer(''.join([
                                            "#"    ,      #A literal '#', the ranged group start marker
                                            "[^.=]+",      #Then any sequence of characters that doesn't contain a dot or an equal, then an
                                            OPTIONAL_EXTENSION,
                                            "="    ,      #Then a literal '='
                                            RANGE         #Then the range, a pair of numbers seperated by a '..'
                                        ]),
                                   cmd_string)
        for match in ranged_groups:
            group = match.group()
            group_fields = group.split("=")
            group_name = group_fields[0][1:]
            group_range = group_fields[1].split("..")
                
            #Sort group start and group end 
            min_num,max_num = int(group_range[0]),int(group_range[1])
            if min_num > max_num:
                min_num,max_num = max_num,min_num
                
            #Insert default extension if group name has no extension
            if group_name.rfind(".") == -1:
                group_name = group_name + DEFAULT_EXTENSION
                    
            self.groups.append(RangePageGroup(group_name, min_num, max_num))
        
        #Try parsing set page groups
        set_groups = re.finditer(''.join([
                                        "@"    , #A literal '@', the set group start marker
                                        "[^.=]+", #Then any sequence of characters that doesn't contain a dot or an equal, then an
                                        OPTIONAL_EXTENSION,
                                        "="    , #Then a literal '=', then a 
                                        COMMA_SEPERATED_LIST_OF_NUMBERS
                                    ]),
                                    cmd_string)
        for match in set_groups:
            group = match.group()
            group_fields = group.split("=")
            group_name = group_fields[0][1:]
            group_numbers = group_fields[1].split(",")
            
            if group_name.rfind(".") == -1:
                group_name = group_name + DEFAULT_EXTENSION
            
            self.groups.append(SetPageGroup(group_name, {int(i) for i in group_numbers}))