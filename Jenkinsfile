pipeline {
    agent any
    
    environment {
        PATH = "C:\\WINDOWS\\SYSTEM32;C:\\Program Files\\Docker\\Docker\\resources\\bin;C:\\Users\\Computer\\anaconda3;C:\\Users\\Computer\\anaconda3\\Scripts;C:\\Program Files\\Git\\bin;C:\\Program Files\\Git\\cmd"
    }

    stages {  
        
        stage('Pull Raw Data From Remote using DVC') {
            steps {
                script{
                    withCredentials([string(credentialsId: 'GDRIVE_CREDENTIALS_DATA', variable: 'GDRIVE_CREDENTIALS_DATA')]){
                        bat "dvc remote modify drive gdrive_use_service_account true"
                        bat "dvc pull annotations.json"
                    }
                }
            }
        }
        
        
        stage('Process Raw Data') {
            steps {
                script{
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
        
        

