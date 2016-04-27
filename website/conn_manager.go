package main

//
//
// Connections are maintained here, but the data sent out is not
//
//

import (
	"fmt"
	"net/http"
)

//a Connection Hub is responsible for which clients are connected to the server
//and who needs messages
type ConHub struct {

	//Create a map of clients, the keys of the map are the channels
	//over which we can push messages to attached clients.  (The values
	//are just booleans and are meaningless.)
	connections map[*connection]bool

	//A channel that is used to register new clients
	register chan *connection

	//a channel that is used to unregister old clients
	unregister chan *connection

	//a channel that is used to message that gets sent out to all the users
	broadcast chan pushMessage
}

//abstraction out the channel to a connection, this makes it easier to add parts
//laster and gets rid of (chan chan objects)
type connection struct {
	send chan pushMessage
}

//again, abstract out the string that usually goes in the channel above.
//this is very import because we can send an object which can have all
//sorts of fields, we will use this abstraction much more than the
//connection abstraction above
type pushMessage []byte

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

		//this waits for something to hit the notify channel, it waits here
		//until the connection closes and writes to the channel
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
		//the response supports streaming.
		f.Flush()
	}
}

//This ConHub method starts a new go-routine.  It handles
//the addition & removal of clients, as well as the broadcasting
//of messages out to clients that are currently attached.
func (hub *ConHub) run() {

	//Start a go-routine so that this run concurrently
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
					//the connection and delete the connection from the
					//connection list
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
					//log.Printf("Sent message to %d connections\n",
					//	len(hub.connections))
				}
			}
		}
	}()
}
