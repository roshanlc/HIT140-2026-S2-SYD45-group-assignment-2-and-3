# Task 1 – Argentina's Attackinng Performance of Forwards vs Midfielders 

## Overview

This project analyses whether there was a significant difference in attacking performance between Argentina's forwards and midfielders at the **2026 FIFA World Cup**. Player statistics were obtained from **FBref** and processed using Python.

## Method

Attacking performance was measured using **G+A/90 (Goal Contributions per 90 minutes)**. The final dataset contained **13 eligible players: 5 forwards and 8 midfielders**. Descriptive statistics, 95% confidence intervals, and a **Welch two-sample t-test** were used.

## Results

Forwards had a higher mean G+A/90 (**1.558**) than midfielders (**0.308**). However, the Welch t-test produced **t = 1.358** and **p = 0.2418**. Since p > 0.05, the null hypothesis was not rejected, meaning there was **insufficient evidence of a statistically significant difference** between the two groups.

