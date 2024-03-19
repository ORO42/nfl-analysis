# datasource: SportsOddsHistory.com

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import os
from datetime import datetime


# specify start season
season = 2021

driver = webdriver.Chrome()

# define header for CSV file
header = [
    "season",
    "season_week",
    "week_day",
    "month",
    "day",
    "year",
    "hour",
    "minute",
    "favorite",
    "favorite_score",
    "spread",
    "underdog",
    "underdog_score",
    "straight_winner",
    "winner_score",
    "straight_loser",
    "loser_score",
    "team_covered",
    "OU_text",
    "OU_value",
    "at",
    "is_OT",
    "straight_tie",
    "spread_tie",
]

table_loop_count = 0

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# open csv for writing
with open(f"nfl_odds_data_{current_datetime}.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(header)

    # loop through the number of desired seasons
    for _ in range(10):
        # get site
        driver.get(f"https://sportsoddshistory.com/nfl-game-season/?y={season}")
        time.sleep(2)

        tables = driver.find_elements(By.CLASS_NAME, "soh1")
        del tables[:2]

        print(f"=========={season}==========")

        for table in tables[:-1]:
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]

            for row in rows:
                items = row.find_elements(By.TAG_NAME, "td")

                week_day = items[0].text
                date = items[1].text.replace(",", "")
                month, day, year = date.split(" ")
                game_time = items[2].text
                hour, minute = map(int, game_time.split(":"))

                favorite = items[4].text
                spread_raw = items[6].text
                spread_split = spread_raw.split(" ")

                if spread_split[1] == "PK":
                    spread, favorite, underdog = "PK", "PK", "PK"
                else:
                    spread = float(spread_split[1])
                    underdog = items[8].text

                OU = items[9].text
                OU_text, OU_value = OU.split(" ")

                at = (
                    favorite
                    if items[3].text == "@"
                    else (underdog if items[7].text == "@" else "N")
                )

                b_test = items[4].find_elements(By.TAG_NAME, "b")
                team_covered = favorite if len(b_test) > 0 else underdog

                score = items[5].text
                is_OT = "OT" in score
                straight_tie = "P" in score

                score_split = score.split(" ")[1].split("-")
                favorite_score, underdog_score = int(score_split[0]), int(
                    score_split[1]
                )

                if favorite_score > underdog_score:
                    straight_winner, winner_score, straight_loser, loser_score = (
                        favorite,
                        favorite_score,
                        underdog,
                        underdog_score,
                    )
                elif underdog_score > favorite_score:
                    straight_winner, winner_score, straight_loser, loser_score = (
                        underdog,
                        underdog_score,
                        favorite,
                        favorite_score,
                    )
                else:
                    straight_tie = True

                spread_tie = spread != "PK" and abs(
                    favorite_score - underdog_score
                ) == abs(spread)

                line_to_write = [
                    season,
                    table_loop_count + 1,
                    week_day,
                    month,
                    day,
                    year,
                    hour,
                    minute,
                    favorite,
                    favorite_score,
                    spread,
                    underdog,
                    underdog_score,
                    straight_winner,
                    winner_score,
                    straight_loser,
                    loser_score,
                    team_covered,
                    OU_text,
                    OU_value,
                    at,
                    is_OT,
                    straight_tie,
                    spread_tie,
                ]
                writer.writerow(line_to_write)

            if table_loop_count < 17:
                table_loop_count += 1
            else:
                table_loop_count = 0

        table_loop_count = 0
        season -= 1
        time.sleep(8)

driver.quit()
