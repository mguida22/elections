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
				}

			case msg := <-hub.broadcast:
				{
					//for every connection that is active
					for c := range hub.connections {

						//if there is something to send
						//send it
						c.send <- msg
					}
					log.Printf("Sent message to %d connections\n",
						len(hub.connections))
				}
			}
		}
	}()
}

//This Connection Hub method handles and HTTP request at the "/events/" URL.
func (hub *ConHub) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	//Make sure that the writer supports flushing.
	f, ok := w.(http.Flusher)

	if !ok {
		http.Error(w, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	//Set the headers related to event streaming.
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	//create a new connection and register the chan
	newConnection := &connection{}
	newConnection.send = make(chan pushMessage)

	//register the connection so that we send messages to it
	hub.register <- newConnection

	//Listen to the closing of the http connection via the CloseNotifier
	notify := w.(http.CloseNotifier).CloseNotify()

	//defer the function for when the connection closes
	go func() {
		<-notify
		hub.unregister <- newConnection
	}()

	//for every message
	for {

		//get the message
		msg, open := <-newConnection.send

		//break once the connection is closed
		if !open {
			break
		}

		// Write to the ResponseWriter, `w`.
		fmt.Fprintf(w, "data:%s\n\n", msg)

		//Flush the response.  This is only possible if
		//the repsonse supports streaming.
		f.Flush()
	}
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

func main() {

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
	//is called in a separate goroutine for each
	//request to "/events/".
	http.Handle("/events/", hub)

	//create a new push object for us to push into
	//we will get rid of this once we get everything together
	newPush := pushMessage{}

	//generate a fake function that sends the time to the user every second
	//again we will get rid of this once we get storm working
	go func() {
		for i := 0; ; i++ {

			//create the message to send to the user
			newPush.main = fmt.Sprintf("%d - the time is %v", i, time.Now())

			//send the message
			hub.broadcast <- newPush

			//wait a second
			time.Sleep(time.Second)
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
