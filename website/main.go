package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"
)

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
