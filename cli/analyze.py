import sys
import argparse
from datetime import datetime 
class LogRecord:
   def __init__(self , timestamp ,  level , message , raw_line):
      self.timestamp = timestamp
      self.level = level
      self.message = message
      self.raw_line= raw_line


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
    parser.add_argument(
       "--verbose",
       action="store_true",
       help="show detailed log lines",
    )
    parser.add_argument(
       "--format",
       default="simple",
       choices=["simple"],
       help="Log format (default: simple)"
    )

    args = parser.parse_args()

    return args.logfile, args.level, args.top , args.stats , args.quiet ,args.json , args.since , args.until , args.verbose , args.format,
class SimpleLogParser:
 def parse(self , line):
   parts = line.strip().split(" ")

   if len(parts)< 4:
      return None
   
   try:
      timestamp_str= parts[0]+" "+parts[1]
      timestamp = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")
   except ValueError:
      return None
   
   level = parts[2]
   message = " " .join(parts[3:])

   return LogRecord(
      timestamp=timestamp,
      level=level,
      message=message,
      raw_line=line

   )


def process_file(log_file , levels , quiet , json_flag, since_time,until_time,log_format):
  errors={}
  matched_logs =[]
  parser=SimpleLogParser()

  if log_format=="simple":
     parser=SimpleLogParser()
  else:
     print(f"Unsupported log format: {log_format}")
     sys.exit(1)

  try:
   with open(log_file,"r") as file:
    total_lines=valid_lines=invalid_lines=matched_lines=0
    
    for line in file:
     total_lines+=1

     record=parser.parse(line)
     if record is None:
         invalid_lines+=1
         continue
     
     valid_lines+=1

     log_time=record.timestamp
     

     if since_time and log_time < since_time:
        continue
     if until_time and log_time > until_time:
        continue
        
        
     if record.level in levels:
        matched_lines+=1
        errors[record.message] =errors.get(record.message,0)+1
        matched_logs.append(record)

  except FileNotFoundError:
    print("Error: Log file not found")
    sys.exit(1)

  stats={
     "total lines": total_lines,
     "valid lines": valid_lines,
     "invalid lines": invalid_lines,
     "matched lines": matched_lines
  }
  return errors,stats , matched_logs

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
 log_file,level_filter,top_n,show_stats,quiet,json_flag,since_string,until_string,verbose,log_format,=parse_args()
 since_time=parse_time(since_string)
 until_time=parse_time(until_string)
 if since_time and until_time and since_time > until_time:
    print("Error: --since must be earlier than --until")
    sys.exit(1)

 errors,stats , matched_logs=process_file(log_file,level_filter,quiet,json_flag,since_time,until_time,log_format)

 if verbose and not json_flag and not quiet:
    for record in matched_logs:
     print("time:", record.timestamp)
     print("level:",record.level)
     print("message:",record.message)
     print("--------")

 print_results(errors,level_filter,top_n,json_flag)
 if show_stats and not json_flag:
    print("stats:")
    print(f" Total Lines : {stats['total lines']}")
    print(f" Valid Lines : {stats['valid lines']}")
    print(f" Invalid Lines : {stats['invalid lines']}")
    print(f" matched Lines : {stats['matched lines']}")
if __name__ =="__main__":
 main()



 
