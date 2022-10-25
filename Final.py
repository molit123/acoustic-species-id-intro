from random import sample
import pandas as pd
import numpy as np
import csv

# Returns the hour at which the clip was recorded
def getTime(string):
    return string[11:13]

def stratifiedRS(csv_path, numClips):
    # Read CSV into a DataFrame
    audio_df = pd.read_csv(csv_path)

    # Filter clips to only those that are a minute or longer
    success_recordings = audio_df[(audio_df.get('Duration') >= 60)]

    # Count the number of successful clips per AudioMoth device
    count_clips_df = success_recordings.groupby('AudioMothCode').count()

    # Find the value of the minimum number of clips (this is the value of AM-8 since it has an issue with the number of clips)
    minimum_clips = count_clips_df.loc['AM-8'].get('AudioMothID')

    # Filter the DataFrame to get only the AudioMoths that are greater than the minimum value (this is the first strata layer)
    first_strata = count_clips_df[count_clips_df.get('AudioMothID') > minimum_clips]
    first_strata_audiomoths = first_strata.index.values.tolist()
  
    # AudioMoths with a valid number of clips ranging the entire day
    valid_audiomoths = []

    # Create and open CSV in write mode, and write the header row first
    file = open('sampled.csv', 'w')
    writer = csv.writer(file)
    writer.writerow(audio_df)

    # Iterate through each valid AudioMoth from the first strata
    for am in first_strata_audiomoths:
        # Get only the clips from the valid AudioMoths
        filtered_am = success_recordings[success_recordings.get('AudioMothCode') == am]

        # Create a new DataFrame with a new column for the hour of day that the clip was recorded
        by_date = filtered_am.assign(
                Hour=filtered_am.get('StartDateTime').apply(getTime)
            )

        # Group by the hour so we can check how many clips there are per hour
        total_day_clips = by_date.groupby('Hour').count()

        # Check that the AudioMoth has a clip for each hour of the day
        if (len(total_day_clips) == 24):
            valid_audiomoths.append(am)

        # Iterate through each hour of the day
        for hour in range(0,24):        
            # Convert the hour to comparable and valid string object
            if (hour < 10):
                str_hour = '0' + str(hour)
            else:
                str_hour = str(hour)

            # Filter the clips of this valid AudioMoth by the current hour
            to_sample = by_date[(by_date.get('Hour') == str_hour)]

            # Draw a random sample of 1 clip from the clips of the current hour
            sampled_clip = to_sample.sample(1)

            # Write the sampled random clip to the CSV file
            writer.writerow(sampled_clip.iloc[0])

    file.close()