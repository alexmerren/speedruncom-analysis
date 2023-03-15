# Analysing the Communities of Speedrun.com

![](https://www.speedrun.com/images/logo-white.png)

This repository contains all the information related to the final project of my undergraduate degree. 

This repository is comprised of three main parts: data collection, data analysis, and the data itself. These are logically separated into the directories [collection](collector/), [analysis](analysis/), and [data](data/) respectively.

The data can be found in the [data](data/) directory. In this, we can find the [games metadata](data/games/metadata/), the [other games users play](data/games/network/), and the [world record history](data/games/world_record_history/) for each game. Some functions will need a directory called `data/too_big/`. These files are too big to be uploaded to GitHub, and need to be re-generated each time.

## Contents

 * [Documentation](#documentation)
 * [Internal References](#internal-references)
 * [External References](#external-references)

## Documentation

All functions within the analysis and collector directories are documented. I'm still researching on how I can publish this documentation easily.

## Internal References

There are three main analysis files:

 * [Network Analysis](analysis/notebooks/Network_Analysis.ipynb)
 * [Exploratory Analysis](analysis/notebooks/Exploratory_Analysis.ipynb)
 * [User Preference Generator](analysis/user_preference_generator.py)

## External References

 * [Speedrun.com API Documentation](https://github.com/speedruncomorg)
 * [Srcomapi Package](https://github.com/blha303/srcomapi)
 * [Requests-cache Documentation](https://github.com/requests-cache/requests-cache)
 * [Graph-tool Documentation](https://graph-tool.skewed.de/static/doc/index.html)
 * [PecanPy Documentation](https://pecanpy.readthedocs.io/en/latest/)
 * [Sklearn Documentation](https://scikit-learn.org/stable/)
 * [Networkx Documentation](https://networkx.org/documentation/stable/index.html)
