#!/bin/bash
export PYTHONPATH="/home/jazzms/.venv/lib/python3.12/site-packages:/home/jazzms:$PYTHONPATH"
sudo ntpdate -s time.nist.gov
# Function to print colored and bold text
print_bold_red() {
    echo -e "\e[1;31m$1\e[0m"  # Bold red text
}

print_bold_green() {
    echo -e "\e[1;32m$1\e[0m"  # Bold green text
}


# Start Celery worker in the background if $CELERY is set to 1
if [ "$CELERY" = "1" ]; then
#   poetry run celery -A app.src.ms.tasks beat --loglevel=info &

  print_bold_green "CELERY WORKERS ARE ON"
#    poetry run celery -A app.ext.syncer.background.tasks worker -l info -E -Q workers_q -c 1 --prefetch-multiplier=1 &

else
   # Print message indicating Celery workers are off in bold red color
   print_bold_red "CELERY WORKERS ARE OFF" &
fi




echo "START CRON"

sudo cron -f &

echo "START APP"
#Start BOTS
#python3 /home/jazzms/app/src/bot.py &
# Start MAIN
python3 -u /home/jazzms/app/src/main.py

