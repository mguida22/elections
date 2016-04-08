## Setting up streamparse: 

1) Install leiningen: 

Ubuntu: 

``` sudo apt-get install leiningen ```

Mac: 

``` brew install leiningen ```

Make sure the version of leiningen is 2.6.1

2) Install streamparse:

``` pip install streamparse ```

For trying out a sample project (Word count)

```
cd wordcount
sparse run
```

Refer: https://streamparse.readthedocs.org/en/stable/quickstart.html#your-first-project

This does not require kafka and zookeeper and should run as it is provided leiningen and streamparse have been installed correctly.

## Setting up Kafka and Zookeeper:

1) Install Kafka

Download the latest binary version (2.11 is recommended) from https://kafka.apache.org/downloads.html 

2) Follow the instructions at https://kafka.apache.org/07/quickstart.html to run a zookeper instance and kafka server. You can run a producer and consumer instance to exchange messages.

If it works properly, then the setup is complete. 

## Basic Idea:

Run the twitter stream and collect the tweets in a kafka queue and the spout reads off the tweets from the kafka queue. 

Refer to the code in github to run the twitter stream through a spout.
