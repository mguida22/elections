package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/lib/pq"
	"log"
	"os"
	"strings"
)

type Tweet struct {
	Text string `json:"text"`
}

type Word struct {
	ID   string
	Text string
}

func main() {
	// open input file
	fi, err := os.Open("tweets.txt")
	if err != nil {
		panic(err)
	}
	// close fi on exit and check for its returned error
	defer func() {
		if err := fi.Close(); err != nil {
			panic(err)
		}
	}()
	// make a read buffer
	r := bufio.NewReader(fi)

	db, err := sql.Open("postgres", "user=Ben dbname=gosegment sslmode=disable")

	if err != nil {
		log.Println("1", err)
		return
	}

	defer db.Close()

	stmt, pErr := db.Prepare("INSERT INTO word_list(word) VALUES($1)")

	if pErr != nil {
		log.Println("2", pErr)
		return
	}

	defer stmt.Close()

	counter := 0

	for {
		fileLine, err := r.ReadString('\n')

		if err != nil {
			panic(err)
		}

		var newTweet Tweet

		jErr := json.Unmarshal([]byte(fileLine), &newTweet)

		if jErr != nil {
			log.Println("4", jErr)
			log.Println(fileLine)
		}

		score := 0
		wordList := []Word{}

		displayTweet(newTweet, &score)

		wordRange := strings.Split(newTweet.Text, " ")

		for _, single_space_word := range wordRange {

			single_space_word = strings.Trim(single_space_word, `!,.;:'"?-)([]{}…—“”`)

			secondRange := strings.Split(single_space_word, "\n")

			for _, singleWord := range secondRange {

				singleWord = strings.ToLower(strings.Trim(singleWord, `!,.;:'"?-)([]{}…—“”`))

				//make sure we are not adding nothing or a URL to the list
				if singleWord != "" && (len(singleWord) < 12 || singleWord[0:12] != "https://t.co") {

					_, sErr := stmt.Exec(singleWord)

					if sErr != nil && sErr.Error() != `pq: duplicate key value violates unique constraint "word_list_word_key"` {
						log.Println("5", sErr)
						break
					}

					newWord := Word{"", singleWord}

					db.QueryRow("SELECT id FROM word_list WHERE word=$1",
						singleWord).Scan(&newWord.ID)

					wordList = append(wordList, newWord)
				}
			}
		}

		stmt, pErr := db.Prepare(`INSERT INTO
                        word_relations(word_ids, score) VALUES($1, $2) ON
                        CONFLICT (word_ids) DO UPDATE SET score =
                        word_relations.score + $2`)

		if pErr != nil {
			log.Println("7", pErr)
			return
		}

		defer stmt.Close()

		wordStmt, spErr := db.Prepare(`INSERT INTO
                        word_score(id, score) VALUES($1, $2) ON
                        CONFLICT (id) DO UPDATE SET score =
                        word_score.score + $2`)

		if spErr != nil {
			log.Println("8", spErr)
		}

		defer wordStmt.Close()

		for i, iWord := range wordList {

			wordStmt.Exec(iWord.ID, score)

			for j, jWord := range wordList {

				if i != j {

					_, sErr := stmt.Exec((iWord.ID + "/" + jWord.ID), score)

					if sErr != nil {
						log.Panicln("8", sErr)
						return
					}
				}
			}
		}

		counter++

		if counter%1000 == 0 {
			var wordCount int
			QRerr := db.QueryRow("SELECT count(id) FROM word_list").Scan(&wordCount)

			if QRerr != nil {
				log.Println(QRerr)
				break
			}

			log.Println(counter, "tweets viewed &", wordCount, "words used.")
		}
	}
}

func displayTweet(tweet Tweet, score *int) {

	var input string
	validInput := false

	log.Println("\n----Rank the Tweet----")
	log.Println(tweet.Text)

	for !validInput {

		fmt.Print("----(p)ostive, (n)egative, (i)gnore----: ")
		fmt.Scanln(&input)

		if input == "p" {
			*score = 1
			validInput = true
		} else if input == "n" {
			*score = -1
			validInput = true
		} else if input == "i" {
			*score = 0
			validInput = true
		} else {

			log.Println("\nIncorrect input, please enter...")
		}
	}
}
