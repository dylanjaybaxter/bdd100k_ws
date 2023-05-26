#!/bin/bash

# URL of the webpage
url="http://dl.yf.io/bdd100k/mot20/"

# Download function
download_file() {
    link=$1
    wget --quiet --continue "$link"
}

# Extract links from webpage and download files
links=$(curl -s "$url" | grep -o '<a [^>]*href="[^"]*"' | grep -o '".*"' | tr -d '"' | grep -v '/$')

for link in $links; do
    download_file "$url$link"
done
