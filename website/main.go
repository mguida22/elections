package main

import (
	"encoding/json"
	"github.com/Shopify/sarama"
	"html/template"
	"log"
	"net/http"
	"time"
)

type feedMessage struct {
	Sentiment string
	Candidate string
}

type score struct {
	Positive int
	Negative int
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

	//Make a new Connection Hub instance
	hub := &ConHub{
		broadcast:   make(chan pushMessage),
		register:    make(chan *connection),
		unregister:  make(chan *connection),
		connections: make(map[*connection]bool),
	}

	//Start processing events
	hub.run()

	//Make b the HTTP handler for "/events/".  It can do
	//this because it has a ServeHTTP method.  That method
	//is called in a separate go-routine for each
	//request to "/events/".
	http.Handle("/events/", hub)

	//generate a fake function that sends the time to the user every second
	//again we will get rid of this once we get storm working
	go func() {
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
						candidateMap[newSentiment.Candidate].Positive++

					} else {
						candidateMap[newSentiment.Candidate].Negative++
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

						jsonString, err := json.Marshal(fullArray)

						if err != nil {
							log.Panicln(err)
						}

						hub.broadcast <- pushMessage{jsonString}
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
	}()

	//start the main handler
	http.HandleFunc("/", MainPageHandler)

	//start the static file server in the /static/ dir
	fs := http.FileServer(http.Dir("static"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	//start the server on port 8000, this will listen forever
	http.ListenAndServe(":8000", nil)
}

//Handler for the main page
func MainPageHandler(w http.ResponseWriter, r *http.Request) {

	//make sure we don't match on anything but the root
	if r.URL.Path != "/" {
		http.Redirect(w, r, "/", 303)
		return
	}

	// Read in the template with our SSE JavaScript code.
	t, err := template.ParseFiles("static/index.html")

	if err != nil {
		log.Fatal(err)
	}

	// Render the template, writing to `w`.
	t.Execute(w, nil)
}
