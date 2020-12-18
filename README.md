
# HTTP(S) - Client 

### Program can:
* Send REQUEST_TYPE requests and get answer
* Send data from file by post request
* Save answer in file
-----------------------------------------------------------------------------------------------------------------------------------  
### How it works:
* You should print in terminal: python main.py url args
-----------------------------------------------------------------------------------------------------------------------------------
|Argument|Action|Using Examples| 
|----------|------|--------------|
|-d or --data|Set data| -d "Hello, World!"|
|-f or --file|Set data from file|-f "test.txt"|
|-l or --reference|Add reference in request|-e "https://github.com/trrail/python-tasks/edit/master/README.md"|
|-O or --output|Write answer in file|-O "test.txt|
|-a or --agent|Set User-Agent in request|-a "Mozilla/5.0"|
|-c or --cookie|Set cookie in request|-c "income=1"|
|-H or --headers|Add headers|-h "Accept: */* Authorization: YWxhZGRpbjpvcGVuc2VzYW1l"|                            
|-v or --verbose|Print request with response|-v|
|-C or --cookie_ile|Set cookie from file, point out path|-c "cookie.txt"|
|-r or --request|Set request method|-r "POST or PUNCH or CONNECT or DELETE or OPTION or PUT or etc"|
|-0|Ignore body of response|-0|
|-1|Ignore head of response|-1|
|-t or --timeout|Set timeout for connect|-t 3000|
|-p or --protocol|Set protocol| -p HTTP/1.1|
|-g or --redirect|Set max count redirect|-g 30|
-----------------------------------------------------------------------------------------------------------------------------------



