import urllib.request, urllib.error
import sys, random, csv
from multiprocessing.pool import ThreadPool

# settings
secure = 0 # 0 = http 1 = https
tld_location = "tld.txt" # default tld list from ssl.com, set this to None to skip validation
tld_sep = None # change this to your desired file seperator
dictionary_location = "small.txt" # default dictionary is from
dictionary_sep = None # change this to your desired file seperator
default_ext = "" # force a default ext here, this will not be cleared by a negative input, only changed by a positive input
user_agents = [ #edit these to change the random user agents
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
    ]
positives = [1,"y","yes"] # add acceptable positive responses here, if one is not present here a user input is expected to be a negative

# url validation function
def validate_url(url):
    # refine the input
    for n in range(3):
        if not url.startswith("http://") and not url.startswith("https://"):
            if secure == 0:
                url = "http://" + url
            elif secure == 1:
                url = "https://" + url
            else:
                print("Please enter a valid security level in the settings")
                sys.exit()
        elif not url.endswith("/"):
            url = url + "/"
        elif tld_location is not None:
            file = open(tld_location, "r")
            tlds = file.read().split(tld_sep)
            for tld in tlds:
                tld = "." + tld.lower().strip()
                if tld in url.lower():
                    found = True
                    break
                else:
                    found = False
            if found == False:
                print("Please enter an url with a valid top level domain")
                sys.exit()
            file.close()
            break
        else:
            print("Top level domain checking is disabled")
        pass
    try:
        headers = { "User-Agent" : random.choice(user_agents) }
        request = urllib.request.Request(url, data = None, headers = headers)
        response = urllib.request.urlopen(request).getcode()
        if response == 200:
            print("Now using",url,"as the root directory")
    except urllib.error.HTTPError as e:
        e = str(e)
        response = "".join(c for c in e if c.isdigit())
        print(response)
        print("This website is not accepting connections or does not resolve to an IP")
        sys.exit()
    return url

# preloads the dictionary, appends the word to root and stores the result in a list
def load_dictionary(root, ext):
    file = open(dictionary_location, "r")
    wordlist = file.read().split(dictionary_sep)
    address_list = [] #Future# use an array here to save space?
    for word in wordlist:
        address = root + word + ext
        address_list.append(address)
    file.close()
    print("*Dictionary of", len(address_list), "Words Loaded")
    return address_list

# sends get requests from the address_list and record the responses to output_list
def dictionary(address):
    output_list = []
    try:
        request = urllib.request.Request(address, data = None, headers = { "User-Agent" : random.choice(user_agents) })
        response = urllib.request.urlopen(request).getcode()
        if response == 200:
            output_list.append(address)
            ##print(address, "was successful") # show successes
    except urllib.error.HTTPError as e:
        e = str(e)
        response = "".join(c for c in e if c.isdigit())
        ##print(address, "resulted in", response) # show failures
    except urllib.error.URLError as e:
        e = str(e)
        response = "".join(c for c in e if c.isdigit())
        ##print(address, "resulted in", response) # show failures
    return output_list
    
# request user input for minimum length, maximum length, and character types
def bruteforce(root, output):
    print("Fix Me")

# creats up to max_threads and returns responses_list
def create_threads(method, root, ext, max_threads, responses_list):
    if method == 0: # dictionary
        address_list = load_dictionary(root, ext) # only loads the dictionary if it is the selected option
        responses_list = ThreadPool(max_threads).imap_unordered(dictionary, address_list)
        print("*Dictionary Based Threads Created")
    elif method == 1: #bruteforce
        pass
    else:
        print("Please enter a valid option")
        main()
    return responses_list

def write(responses_list, root):
    print("*Starting to Write to .csv")
    responses_list = list(filter(None, responses_list))
    site = root[6:].replace("/","_").strip("_")
    output_file = open(site + ".csv", "w")
    writer = csv.writer(output_file, lineterminator="\n")
    for output in responses_list: # writes once per successful request to the csv
        writer.writerow(output)
    print("*Finished Writing", len(responses_list), "items to .csv")
    
def main():
    # get user inputs
    root = validate_url(input("Please enter the url of the website\n").replace(" ",""))
    method = int(input("Enter 0 to throw a dictionary at the website, enter 1 to punch it, enter 2 to do both\n"))
    max_threads = int(input("Please enter your desired amount of threads at max load\n"))
    if input("Would you like to search for something other than the default extension?\n") in positives:
        ext = input("Desired extension in .ext format or None\n")
    else:
        ext = default_ext
    # create the output/responses list and prep for output/responses 
    output_list = []
    responses_list = []
    responses_list = create_threads(method, root, ext, max_threads, responses_list)
    # write out the responses
    write(responses_list, root)
    
main()
