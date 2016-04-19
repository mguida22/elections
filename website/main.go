package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"
)

//a Connection Hub is responsable for which clients are connected to the server
//and who needs messages
type ConHub struct {

	//Create a map of clients, the keys of the map are the channels
	//over which we can push messages to attached clients.  (The values
	//are just booleans and are meaningless.)
	connections map[*connection]bool

	//Register new clients
	register chan *connection

	//Unregister all old clients
	unregister chan *connection

	//message that gets sent out to all the users
	broadcast chan pushMessage
}

//abrastion out the chan to a connection, this makes it easier to add parts
//laster and gets rid of (chan chan objects)
type connection struct {
	send chan pushMessage
}

//again, abstract out the string that usally goes in the chanel above.
//this is very import because we can send an object which can have all
//sorts of fields, we will use this abstraction much more than the
//connection abstraction above
type pushMessage struct {
	main string
}

//This ConHub method starts a new goroutine.  It handles
//the addition & removal of clients, as well as the broadcasting
//of messages out to clients that are currently attached.
func (hub *ConHub) run() {

	//Start a goroutine so that this run concrently
	go func() {

		//Loop endlessly
		for {

			//Block until we receive from one of the
			//three following channels.
			select {

			case c := <-hub.register:
				{
					//There is a new client attached and we
					//want to start sending them messages.
					hub.connections[c] = true

					log.Println("opened")
				}

			case c := <-hub.unregister:
				{
					//if the connection is over, we need to close
					//the conenction and delte the conection from the
					//conection list
					if _, ok := hub.connections[c]; ok {
						delete(hub.connections, c)
						close(c.send)
					}

					log.Println("closed")
				}

			case msg := <-hub.broadcast:
				{
					// There is a new message to send.  For each
					// attached client, push the new message
					// into the client's message channel.
					for c := range hub.connections {

						//if there is something to send
						//send it
						c.send <- msg

						log.Println("sent")
					}
				}
			}
		}
	}()
}

// This Connection Hub method handles and HTTP request at the "/events/" URL.
func (hub *ConHub) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	// Make sure that the writer supports flushing.
	f, ok := w.(http.Flusher)

	if !ok {
		http.Error(w, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	// Set the headers related to event streaming.
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// Create a new channel, over which the broker can
	// send this client messages.
	newConnection := &connection{}

	// Add this client to the map of those that should
	// receive updates
	hub.register <- newConnection

	// Listen to the closing of the http connection via the CloseNotifier
	notify := w.(http.CloseNotifier).CloseNotify()

	go func() {
		<-notify
		hub.unregister <- newConnection
	}()

	for {

		msg, open := <-newConnection.send

		if !open {
			break
		}

		// Write to the ResponseWriter, `w`.
		fmt.Fprintf(w, "%s\n\n", msg)

		// Flush the response.  This is only possible if
		// the repsonse supports streaming.
		f.Flush()

	}

	log.Println("finished")
}

// Handler for the main page, which we wire up to the
// route at "/" below in `main`.
func MainPageHandler(w http.ResponseWriter, r *http.Request) {

	// Did you know Golang's ServeMux matches only the
	// prefix of the request URL?  It's true.  Here we
	// insist the path is just "/".
	if r.URL.Path != "/" {

		fs := http.FileServer(http.Dir("static"))
		http.Handle("/static/", http.StripPrefix("/static/", fs))
		return
	}

	// Read in the template with our SSE JavaScript code.
	t, err := template.ParseFiles("static/index.html")
	if err != nil {
		log.Fatal(err)

	}

	// Render the template, writing to `w`.
	t.Execute(w, "Duder")

	// Done.
	log.Println("Finished HTTP request at ", r.URL.Path)
}

// Main routine
//
func main() {

	// Make a new Connection Hub instance
	hub := &ConHub{
		broadcast:   make(chan pushMessage),
		register:    make(chan *connection),
		unregister:  make(chan *connection),
		connections: make(map[*connection]bool),
	}

	// Start processing events
	hub.run()

	// Make b the HTTP handler for "/events/".  It can do
	// this because it has a ServeHTTP method.  That method
	// is called in a separate goroutine for each
	// request to "/events/".
	http.Handle("/events/", hub)

	// Generate a constant stream of events that get pushed
	// into the Broker's messages channel and are then broadcast
	// out to any clients that are attached.

	newPush := pushMessage{}

	go func() {
		for i := 0; ; i++ {

			// Create a little message to send to clients,
			// including the current time.
			newPush.main = fmt.Sprintf("%d - the time is %v", i, time.Now())
			hub.broadcast <- newPush

			time.Sleep(5 * 1e9)

			log.Println("he")

		}
	}()

	// When we get a request at "/", call `MainPageHandler`
	// in a new goroutine.
	http.HandleFunc("/", MainPageHandler)

	// Start the server and listen forever on port 8000.
	http.ListenAndServe(":8000", nil)
}
