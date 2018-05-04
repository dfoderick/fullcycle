//go script for automating full cycle build. listens for changes on github and pushes docker image to docker hub
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
	"reflect"
	"os"
	"os/exec"
	"bufio"
)

type Author struct {
	Name string
	Email string
	Date time.Time
}

type CommitThing struct {
	Sha string
	Commit struct {
		Author Author
		Message string
	}
}

func printstruct(t CommitThing) {
	s := reflect.ValueOf(&t).Elem()
	typeOfT := s.Type()
	for i := 0; i < s.NumField(); i++ {
    		f := s.Field(i)
    		fmt.Printf("\n%d: %s %s = %v\n", i,
        		typeOfT.Field(i).Name, f.Type(), f.Interface())
	}
}

func runbuild() {
	cmd := exec.Command("/bin/sh","fcmbuildweb")
	cmdReader, err := cmd.StdoutPipe()

	if err != nil {
		fmt.Fprintln(os.Stderr, "Error creating StdoutPipe for Cmd", err)
		os.Exit(1)
	}

	scanner := bufio.NewScanner(cmdReader)
	go func() {
		for scanner.Scan() {
			fmt.Printf("build out | %s\n", scanner.Text())
		}
	}()

	err = cmd.Start()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error starting Cmd", err)
		os.Exit(1)
	}

	err = cmd.Wait()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error waiting for Cmd", err)
		os.Exit(1)
	}
}

func main() {
	var lastcommit time.Time
	var lastfound time.Time
	lastcommit = time.Now()
	lastfound = lastcommit

	url := "https://api.github.com/repos/dfoderick/fullcyclereact/commits"

	for {
		githubClient := http.Client{
			Timeout: time.Second * 5, // Maximum of 2 secs
		}

		req, err := http.NewRequest(http.MethodGet, url, nil)
		if err != nil {
			log.Fatal(err)
		}

		req.Header.Set("User-Agent", "fullcycle")

		res, getErr := githubClient.Do(req)
		if getErr != nil {
			log.Fatal(getErr)
		}

		body, readErr := ioutil.ReadAll(res.Body)
		if readErr != nil {
			log.Fatal(readErr)
		}

		var commits []CommitThing
		jsonErr := json.Unmarshal(body, &commits)
		if jsonErr != nil {
			log.Fatal(jsonErr)
		}

		//printstruct(commits[0])
		lastfound = commits[0].Commit.Author.Date
		fmt.Println("Last Check  =" + lastfound.Format(time.RFC3339))
		fmt.Println("Last Commit = " + lastcommit.Format(time.RFC3339))

		if lastfound.After(lastcommit) {
			runbuild()
			lastcommit = lastfound
		}

		time.Sleep(1 * 20 * 1000 * time.Millisecond)
	}
}

