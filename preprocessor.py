import re
import pandas as pd
from textblob import TextBlob


def preprocess(data):
    pattern1 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM|am|pm)'
    pattern2 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'


    messages = re.split(pattern1, data)[1:]
    dates = re.findall(pattern1, data)
    date_format = '%m/%d/%y, %I:%M %p'


    # If pattern1 fails, try pattern2
    if not messages or not dates:
        messages = re.split(pattern2, data)[1:]
        dates = re.findall(pattern2, data)
        date_format = '%d/%m/%Y, %I:%M %p'


    # If both patterns fail, return an error message
    if not messages or not dates:
        print("The data format is not correct. Please check the input data.")
        return None


    df = pd.DataFrame({'user_message': messages, 'message_date': dates})


    # Try parsing dates with the initially chosen format
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format=date_format)
    except ValueError:
        # If the first format fails, try alternative formats
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')
        except ValueError:
            try:
                df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p')
            except ValueError:
                print("Failed to parse dates. Please check the input data format.")
                return None


    df.rename(columns={'message_date': 'date'}, inplace=True)


    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])


    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)


    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute


    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))


    df['period'] = period
    # Sentiment Analysis
    sentiments = []
    for message in df['message']:
        blob = TextBlob(message)
        sentiment = blob.sentiment
        sentiments.append(sentiment.polarity)  # Consider using sentiment.subjectivity for subjectivity analysis


    df['sentiment'] = sentiments


    return df


# Paths to the WhatsApp chat files
file_paths = [
    r"/mnt/data/WhatsApp Chat with KES With Anudip (Placement Training).txt",
    r"/mnt/data/WhatsApp Chat with We move world- Tech ONLY.txt"
]


for file_path in file_paths:
    try:
        # Read the file with proper encoding handling
        with open(file_path, "rb") as file:
            bytes_data = file.read()


        # Decode the bytes data, ignoring errors
        data = bytes_data.decode("utf-8", errors="ignore")


        # Preprocess the data
        df = preprocess(data)
        if df is not None:
            print(f"Processed data from file: {file_path}")
            print(df.head())
            user_list = df['user'].unique().tolist()
            print("Unique users:", user_list)
        else:
            print(f"Data preprocessing failed for file: {file_path}. Please check the input data format.")


    except FileNotFoundError as e:
        print(f"Error: {e}. Please check the file path and ensure the file exists.")
    except Exception as e:
        print(f"An error occurred: {e}")





