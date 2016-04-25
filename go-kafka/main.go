package main

import (
	"encoding/json"
	"github.com/Shopify/sarama"
	"log"
	"time"
)

type feedMessage struct {
	Sentiment string
	Candidate string
}

type score struct {
	positive int
	negative int
}

func main() {

	//create a new consumer to look at the tweets
	consumer, err := sarama.NewConsumer([]string{"localhost:9092"}, nil)

	//if there is an error, end the progam
	if err != nil {
		panic(err)
	}

	//make sure to close the consumer when the function is over
	defer func() {
		if err := consumer.Close(); err != nil {
			log.Fatalln(err)
		}
	}()

	//create a new topic to listen
	partitionConsumer, err := consumer.ConsumePartition("sentimentfeed", 0, sarama.OffsetOldest)

	if err != nil {
		panic(err)
	}

	defer func() {
		if err := partitionConsumer.Close(); err != nil {
			log.Fatalln(err)
		}
	}()

	//create a message once so we can add to it later
	newSentiment := feedMessage{}

	//create a map for a new sentiment
	candidateMap := make(map[string]*score)

	//count for amount of messages managed
	messagesRead := 0

	//create a tick so that we know to send messages every two seconds
	//this can be overridden if the array is too large
	tick := time.Tick(time.Second * 2)

	for {
		select {

		//if there is a message
		case msg := <-partitionConsumer.Messages():
			{
				//put the json values into the struct
				json.Unmarshal(msg.Value, &newSentiment)

				//if the message is for no one
				if newSentiment.Candidate == "none" {
					break
				}

				positive := false

				if newSentiment.Sentiment == "pos" {
					positive = true
				}

				//if the candidate is not already in the map
				if _, ok := candidateMap[newSentiment.Candidate]; !ok {

					candidateMap[newSentiment.Candidate] = &score{}
				}

				//if the tweet is postive
				if positive {
					candidateMap[newSentiment.Candidate].positive++

				} else {
					candidateMap[newSentiment.Candidate].negative++
				}

				messagesRead++

				//if there are more than 100 messages, go ahead and send it
				if messagesRead > 100 {

					//send the array to the client now
					tick = time.Tick(time.Nanosecond)
				}
			}

		//send messages out every two seconds
		case <-tick:
			{
				if messagesRead != 0 {

					//logic to send message to client goes here
					//
					fullArray := make(map[string]score)

					for key, value := range candidateMap {

						fullArray[key] = *value
					}

					log.Println(fullArray)
					//
					//end logic

					log.Println(messagesRead, "messages read")
					messagesRead = 0

					for key := range candidateMap {

						delete(candidateMap, key)
					}
				}

				tick = time.Tick(time.Second * 2)
			}
		}
	}
}
