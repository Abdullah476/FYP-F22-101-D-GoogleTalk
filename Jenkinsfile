pipeline {
    agent any
    
    environment {
        PATH = "C:\\WINDOWS\\SYSTEM32;C:\\Program Files\\Docker\\Docker\\resources\\bin"
    }

    stages {  
        
        stage('Pull Raw Data From Remote using DVC') {
            steps {
                script{
                    
                }
            }
        }
        
        stage('Process Raw Data') {
            steps {
                script{
                    
                }
            }
        }
        
        stage('Train ML Model') {
            steps {
                script{
                    
                }
            }
        }
                        
        stage('Build Image and Push to DockerHub') {
            steps {
                script{
                    dockerImage = docker.build("abdullahajaz/i190476_i190695_mlops_a2:latest")
                }
            }
        }
        
    }
}
