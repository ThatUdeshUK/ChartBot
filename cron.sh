echo "Starting"

source venv/bin/activate

python --version

#python crawlers/youtube.py -y AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA data
#python crawlers/lastfm.py -l 196e42e2e2c1a028450f5426a88a7fb4 data
#python crawlers/at40.py -l 196e42e2e2c1a028450f5426a88a7fb4 data
#python crawlers/uk40.py -l 196e42e2e2c1a028450f5426a88a7fb4 data

python reducers/reducer.py -y AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA data
python reducers/selector.py data

python downloaders/downloader.py -y AIzaSyApZSllh8X0aggJ_qyXliX2yDiQU_9fgeA data
python downloaders/finalizer.py data

echo "Done!"

deactivate
