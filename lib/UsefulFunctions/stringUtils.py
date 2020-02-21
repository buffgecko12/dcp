def normalize_field(mystring):
    return mystring.replace(" ","").lower()

def mychr(string):
    mystring = ""
    
    if(string == "a"):
        mystring = chr(225)
    elif(string =="e"):
        mystring = chr(233)
    elif(string =="i"):
        mystring = chr(237)
    elif(string =="o"):
        mystring = chr(243)
    elif(string =="u"):
        mystring = chr(250)
    elif(string =="n"):
        mystring = chr(241)
    elif(string =="!"):
        mystring = chr(161)
    elif(string =="?"):
        mystring = chr(191)
        
    return mystring