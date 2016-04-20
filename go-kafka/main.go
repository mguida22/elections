package main

import (
	"github.com/Shopify/sarama"
	"log"
	"os"
	"os/signal"
)

func main() {
	consumer, err := sarama.NewConsumer([]string{"localhost:9092"}, nil)
	if err != nil {
		panic(err)
	}

	defer func() {
		if err := consumer.Close(); err != nil {
			log.Fatalln(err)
		}
	}()

	partitionConsumer, err := consumer.ConsumePartition("twitterfeed", 0, sarama.OffsetNewest)
	if err != nil {
		panic(err)
	}

	defer func() {
		if err := partitionConsumer.Close(); err != nil {
			log.Fatalln(err)
		}
	}()

	// Trap SIGINT to trigger a shutdown.
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	consumed := 0

	for {
		select {
		case msg := <-partitionConsumer.Messages():
			log.Println(string(msg.Value))
			consumed++
		case <-signals:
			break
		}
	}

	log.Printf("Consumed: %d\n", consumed)
}
