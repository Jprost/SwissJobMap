while true; 
do
	HOUR="$(($(date +'%-H') % 3))"
	if [ $HOUR -eq 0 ]; then
		echo Scrapping ...		
		python3 scrap.py
		git pull
		git add ../Data/df_jobs_content.p ../Data/df_jobs.p
		currentDate=
		git commit -m "$(date +'%a-%d-%b %Hh')"
		git push

		sleep 1h
	else
		echo Sleeping ...
		sleep 30m
	fi
done