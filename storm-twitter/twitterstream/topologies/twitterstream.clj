(ns twitterstream
  (:use     [streamparse.specs])
  (:gen-class))

(defn twitterstream [options]
   [
    ;; spout configuration
    {"word-spout" (python-spout-spec
          options
          "spouts.readtweets.TweetSpout"
          ["tweet"]
          :p 1
          )
    }

    ;; bolt configuration
   
    {"storeDB-bolt" (python-bolt-spec
          options
          {"word-spout" :shuffle}
          "bolts.saveDB.DatabaseBolt"
          ["tweet"]
          :p 1
          )
    

    "count-bolt" (python-bolt-spec
          options
          {"word-spout" :shuffle}
          "bolts.tweetprocessor.TweetProcessor"
          ["tweet"]
          :p 1
          )
    }
  ]
)
