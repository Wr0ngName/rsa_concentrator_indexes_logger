# RSA Concentrator Indexes Logger
RSA Security Analytics - Concentrator Indexes Stats logger

Allows for a better understanding of the indexes for each meta parsed and stored:

Run on a concentrator you want to check the indexes (simply said, the amount of different values per meta).

A PERL script is already designed to output the different levels for each meta. It's the script we will use as an input.

The current Python script will get the output and build a database with the different values for the different meta. But on each executions following the building of the database, it will only rewrite the value if this one is higher than the previous one. And it will update the data and time of storage.

In conclusion, after a few hours running, you can easily see which indexes are full, or empty, and then adjust your configuration in consequence.

Here is how to use it:

./indexConcentratorLogger.py /root/index-concentrator.pl [refreshing delay in mins - default: 5] [max iterrations - default: 1440 (every mins = 5 days running)]

Requires Python 2.7 to run, tried to stay simple and native, in order to reduce the footprint on the concentrator.
