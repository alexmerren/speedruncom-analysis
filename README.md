# Final Project Data Collection & Data Analysis

This repository is the centre of the data collection and data analysis for the
final project of my undergraduate degree. My aim of this repository is to
encapsulate the logic for data collection and analysis. I will be getting the
data from [speedrun.com](https://www.speedrun.com) and analysing it using
machine learning techniques. Specifically, I will be using network machine
learning algorithms such as Deepwalk and Node2Vec. Furthermore, I may use
clustering and regerssion techniques to complete further analysis.

## How does this work?

This repository is split into four logical directories:
* [Data](/data) - The repository of all the formatted data that I have collected.
* [Analysing](/notebook) - A repository for the Jupyter Notebooks or other analysis programs.
* [Data Collector](/collector) - Code using srcomapi for requests, and custom formatting into the data repository.
* [Data Collector v2](/collectorv2) - My attempt at making a custom collector. Work in progress.
* [Speedrun.com API Module](/srcomapi) - A wrapper for the speedrun.com API created by [blha303](https://github.com/blha303).
* [Request Caching Module](/requests_cache) - A request cache module created by [requests-cache](https://github.com/requests-cache).

## Usage

It's probably best to use your own scripts that wrap the srcomapi package, but
the [data](/data) may be useful.

## Thanks

A big thank you to [blha303](https://github.com/blha303) for creating the
[srcomapi repository](https://github.com/blha303/srcomapi). It has saved me
countless hours creating my own wrapper for the API, you have my thanks!

## References

 * [Srcomapi repository](https://github.com/blha303/srcomapi)
 * [Speedrun.com API reference](https://github.com/speedruncomorg)
 * [Request-cache repository](https://github.com/requests-cache/requests-cache)
