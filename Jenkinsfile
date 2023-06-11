pipeline {
    agent any
    
    environment {
        PATH = "C:\\WINDOWS\\SYSTEM32;C:\\Program Files\\Docker\\Docker\\resources\\bin"
        GDRIVE_CREDENTIALS_DATA = {
                                      "type": "service_account",
                                      "project_id": "causal-medium-238907",
                                      "private_key_id": "f63fe54c04cc27cf13bfaa0b80d3fd0b6c89b0e8",
                                      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQD9dmLZlEcuE/z4\n3JiCwJovaRftE+gnVz22t4t2viu45EhXy5lW0ZA80u1h7aqVcUHUBzdDCIgPRhRg\nemOa0+YhCXsiaysvUPe/ncEuTaQT5qHXfp3XbAzYf1/NmVFWouH21SQnfDo9mFY0\nBoIGk2dllA85SvD3HAnIwvkc1suTfF7ci9XzX7JfzCtPh1uWZBrpM/IC0VlPNQEV\nnognylk5WsuYyJqhHKv4BsLjUoq0awmx2wAD5gnP+tdy4Upm+GNVAL/DTLJ//7C/\njxuzegvUESjxPGbgWoXHGDOvDKXD7zSFpZTL9wfmpnQT9xlek8UVhKVJ0NKXXsHH\nyrpUIZ1NAgMBAAECggEABmAid2ef7LxK+jWOToequTOTCv8bsVWj80Mlqmx5LBLt\n8OtppYHq92S03Og+CLlLFxrBXJnL1lqEa7LYa44V9VHIO6LneK64NKUytUf1rxx3\niLSiIseQgSefEMxg++Vn+q381VNuIZuB25goUCMIEEmLonzMl+KoKlkhLAUJJOII\nrjOEX6gwjDQsxuobyV/CCwkRpAZKpp6K38V3dB5r5W60uSpzwkQhbdEwBkRlmruV\nQoXydN0WVKeanQ4TQVRlCQiJYcnydpP3zt8ZCakY1h6KM5WjxRzC8GtrYgu6FUjE\nfiAdod0B0iDDkRcsWAbNZsvJYaeVgu2IbaAuI25lbwKBgQD/BsVh4piXtY2mmgVG\nmtRXJcD1G8Ur8k4X4EmocujYRK4Ii+ZzC8+gptqzVnTiCaYfWqXSiCazAnTnXGIS\nymeR0R74H7JQSgkZo2Pd9mhaY5VK+UYn7YWT/SOr17c8LhJkUZ3hfXJldb8jdleG\nExR8gsdnhUndR25PSFSFGmsMYwKBgQD+bhYvPmyJZ76PaQtUWEOvJEG7lmIunnuu\nsR/iVVFP5+zLxEG/vHOuia44ehZwMrLnECESBqZiaYZcsMA8mIE7g3uIYmgbeJgw\npEwtZIgG0RhaLvXNd9XKZOGxdwj9CLmE00QRuljkG94fVTg8/7EQ4q+MRvp4YKBW\nrQX3yjUmjwKBgQCvbt37PyCPREJEODGm5z1pEbySIF9botybyhuBeEK6+0vo7yxB\nOf/DWOSbd78B+3c+nGHz2NseS3NV8JQ6rufeREgUkeFdIADwlRhPCYGxpE1//MiJ\nEPjR29JdFRCkomDeh9Ke2mgGaaBp6a+9uIRgPqqjiOpOASRd/7i8s3auVwKBgQD7\nKkHMMZuDqV58w/3jLZ7jbq9VN4eE7f663S/UhtTWROWF4h/l32tziYbrSdqMt//U\nCiAbY2UtEW8KYZHkP8iTr6BrannLZKkYm5h31x5RXGjl3iXYx8vNGPmT7yZ4Y/yA\nGu6/cW3/AWOtGruBvAhX2u/hUtA/tWOTLQsPKhZ+EQKBgGuX20vi5uSKztHqfR6k\nFvPHvVB5OOELZOnjA3h2KuL6B+Ezms0scsVThAjDyCPEBIA27oVgk8+pMcc7DKla\nUYmwnQPKYhiRpuJDUL/ldNkl+0QPj7B1z4DBA97s5PP+E2beaZ+Jn0J6QdwBk3v2\neRQz34V+dV+VKiY1tJ6aiK+D\n-----END PRIVATE KEY-----\n",
                                      "client_email": "mlops-project@causal-medium-238907.iam.gserviceaccount.com",
                                      "client_id": "106822059257179820049",
                                      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                      "token_uri": "https://oauth2.googleapis.com/token",
                                      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mlops-project%40causal-medium-238907.iam.gserviceaccount.com",
                                      "universe_domain": "googleapis.com"
                                    }
    }

    stages {  
        
        stage('Pull Raw Data From Remote using DVC') {
            steps {
                script{
                    bat "dvc remote modify drive gdrive_use_service_account true"
                    bat "dvc pull annotations.json"
                }
            }
        }
        
        stage('Process Raw Data') {
            steps {
                script{
                    bat "conda activate base"
                    bat "python process_data.py"
                }
            }
        }
        
        stage('Train ML Model') {
            steps {
                script{
                    bat "python train.py"
                }
            }
        }
                         
        stage('Build Image and Push to DockerHub') {
            steps {
                script{
                    dockerImage = docker.build("abdullahajaz/FYP:latest")
                    if(dockerImage){
                        withDockerRegistry([credentialsId: "dockerhub", url: ""]) {
                            dockerImage.push()
                        }
                    }else{
                        error "Docker image build failed."
                    }
                }
            }
        } 
        
        stage('Deploy the Docker Container') {
            steps {
                script{
                    bat "docker run -d -p 8086:8086 abdullahajaz/FYP:latest"
                }
            }
        }
    }
}
