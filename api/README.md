'''sh
awscurl --service lambda 'https://gbd7kw7udcw2piemn5londn7ga0kafdb.lambda-url.us-east-1.on.aws/'

awscurl --service lambda -X 'PUT' 'https://gbd7kw7udcw2piemn5londn7ga0kafdb.lambda-url.us-east-1.on.aws/create-task' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"content": "this is a test", "user_id": "chom", "task_id": "test", "is_done":"False"}'

awscurl --service lambda -X 'GET' 'https://gbd7kw7udcw2piemn5londn7ga0kafdb.lambda-url.us-east-1.on.aws/get-task' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"task_id": "task_d8ead93f0a604f54802cd5184e49cdb1" }'
