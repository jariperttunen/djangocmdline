import argparse
import requests
import os
from requests.auth import HTTPBasicAuth
#1. Motti fertilization www addresses
server_address='http://127.0.0.1:8000/'
url_home = server_address
url_upload = url_home+'uploadxml'
url_run = url_home+'updatexml'
url_get = url_home+'downloadxml'
proxies = {'http':'http://10.88.2.10:8080','https':'https://10.88.2.10:8080'}
#2. This 'browser_header'emulates Safari on macOS as User-Agent.
#   Django requires 'Referer' [sic] in the http header for all 'POST' requests.
#   For more see https://en.wikipedia.org/wiki/User_agent. 
browser_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
                  'Referer':url_home}
#3. The 'files_data' dictionary for file upload:
#3.1 The dictionary key 'upload_template_files' is the FileField name of Django form FertilizationTemplateUploadForm (in forms.py)
#that receives and can extract the excel file.
#The key value is a 3-tuple as follows:
#3.2 'args.f' (command line argument) is the existing excel fertilization template file (in the working directory)
#3.3 file 'open' is needed, we will obviously send the content of the file
#3.4 'application/vnd.ms-excel' tells the file type explicitely
#3.5 The dictionary {'Expires':'0'} is not needed anymore.
#The 'files_data' dictionary looks like this. Note: file data is available after command line parsing.
#files_data = {'upload_template_files': (args.f, open(args.f, 'rb'), 'application/vnd.ms-excel')}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',type=str,dest='f',help="XML template input file")
    args = parser.parse_args()
    if args.f == None:
      print("No XML file")
      quit()
    os.environ['NO_PROXY']='127.0.0.1'
    files_data = {'upload_xml': (args.f, open(args.f, 'rb'), 'application/xml')}
    #1. Start the session, note the same connection is used throughout the session 
    s = requests.Session()
    #Query the home page, you will get the csrftoken (one of Django www security component)
    print("HOME PAGE")
    r=s.get(url_home,headers=browser_header)
    print("R HEADER",r.headers)
    #print("R CONTENT",r.content)
    print("R COOKIES",r.cookies)
    #response.raise_for_status()
    print("HOME PAGE DONE")
    csrf_token=r.cookies['csrftoken']
    print("CSRF",csrf_token)
    #2. Upload the excel file, send back cookies, note the 'csrfmiddlewaretoken' for the Django www application, note 'auth' is needed each time
    r1=s.post(url_upload,headers=browser_header,cookies=r.cookies,files=files_data,data={'csrfmiddlewaretoken':csrf_token})
    #3. Run the motti simulation
    r2=s.post(url_run,headers=browser_header,cookies=r.cookies,data={'csrfmiddlewaretoken':csrf_token})
    #4. Retrieve the resulting excel file
    r3=s.get(url_get,headers=browser_header,cookies=r.cookies,data={'csrfmiddlewaretoken':csrf_token})
    #4.1 Fancy way to retrieve the file name, you should get the same uploaded file but with results, with "Out.xml" in the name.
    print("r3 HEADERS",r3.headers)
    fname = r3.headers['Content-Disposition'].split('=')[1]
    #4.2 Write the file
    f=open(fname, 'wb')
    f.write(r3.content)
    f.close()
    #Done
