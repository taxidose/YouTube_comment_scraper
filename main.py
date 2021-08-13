from secret import API_KEY
from googleapiclient.discovery import build
import pandas as pd
import datetime

comment_counter = 0

VIDEO_ID = "X3EHnj5YtFU"


def request_comments(video_id=None, page_token=None):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    if video_id is None:
        video_id = VIDEO_ID

    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token
        )

        return request.execute()

    except Exception:
        print("Couldn't request video")
        main()


def update_df(api_response_data, df=None):
    # comments_datetimes = [comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
    #                       for comment in api_response_data["items"]]
    # comments_text = [comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    #                  for comment in api_response_data["items"]]
    #
    # authors_names = [comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
    #                  for comment in api_response_data["items"]]
    # authors_channel_ids = [comment["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
    #                        for comment in api_response_data["items"]]
    #
    # new_df = pd.DataFrame(list(zip(comments_datetimes, comments_text, authors_names, authors_channel_ids)),
    #                       columns=["Datetime", "Comment", "Authorname", "Author-ID"])

    comments_text = []
    datetimes = []
    author_names = []
    author_ids = []

    for item in api_response_data["items"]:
        global comment_counter
        comment_counter += 1

        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments_text.append(comment)
        datetime = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
        datetimes.append(datetime)
        author_name = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
        author_names.append(author_name)
        author_id = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
        author_ids.append(author_id)
        # print(f"{comment=}, {datetime=}, {author_name=}")

    new_df = pd.DataFrame(list(zip(datetimes, comments_text, author_names, author_ids)),
                          columns=["Datetime", "Comment", "Authorname", "Author-ID"])

    if df is None:
        return new_df

    return df.append(new_df, ignore_index=True)


def main():
    print(f"--------------------\nYT Comment Scraper\n(Only top-level comments get scraped.)\n--------------------")
    video_id = input("Enter video-id: ")

    response = request_comments(video_id)
    print("page 1 read...")

    df = update_df(response)
    print("df initialized...  ")

    page_counter = 1

    while True:
        page_counter += 1
        try:
            response = request_comments(page_token=response["nextPageToken"])
            df = update_df(response, df)
            print(f"commentpage {page_counter} read... df updated...")
        except Exception as e:
            print("end rechead...")
            break

    date = datetime.datetime.now()
    today = date.strftime("%y%m%d")

    filename = f"{video_id}_{today}.csv"
    df.to_csv(filename, index=False)

    print(f"\n{filename}.csv file created... finished... ({comment_counter} toplevel comments)")

    # for comment in response["items"]:
    #     print(comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"])

    choice = input("\nScrape another video? ")
    choice = choice.lower()
    if choice in ["yes", "y", "ja", "j"]:
        main()


if __name__ == '__main__':
    main()
