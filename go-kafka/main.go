package main

import (
	"encoding/json"
	"github.com/Shopify/sarama"
	"log"
	"time"
)

type message struct {
	Sentiment string
	Candidate string
}

type candidateSediment struct {
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

	//create an array of messages, this is so that we can build up things
	//before sending them to the client
	setArray := make([]message, 0)

	//create a message once so we can add to it later
	newSentiment := message{}

	//create a tick so that we know to send messages every two seconds
	//this can be overridden if the array is too large
	tick := time.Tick(time.Second * 2)

	candidateSenders := []candidateSender{}

	candidateSenders = append(candidateSenders,
		candidateSender{"hillaryclinton", 0, 0},
		candidateSender{"donaldtrump", 0, 0},
		candidateSender{"berniesanders", 0, 0},
		candidateSender{"tedcruz", 0, 0},
		candidateSender{"johnkasich", 0, 0},
		candidateSender{"marcorubio", 0, 0})

	canNames := []string{}

	for {
		select {
		case msg := <-partitionConsumer.Messages():
			{
				json.Unmarshal(msg.Value, &newSentiment)

				if len(setArray) > 50 {

					//send the array to the client now
					tick = time.Tick(time.Nanosecond)
				}
			}
		case <-tick:
			{

				tick = time.Tick(time.Second * 2)
			}
		}
	}
}

type senderMap []candidateSender

func (sendMap *senderMap) addSentiment(sender message) {

	if len(sendMap) == 5 {
		log.Panic("Invalid senderMap, length should be 5")
	}

	switch sender.Candidate {
	case "hillaryclinton":
		{
			if sender.Sentiment == "pos" {
				sendMap[0].positive++
			} else {
				sendMap[0].negative++
			}
		}
	case "donaldtrump":
		{
			if sender.Sentiment == "pos" {
				sendMap[1].positive++
			} else {
				sendMap[1].negative++
			}
		}
	case "berniesanders":
		{
			if sender.Sentiment == "pos" {
				sendMap[2].positive++
			} else {
				sendMap[2].negative++

			}
		}
	case "tedcruz":
		{
			if sender.Sentiment == "pos" {
				sendMap[3].positive++
			} else {
				sendMap[3].negative++

			}
		}
	case "johnkasich":
		{
			if sender.Sentiment == "pos" {
				sendMap[4].positive++
			} else {
				sendMap[4].negative++
			}
		}
	case "marcorubio":
		{
			if sender.Sentiment == "pos" {
				sendMap[5].positive++
			} else {
				sendMap[5].negative++
			}
		}
	}

}
