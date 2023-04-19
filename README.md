# Speedrun.com Dataset

![](https://www.speedrun.com/images/logo-white.png)

A dataset focused on user/game metadata and user behavioural data from [speedrun.com](https://www.speedrun.com).

## Contents

 * [Dataset Context](#context)
 * [Dataset Contents](#dataset-contents)
 * [Contact Me](#contact-me)
 * [FAQ](#frequently-asked-questions)
 * [References](#references)

## Dataset Context

This dataset contains metadata for both users and games, and user behaviour data for personal bests and individual runs. This data was collected in January to March 2023, and is designed to be cleaned so that January 1st 2023 is the maximum date.

This data was the foundation for my undergraduate thesis on investigating the communities of speedrun.com. 

Keywords: Speedrunning, Speedrun, Videogame, Videogames, Data science, Networks, Community Detection, Recommendation System, Recommendation Engine, Collaborative Filtering, Content Filtering, User Behaviour.

## Dataset Contents

The following is the layout of the `data/raw/` directory, and then a description of each of the files and directories:

```
raw/
├── games/
├── srcom_games_with_metadata.csv
├── srcom_user_runs.csv
├── srcom_users_with_metadata.csv
└── users/
```

[`srcom_games_with_metadata.csv`](data/raw/srcom_games_with_metadata.csv) - Contains metadata for every game on speedrun.com:
 * game\_id: The internal ID of each game. Information for each game can be found via the [games endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q).
 * game\_name: The name provided for each game. This is required by speedrun.com to be a valid game.
 * game\_developers: A comma-separated string of each developer of a game, this can also be None. Information for each developer can be found via the [developer endpoint](https://www.speedrun.com/api/v1/developers/xv6dvx62).
 * game\_release\_date: An ISO 8601 date. This is the release date of the game.
 * game\_created\_date: An ISO 8601 date and time. This is the date and time the game was added to speedrun.com.
 * game\_num\_categories: The number of categories for a game. The values of these can get retrieved via the [categories endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q/categories).
 * game\_num\_levels: The number of levels for a game. The values of these can be retrieved via the [levels endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q/levels).
 * game\_num\_runs: The number of runs for a game. These have been scraped from each pages' `webstats` page as listed in the games endpoint.
 * game\_num\_users: The number of users that have played a game. This has been calculated by iterating through the leaderboards from the [leaderboards endpoint](https://www.speedrun.com/api/v1/leaderboards/o1y9wo6q/category/wkpoo02r).
 * game\_num\_guests: The number of guests that have played a game. The num\_users and num\_guests are calculated using the same method.

[`srcom_users_with_metadata.csv`](data/raw/srcom_users_with_metadata.csv) - Contains metadata for every user that has contributed to the leaderboards of each game in the games metadata:
 * user\_id: The internal ID of each user. Information for each user can be found via the [users endpoint](https://www.speedrun.com/api/v1/runs?user=o86y93wj).
 * user\_signup\_date: An ISO 8601 date and time. This is the date and time the user signed up to speedrun.com
 * user\_location: The user-provided location on their profile. This is an ISO 3166 alpha-2 code for each country.
 * user\_num\_games: The number of games each user has played. This is collected by counting the number unique games a user has submitted a verified run for via the [runs endpoint](https://www.speedrun.com/api/v1/runs?user=o86y93wj&status=verified).
 * user\_games: A comma-separated string of each of the game IDs that a user has played.

[`srcom_user_runs.csv`](data/raw/srcom_user_runs.csv) - Contains the number of runs for most users in the user metadata file. This is separate as there is a different number of users in each file.
 * user\_id: The internal ID of each user. Information for each user can be found via the [users endpoint](https://www.speedrun.com/api/v1/runs?user=o86y93wj).
 * user\_num\_runs: The number of verified runs for each user. This is collected by counting the number of runs via the [runs endpoint](https://www.speedrun.com/api/v1/runs?user=o86y93wj&status=verified)

[`games/`](data/raw/games/) - The personal bests of each user that appears on any leaderboard of a given game. 
 * original\_game\_id: The internal ID of the game named in the file.
 * user\_id: The internal ID of the user on the leaderboard.
 * game\_id:  The internal ID of the other game the users have played.
 * category\_id: The internal ID of the category of the other game the user has played.
 * level\_id: The internal ID of the level of the other game the user has played.
 * position: The position in the leaderboard of the other game the user has played.

[`users/`](data/raw/users/) - The individual runs of each user that appears in the user metadata.
 * user: The internal ID of the user in the named file. Information can be found for each user via the [users endpoint](https://www.speedrun.com/api/v1/runs?user=o86y93wj).
 * game\_id: The internal game ID that a user has a verified run for. Information for each game can be found via the [games endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q).
 * category\_id: The internal category ID that a user has a verified run for. The values of these can get retrieved via the [categories endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q/categories).
 * level\_id: The internal level ID that a user has a verified run for. The values of these can be retrieved via the [levels endpoint](https://www.speedrun.com/api/v1/games/o1y9wo6q/levels).
 * time: An integer number of seconds. The overall time of the individual run.
 * date: An ISO 8601 date and time. The date and time that the run was submitted. 
 * emulated: Boolean value if the platform was emulated (true) or not (false).

## Contact Me

I will be submitting improvements and extra information to this dataset over time. If you have any questions, please create a GitHub Issue.

## Frequently Asked Questions:

 * How did you collect the data?

Using the collection system stored in `collector/`. This is written in Python and uses the requests\_cache and srcomapi packages to access the speedrun.com API efficiently.

 * How do I look at your analysis?

I'm flattered, honestly. All analysis is found under the `analysis/` directory, but requires `main.py` to be run first. To run the analysis without issues, you can try the following:

```bash
cd speedruncom-data
mkdir data/too_big/
python3 main.py
```

 * I've tried your analysis notebooks but there are missing files, what do I do?

There may be instances where generated files are too big to be stored on GitHub, and I'm lazy. There will be methods to generate these files, such as `main.py`.

## References

 * [Speedrun.com API Documentation](https://github.com/speedruncomorg)
 * [Srcomapi Package](https://github.com/blha303/srcomapi)
 * [Requests-cache Documentation](https://github.com/requests-cache/requests-cache)
 * [Graph-tool Documentation](https://graph-tool.skewed.de/static/doc/index.html)
 * [PecanPy Documentation](https://pecanpy.readthedocs.io/en/latest/)
 * [Sklearn Documentation](https://scikit-learn.org/stable/)
 * [Networkx Documentation](https://networkx.org/documentation/stable/index.html)
