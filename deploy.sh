aws ecr get-login-password --region sa-east-1 | sudo docker login --username AWS --password-stdin 689566614228.dkr.ecr.sa-east-1.amazonaws.com
sudo docker build -t tweet_collector .
sudo docker tag tweet_collector:latest 689566614228.dkr.ecr.sa-east-1.amazonaws.com/tweet_collector:latest
sudo docker push 689566614228.dkr.ecr.sa-east-1.amazonaws.com/tweet_collector:latest
