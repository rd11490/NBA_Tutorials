import pandas as pd
import math

# Adjust pandas settings to show more columns when printing dataframe
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Read the csv file into a dataframe
shots = pd.read_csv("shots.csv")

# Print the first 10 rows
#print(shots.head(10))

# Take only the necessary columns
shots = shots[["playerId", "teamId", "teamName", "xCoordinate", "yCoordinate", "shotAttemptedFlag", "shotMadeFlag", "shotZoneBasic"]]

# Print the first 10 rows
#print(shots.head(10))

# Calculate shot zone based on co-ordinates:
# We will divide the shots into 4 zones, Restricted Area (<4ft), Paint, Mid-Range, 3Pt Shot
# We will determine the bin of the shot based on the x,y coordinates of the shot


# We need to convert the distance provided to real units. In the case of the shots we are using here the conversion is
# 1 to 18/15 (inches)
def convert_shot_to_real(x):
    return (x / 7.5) * 9

# Calculate the distance from the hoop. In our shot coordinate system, the hoop is at 0,0.
#  We just need to take sqrt(x^2 + y^2) convert it to real units and then divide by 12 to go from inches to feet.
def calculate_distance(x, y):
    return convert_shot_to_real(math.hypot(x, y))/12.0

# The Restricted area has a radius of 4ft from the center of the hoop
def is_restricted(x, y):
    return calculate_distance(x, y) <= 4

# The paint is 16 ft by 19 ft
def is_paint(x, y):
    return -80 < x < 80 and -47.5 < y < 142.5

# 3s are 22 ft in the corners so you can check if x is out side of 22 feet
# 3s are 23.75 ft above the break, so distance can be checked for above the break 3s
def is_three(x, y):
    return x < -220 or x > 220 or calculate_distance(x, y) > 23.75

# A function that takes in a dataframe row, extracts the x and y coordinates and returns the shot bin
def determine_shot_bin(row):
    x = row["xCoordinate"]
    y = row["yCoordinate"]
    if is_restricted(x, y):
        return "Restricted"
    elif is_paint(x, y):
        return "Paint"
    elif is_three(x, y):
        return "3 Pt"
    else:
        return "Mid Range"


# add a column to the shots dataframe where the value is the result of applying determine_shot_bin to the row
shots["zone"] = shots.apply(determine_shot_bin, axis=1)

# print the first 10 results
#print(shots.head(10))



# Aggregate the shots

# A function to aggregate the raw shots to statistics about the group
def reduce_shot_group(group):
    total_shots = group["shotAttemptedFlag"].sum() # Calculate the number of attempted shots
    made_shots = group["shotMadeFlag"].sum() # Calculate the number of made shots
    percentage = round(made_shots/total_shots, 3) # Calculate the field goal percentage (round to 3 decimal places)

    return pd.Series([made_shots, total_shots, percentage]) # Return a row representing these aggregations


# A Function to calculate the shot frequency from each zone by dividing the number of shots in each zone by
# the total number of shots the team has taken
def calculate_shot_frequency(group):
    group["frequency"] = round(group["attempted"] / group["attempted"].sum(),3)
    return group


# Take all of our raw shots and group them by the team who took the shot and the zone the shot was taken from
# then apply our reduce shot groups function to each of the resulting shots.
# We need to reset the index on the dataframe when we are finished to convert the result back to a standard dataframe
aggregated_shots = shots.groupby(by=["teamName","zone"]).apply(reduce_shot_group).reset_index()

# The result of our reduce shot groups function does not give our columns names so we need to provide them
aggregated_shots.columns = ["teamName","zone", "made", "attempted", "fg%"]

# Take our resulting aggregated shots and group by the team that took the shot. Then apply our calculate frequency
# function to the group and once again reset the index
aggregated_shots=aggregated_shots.groupby(by="teamName").apply(calculate_shot_frequency).reset_index()

# Print our results
print(aggregated_shots.head(10))