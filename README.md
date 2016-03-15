# Elections
Using twitter data to predict primary election results.

## Setting up MongoDB ( AWS - Ubuntu)

Follow the steps to setup MongoDB on an Ubuntu machine.

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

On a Mac:

brew update
brew install mongodb

### Starting MongoDB:
sudo service mongod start

### Stopping MongoDB:
sudo service mongod stop

## Installing tweepy and pymongo

pip install tweepy
pip install pymongo

## Setting the environment variables

In the ~/.bashrc file (ubuntu) or ~/.bash_profile file (mac), enter the following:

export TWITTER_CONSUMER_KEY='your key'
export TWITTER_CONSUMER_KEY_SECRET_0='your key'
export TWITTER_ACCESS_TOKEN_KEY='your key'
export TWITTER_ACCESS_TOKEN_KEY_SECRET_0='your key'
export PYTHONPATH="Location of your folder (in this case the location of the folder 'Elections' ":$PYTHONPATH

then either load a new prompt or run

source ~/.bashrc
or
source ~/.bash_profile

## Tmux

A tmux session named collect_twitter_data has been created. It will be running in the background forever until terminated explicitly. Currently extract-tweets.py is running on the AWS instance and it is collecting data. To view what's happening you should 'attach' to that session. Basically, ssh to our instance from the terminal and run the command:

tmux attach -t collect_twitter_data

Then you can use it as an usual ubuntu terminal. 

For more info on tmux - https://robots.thoughtbot.com/a-tmux-crash-course
