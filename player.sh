#!/bin/bash

QUEUE_FILENAME=~/bloodseeker/UrlsList.txt
CURRENT_TRACK_FILE=~/bloodseeker/CurrentTrack.txt
TMP_Q=/tmp/qnwoiqkpoudyiqwydiq

function pop(){
        url=$(head -n 1 $QUEUE_FILENAME)
        tail -n +2 $QUEUE_FILENAME > $TMP_Q && mv $TMP_Q $QUEUE_FILENAME
        echo "$url"
}

for (( ; ; ))
do
        url=$(pop)

	if [ -z "$url" ]; then
		# echo "Nothing popped, sleeping"
		rm -f $CURRENT_TRACK_FILE
		sleep 3
	else
		echo "Popped [$url], playing now"
		echo $url > $CURRENT_TRACK_FILE
		cvlc --no-video --play-and-exit "$url"
		#cvlc --no-video --play-and-exit vlc:quit "$url"
        	sleep 3
	fi
done
