rm kube.log.temp
mv kuber.log kuber.log.temp
rm kuber.log
pgrep python | xargs kill -9
pgrep kubectl | xargs kill -9
pgrep sh | xargs kill -9
