from multiprocessing import Pool
import requests
import argparse
import signal

class Zero_Finder():
    def __init__(self,target,file,extensions,output_file,blacklist_status_code,threads,header,cookie,user_agent,proxy):
        self.target = target
        self.file = file
        self.extensions = extensions
        self.output_file = output_file
        self.blacklist_status_code = blacklist_status_code
        self.threads = threads
        self.header = header
        self.cookie = cookie
        self.user_agent = user_agent
        self.proxy = proxy
        
        if args.e:
            self.ext_list = self.create_extensions()
        self.url = self.check_url()
        self.headers,self.proxy_set = self.create_headers()
        self.set_processes()

    def create_extensions(self):
        ext_list = self.extensions.split()
        ext_list.insert(0,"")

        return ext_list

    def check_url(self):
        check = self.target[-1]
        if check == "/": 
            return self.target
        else:
            fixed_url = self.target + "/"
            return fixed_url

    def create_headers(self):
        headers = {
            "Connection":"close"
        }
        
        proxy_set = {}

        if args.a:
            headers["User-Agent"] = self.user_agent

        if args.p:
            proxy_set = {
                "http": "http://" + self.proxy
            }
        
        if args.c:
            headers['Cookie'] = self.cookie

        if args.H:
            header_list = self.header.split(': ')
            list_length = len(header_list) - 1 
            for each_header in range(0,list_length):
                headers[header_list[each_header]] = header_list[each_header + 1]

        return headers,proxy_set

    def set_processes(self):
        print("Finding Pages:")

        if args.b:
            print("Blacklisted Status Code: " + self.blacklist_status_code)

        if args.o:
            file_write = open(self.output_file,"w")
            file_write.close()

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = Pool(processes=int(self.threads)) 
        signal.signal(signal.SIGINT, original_sigint_handler)

        wordlist = []
        with open(self.file,'r') as wordlist_file: 
            for each_word in wordlist_file: 
                if args.e:
                    for ext in self.ext_list:
                        if each_word.find("#") != -1:
                            continue
                        word_ext = each_word.strip() + ext
                        wordlist.append(word_ext.strip())
                else:
                    if each_word.find("#") != -1:
                            continue
                    wordlist.append(each_word.rstrip())

        try:
            start = pool.map_async(self.directory_finder,wordlist)
        except KeyboardInterrupt:
            pool.terminate()
        else:
            pool.close()
        pool.join()

        print("Done!")

    def directory_finder(self,word):
        requests.packages.urllib3.disable_warnings()

        if args.b:
            self.blacklist_status_code = self.blacklist_status_code
        else:
            self.blacklist_status_code = 404
                
        sites = self.url + word
        found = requests.get(sites, allow_redirects = False, verify=False,headers=self.headers,proxies=self.proxy_set) 
            
        if args.o:
            if found.status_code != 404 and found.status_code != int(self.blacklist_status_code):
                print("Found: ", found.url, "\tStatus Code:", found.status_code)  

                file_write = open(self.output_file,'a')
                file_write.write("Found: ")
                file_write.write(found.url)
                file_write.write("\tStatus Code: ")
                file_write.write(str(found.status_code))
                file_write.write("\n")
                file_write.close() 

        elif found.status_code != 404 and found.status_code != int(self.blacklist_status_code):
            print("Found: ", found.url, "\tStatus Code:", found.status_code)                                                         

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Brute Forcing Directories and Pages')

    parser.add_argument('-u', metavar='<Target URL>', help='target/host URL, E.G: -t http://findme.blah/', required=True)
    parser.add_argument('-e', metavar='<extensions>',help="Example: -e '.ext1 .ext2 .ext3'", required=False)
    parser.add_argument('-w', metavar='<wordlist file>',help="Example: -w list.txt", required=True)
    parser.add_argument('-o', metavar='<output file>',help="Example: -o output.txt", required=False)
    parser.add_argument('-b', metavar='<Blacklist Status Code>',help="Example: -b 500", required=False)
    parser.add_argument('-t', metavar='<Threads>',default="10",help="Example: -t 100. Default 10", required=False)
    parser.add_argument('-H', metavar='<Header>',help="Example -H 'Parameter: Value", required=False)
    parser.add_argument('-c', metavar='<Cookie>',help="Example -c 'Cookie Value", required=False)
    parser.add_argument('-a', metavar='<User-Agent>',help="Example: -a Linux", required=False)
    parser.add_argument('-p', metavar='<Proxies>',help="Example: -p 127.0.0.1:8080", required=False)

    args = parser.parse_args()

    try:
        Zero_Finder(args.u,args.w,args.e,args.o,args.b,args.t,args.H,args.c,args.a,args.p)
    except KeyboardInterrupt:
        print("Bye Bye") 
        exit()