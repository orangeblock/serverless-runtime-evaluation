package main

import ("net/http")

func Handler(w http.ResponseWriter, r *http.Request) {
    msg := "{\"status\": 200}"
    w.Write([]byte(msg))
}
