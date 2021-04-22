# mogi-bot
api check nutidy

docker build -t mogi-bot .

docker run -itd --name mogi-bot -v $PWD:/app -p 8000:8000 -e API_KEY=api_key  mogi-bot
