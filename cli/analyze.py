
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
    
file = open("app.log", "r")
errors={}
    
for line in file:
    

    log=Logline(line)
    if not log.is_valid():
         continue
    
    if log.level() == "ERROR":
        r=log.message()
        if r in errors:
            errors[r]+=1
        else:
            errors[r]=1
        print("raw line:",repr(line))  
        print("time:",log.timestamp())
        print("level:","ERROR")
        print("message:",log.message())
        print("________________________")
sort=sorted(errors.items(),key=lambda item : item [1], reverse=True)
for r,value in sort:
    print(r,value)
file.close()



 
