# Elections

Using twitter data to predict primary election results.

## Gathering Data

### Setting up MongoDB ( AWS - Ubuntu)

Follow the steps to setup MongoDB on an Ubuntu machine.

```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

On a Mac:
```
brew update
brew install mongodb
```

#### Starting MongoDB:

`sudo service mongod start`

#### Stopping MongoDB:

`sudo service mongod stop`

### Installing tweepy and pymongo
```
pip install tweepy
pip install pymongo
```
### Setting the environment variables

In the ~/.bashrc file (ubuntu) or ~/.bash_profile file (mac), enter the following:
```
export TWITTER_CONSUMER_KEY='your key'
export TWITTER_CONSUMER_KEY_SECRET_0='your key'
export TWITTER_ACCESS_TOKEN_KEY='your key'
export TWITTER_ACCESS_TOKEN_KEY_SECRET_0='your key'
export PYTHONPATH="Location of your folder (in this case the location of the folder 'Elections' ":$PYTHONPATH
```
then either load a new prompt or run

`source ~/.bashrc`
or
`source ~/.bash_profile`

### Tmux

A tmux session named collect_twitter_data has been created. It will be running in the background forever until terminated explicitly. Currently extract-tweets.py is running on the AWS instance and it is collecting data. To view what's happening you should 'attach' to that session. Basically, ssh to our instance from the terminal and run the command:

`tmux attach -t collect_twitter_data`

Then you can use it as an usual ubuntu terminal.

For more info on tmux - https://robots.thoughtbot.com/a-tmux-crash-course

## Real-time analytics using streamparse

[Streamparse](https://github.com/Parsely/streamparse) lets you run Python code against real-time streams of data via Apache Storm. With streamparse you can create Storm bolts and spouts in Python without having to write a single line of Java. It also provides handy CLI utilities for managing Storm clusters and projects.

### Quickstart with streamparse
With no need for any coding in Java, streamparse lets you [get started](http://streamparse.readthedocs.org/en/stable/quickstart.html) right away with a basic wordcount topology.

**Important:** The version of `lein` installed should be `2.x`. If not, upgrade it by following [this](https://github.com/technomancy/leiningen/wiki/Upgrading).

## Sentiment Analysis

For sentiment analysis we are using a Naive Bayes classifier from ntlk. The training data currently used is a set of 800,000 tagged tweets.

All examples are from within the `sentiment` directory.

### Training a classifier

Trim and keep all 800,000 tweets
```
$ python3 trim.py
```

Trim to 10,000 tweets (faster for testing, use any number up to 800,000)
```
$ python3 trim.py training_set.csv 10000
```

Train the classifier (need the trimmed.csv file from above)
```
$ python3 trainer.py
```

Train the classifier, with 10 iterations over each set (no accuracy improvement, but gives you a better basis for comparison if there are more trials)
```
$ python3 trainer.py 10
```

### Using a classifier

The most accurate classifier from training will be saved at the end and that classifier is loaded here. Edit your config.json to use a different classifier.

To test using the interactive cli
```
$ python3 cli.py
? this is awesome!
pos
? this sucks
neg
```

You can also use the `Analyzer` class provided for use within another program. See the `cli.py` file for an example.
