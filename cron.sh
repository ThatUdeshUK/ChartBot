echo "Starting"

source venv/bin/activate

python --version

python crawlers/youtube.py -a AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA data
python crawlers/lastfm.py -a 196e42e2e2c1a028450f5426a88a7fb4 data

python reducers/lastfm_youtube.py data

python downloaders/downloader.py -a AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA data

echo "Done!"

deactivate
