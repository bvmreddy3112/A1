import sys 
if len(sys.argv)<3:
    print("Usage: python analyze.py <logfile> <LEVEL> [top_n]")
    sys.exit(1)

log_file=sys.argv[1]
level_filter=sys.argv[2]

if len(sys.argv) >=4:
    top_n = int(sys.argv[3])
else:
    top_n=3
    

class Logline:
    def __init__(self,line):
        self.line = line.strip()

    def timestamp(self):
        parts = self.line.split(" ")
        return parts[0]+" "+parts[1]
    
    def level(self):
        parts = self.line.split(" ")
        if len(parts)<3:
            return None
        return parts[2]

    def message(self):
        parts =self.line.split(" ")
        return " ".join(parts[3:])
        

    def is_valid(self):
        parts = self.line.split(" ")
        if len(parts)<4:
            return False
        return True
    
file = open(log_file, "r") 
errors={}
    
for line in file:
    

    log=Logline(line)
    if not log.is_valid():
         continue
    
    if log.level() == level_filter:
        r=log.message()
        if r in errors:
            errors[r]+=1
        else:
            errors[r]=1
        print("raw line:",repr(line))  
        print("time:",log.timestamp())
        print("level:",log.level())
        print("message:",log.message())
        print("________________________")
sorted_errors = sorted(errors.items(),key=lambda item : item [1], reverse=True)
if(top_n>len(sorted_errors)):
 for r,value in sorted_errors:
    print(r,value)
 print(f"Only {len(sorted_errors)} found , less than requested {top_n}")
else:
 top_list= sorted_errors[ : top_n ]
 for r,value in top_list:
    print(r,value)
file.close()



 
