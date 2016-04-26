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
	Positive float64
	Negative float64
}

func main() {

	//create a new consumer to look at the tweets
	consumer, err := sarama.NewConsumer([]string{"localhost:9092"}, nil)

	//if there is an error, end the program
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
	partitionConsumer, err := consumer.ConsumePartition("sentimentfeed", 0, sarama.OffsetNewest)

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

	//populate the map so that all candidate are always listed in the json
	candidateMap["berniesanders"] = &score{}
	candidateMap["donaldtrump"] = &score{}
	candidateMap["hillaryclinton"] = &score{}
	candidateMap["johnkasich"] = &score{}
	candidateMap["tedcruz"] = &score{}

	//count for amount of messages managed
	var messagesRead float64 = 0

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

					//find out if the message is positive or negative
					positive := false
					if newSentiment.Sentiment == "pos" {
						positive = true
					}

					//if the tweet is positive
					if positive {
						candidateMap[newSentiment.Candidate].Positive++

					} else {
						candidateMap[newSentiment.Candidate].Negative++
					}

					messagesRead++
				}

			//send messages out every two seconds
			case <-tick:
				{
					//if there are messages to to send the clients
					if messagesRead != 0 {

						//create a new map to send info to the client
						//this is because we are using a map to pointer
						//array to make things easier but this doesn't
						//work for json.Marshal
						fullArray := make(map[string]score)

						//for each item in the pointer array
						//move the items to the fullArray
						for key, value := range candidateMap {

							//divide the score by the total amount of tweets
							//this lets us get the relative score of each
							//person compared to each other
							fullArray[key] = score{(*value).Positive / messagesRead,
								(*value).Negative / messagesRead}
						}

						//parse the array into a byte json string
						jsonByte, err := json.Marshal(fullArray)

						if err != nil {
							log.Panicln(err)
						}

						//send the message to the all the clients
						hub.broadcast <- jsonByte

						log.Println(messagesRead, "messages read")

						//reset the message count
						messagesRead = 0

						//delete everything in the pointer map
						//this should help keep things small
						for key := range candidateMap {
							candidateMap[key].Negative = 0
							candidateMap[key].Positive = 0
						}
					}
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
