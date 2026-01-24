import sys
import argparse
from datetime import datetime 

def parse_time(t):
   if t is None:
      return None
   try:
      return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
   except ValueError:
      print(f"Invalid time format: {t}")
      print("Expected format: YYYY-MM-DD HH:MM:SS")
      sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze log files and find most frequent error messages"
    )
    parser.add_argument("logfile", help="path to log file")
    parser.add_argument(
       "--level",
       action="append",
       required=True,
       help="Log level to filter (can be used multiple times, e.g. --level ERROR --level INFO)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top results to show (default: 3)"
    )
    parser.add_argument("--stats",action="store_true",help="Show processing statistics")
    parser.add_argument("--quiet",action="store_true",help="show top errors only")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
       "--since",
       help="Start time filter (format: YYYY-MM-DD HH:MM:SS)",
    )

    parser.add_argument(
       "--until",
       help="End time filter (format: YYYY-MM-DD HH:MM:SS)",
    )

    args = parser.parse_args()

    return args.logfile, args.level, args.top , args.stats , args.quiet ,args.json , args.since , args.until

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
        if "-" not in parts[0] or ":" not in parts[1]:
            return False
        return True
    
    def timestamp_dt(self):
       try:
          return datetime.strptime(self.timestamp(), "%Y-%m-%d %H:%M:%S")
       except ValueError:
          return None
    
def process_file(log_file , levels , quiet , json_flag, since_time,until_time):
  errors={}
  try:
   with open(log_file,"r") as file:
    total_lines=0
    valid_lines=0
    invalid_lines=0
    matched_lines=0
   
    for line in file:
     total_lines+=1

     log=Logline(line)
     if not log.is_valid():
         invalid_lines+=1
         continue
    

     log_time=log.timestamp_dt()
     if log_time is None:
        invalid_lines+=1
        continue
     valid_lines+=1

     if since_time and log_time < since_time:
        continue
     if until_time and log_time > until_time:
        continue
        
        
     if log.level() in levels:
        matched_lines+=1
        r=log.message()
        if r in errors:
            errors[r]+=1
        else:
            errors[r]=1
        if not quiet and not json_flag:       
         print("raw line:",repr(line))  
         print("time:",log.timestamp())
         print("level:",log.level())
         print("message:",log.message())
         print("________________________")

  except FileNotFoundError:
    print("Error: Log file not found")
    sys.exit(1)

  stats={
     "total lines": total_lines,
     "valid lines": valid_lines,
     "invalid lines": invalid_lines,
     "matched lines": matched_lines
  }
  return errors,stats

def print_results(errors,levels,top_n,json_flag):
  if len(errors)==0:
        print(f"no logs found for levels: {','.join(levels)}")
        return 
  if json_flag:
     import json
     sorted_errors = sorted(errors.items(),key=lambda item : item [1], reverse=True)
     top_list = sorted_errors[:top_n]

     data = {
        "level": levels,
        "top_n": top_n,
        "results": [
           {"message": msg , "count": count}
           for msg ,count in top_list
        ]
     } 

     print(json.dumps(data, indent=2))
     return 
  
  sorted_errors = sorted(errors.items(),key=lambda item : item [1], reverse=True)
  if top_n>len(sorted_errors):
    for r,value in sorted_errors:
        print(r,value)
    print(f"Only {len(sorted_errors)} found , less than requested {top_n}")


  else:
    top_list= sorted_errors[ : top_n ]
    for r,value in top_list:
        print(r,value)
 
def main():
 log_file,level_filter,top_n,show_stats,quiet,json_flag,since_string,until_string=parse_args()
 since_time=parse_time(since_string)
 until_time=parse_time(until_string)
 if since_time and until_time and since_time > until_time:
    print("Error: --since must be earlier than --until")
    sys.exit(1)
 errors,stats=process_file(log_file,level_filter,quiet,json_flag,since_time,until_time)
 print_results(errors,level_filter,top_n,json_flag)
 if show_stats and not json_flag:
    print("stats:")
    print(f" Total Lines : {stats['total lines']}")
    print(f" Valid Lines : {stats['valid lines']}")
    print(f" Invalid Lines : {stats['invalid lines']}")
    print(f" matched Lines : {stats['matched lines']}")
if __name__ =="__main__":
 main()



 
